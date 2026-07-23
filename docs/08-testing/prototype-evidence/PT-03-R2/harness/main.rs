// PT-03 disposable harness (NON-PRODUCTION). Every store mutation and query
// uses ai-memory-store's public API at the externally pinned source checkout.
use ai_memory_core::{NewPage, PagePath, ProjectId, Tier, WorkspaceId};
use ai_memory_store::Store;
use anyhow::{Context, Result, anyhow};
use serde::{Deserialize, Serialize};
use serde_json::json;
use sha2::{Digest, Sha256};
use std::io::Write;
use std::path::{Path, PathBuf};
use std::time::Duration;

#[derive(Debug, Clone, Serialize, Deserialize)]
struct LedgerRow {
    process: usize,
    sequence: usize,
    path: String,
    body_sha256: String,
    status: String,
    retry_count: usize,
}

fn body_for(path: &str) -> String {
    format!("synthetic-ai-memory-body:{path}")
}

fn digest(text: &str) -> String {
    format!("{:x}", Sha256::digest(text.as_bytes()))
}

fn page(ws: WorkspaceId, project: ProjectId, path: String) -> Result<NewPage> {
    Ok(NewPage {
        workspace_id: ws,
        project_id: project,
        path: PagePath::new(path.clone())?,
        title: format!("Synthetic {path}"),
        body: body_for(&path),
        tier: Tier::Semantic,
        frontmatter_json: json!({"kind":"note","synthetic":true}),
        pinned: false,
        links: Vec::new(),
        author_id: None,
    })
}

async fn scope(store: &Store, project_name: &str) -> Result<(WorkspaceId, ProjectId)> {
    let ws = store.writer.get_or_create_workspace("pt03-r2").await?;
    let project = store.writer.get_or_create_project(ws, project_name, None).await?;
    Ok((ws, project))
}

fn open_with_retry(data: &Path) -> Result<(Store, usize)> {
    for retry in 0..=100usize {
        match Store::open(data) {
            Ok(store) => return Ok((store, retry)),
            Err(error) if retry < 100
                && (error.to_string().contains("locked")
                    || error.to_string().contains("busy")) =>
            {
                std::thread::sleep(Duration::from_millis(25));
            }
            Err(error) => return Err(error.into()),
        }
    }
    unreachable!()
}

async fn scope_with_retry(store: &Store, project_name: &str)
    -> Result<((WorkspaceId, ProjectId), usize)>
{
    for retry in 0..=100usize {
        match scope(store, project_name).await {
            Ok(ids) => return Ok((ids, retry)),
            Err(error) if retry < 100
                && (error.to_string().contains("locked")
                    || error.to_string().contains("busy")) =>
            {
                tokio::time::sleep(Duration::from_millis(25)).await;
            }
            Err(error) => return Err(error),
        }
    }
    unreachable!()
}

async fn upsert_with_retry(store: &Store, input: NewPage) -> Result<usize> {
    for retry in 0..=100usize {
        match store.writer.upsert_page(input.clone()).await {
            Ok(_) => return Ok(retry),
            Err(error) if retry < 100
                && (error.to_string().contains("locked")
                    || error.to_string().contains("busy")) =>
            {
                tokio::time::sleep(Duration::from_millis(10)).await;
            }
            Err(error) => return Err(error.into()),
        }
    }
    unreachable!()
}

fn write_ledger(path: &Path, rows: &[LedgerRow]) -> Result<()> {
    let mut output = std::fs::File::create(path)?;
    for row in rows {
        serde_json::to_writer(&mut output, row)?;
        output.write_all(b"\n")?;
        output.flush()?;
    }
    Ok(())
}

async fn seed(data: &Path, project_name: &str, prefix: &str, count: usize) -> Result<()> {
    let store = Store::open(data)?;
    let (ws, project) = scope(&store, project_name).await?;
    for sequence in 0..count {
        let path = format!("{prefix}/{sequence:05}.md");
        store.writer.upsert_page(page(ws, project, path)?).await?;
    }
    Ok(())
}

async fn worker(data: &Path, project_name: &str, process: usize, count: usize,
                ledger: &Path, marker: Option<&Path>) -> Result<()> {
    let (store, open_retries) = open_with_retry(data)?;
    let ((ws, project), scope_retries) = scope_with_retry(&store, project_name).await?;
    eprintln!("process={process} open_retries={open_retries} scope_retries={scope_retries}");
    if let Ok(ready) = std::env::var("PT03_READY_FILE") {
        std::fs::write(ready, format!("process={process}\n"))?;
    }
    if let Ok(start) = std::env::var("PT03_START_FILE") {
        while !Path::new(&start).exists() {
            std::thread::sleep(Duration::from_millis(5));
        }
    }
    let mut output = std::fs::File::create(ledger)?;
    for sequence in 0..count {
        let path = format!("p{process:02}/{sequence:05}.md");
        let retry_count = upsert_with_retry(&store, page(ws, project, path.clone())?).await?;
        let row = LedgerRow {
            process,
            sequence,
            body_sha256: digest(&body_for(&path)),
            path,
            status: "committed".into(),
            retry_count,
        };
        serde_json::to_writer(&mut output, &row)?;
        output.write_all(b"\n")?;
        output.flush()?;
        if sequence == 99 {
            if let Some(marker) = marker {
                std::fs::write(marker, format!("pid={}\n", std::process::id()))?;
                std::thread::sleep(Duration::from_secs(5));
            }
        }
    }
    Ok(())
}

async fn in_process(data: &Path, ledger: &Path) -> Result<()> {
    let store = Store::open(data)?;
    let (ws, project) = scope(&store, "in-process").await?;
    let mut tasks = Vec::new();
    for process in 0..8usize {
        let writer = store.writer.clone();
        tasks.push(tokio::spawn(async move {
            let mut rows = Vec::new();
            for sequence in 0..1250usize {
                let path = format!("p{process:02}/{sequence:05}.md");
                writer.upsert_page(page(ws, project, path.clone())?).await?;
                rows.push(LedgerRow {
                    process,
                    sequence,
                    body_sha256: digest(&body_for(&path)),
                    path,
                    status: "committed".into(),
                    retry_count: 0,
                });
            }
            Ok::<_, anyhow::Error>(rows)
        }));
    }
    let mut rows = Vec::new();
    for task in tasks {
        rows.extend(task.await??);
    }
    rows.sort_by_key(|row| (row.process, row.sequence));
    write_ledger(ledger, &rows)
}

fn read_ledger(path: &Path) -> Result<Vec<LedgerRow>> {
    std::fs::read_to_string(path)?
        .lines()
        .map(|line| Ok(serde_json::from_str(line)?))
        .collect()
}

async fn verify(data: &Path, project_name: &str, ledger: &Path, report: &Path) -> Result<()> {
    let store = Store::open(data)?;
    let (ws, project) = scope(&store, project_name).await?;
    let rows = read_ledger(ledger)?;
    let mut missing = 0usize;
    let mut wrong_digest = 0usize;
    for row in &rows {
        match store.reader.page_body_by_ids(ws, project, &row.path).await? {
            None => missing += 1,
            Some(body) if digest(&body.body) != row.body_sha256 => wrong_digest += 1,
            Some(_) => {}
        }
    }
    let pages = store.reader.recent_pages_for_project(ws, project, rows.len() + 10).await?;
    let result = json!({
        "ledgerRows": rows.len(),
        "queryablePages": pages.len(),
        "missing": missing,
        "wrongDigest": wrong_digest,
        "pass": missing == 0 && wrong_digest == 0 && pages.len() == rows.len()
    });
    std::fs::write(report, serde_json::to_vec_pretty(&result)?)?;
    println!("{result}");
    Ok(())
}

async fn export_scope(data: &Path, project_name: &str, envelope: &Path,
                      records: &Path) -> Result<()> {
    let store = Store::open(data)?;
    let (ws, project) = scope(&store, project_name).await?;
    let mut hits = store.reader.recent_pages_for_project(ws, project, 100_000).await?;
    hits.sort_by(|left, right| left.path.as_str().cmp(right.path.as_str()));
    let mut record_bytes = Vec::new();
    for hit in hits {
        let stored = store.reader.page_body_by_ids(ws, project, hit.path.as_str()).await?
            .ok_or_else(|| anyhow!("page disappeared during export"))?;
        let record = json!({
            "path": hit.path.as_str(),
            "title": stored.title,
            "body": stored.body,
            "tier": stored.tier,
            "pinned": stored.pinned,
            "frontmatter": serde_json::from_str::<serde_json::Value>(&stored.frontmatter_json)?
        });
        serde_json::to_writer(&mut record_bytes, &record)?;
        record_bytes.push(b'\n');
    }
    let integrity = format!("{:x}", Sha256::digest(&record_bytes));
    std::fs::write(records, &record_bytes)?;
    let created = std::process::Command::new("date")
        .args(["-u", "+%Y-%m-%dT%H:%M:%SZ"]).output()?;
    let envelope_doc = json!({
        "schemaVersion": 1,
        "exportId": "01J8Z0CNFHQH7VK3M2P9XR4T5N",
        "createdAt": String::from_utf8(created.stdout)?.trim(),
        "exportFormatVersion": 1,
        "scope": "project",
        "selectedKinds": ["semantic"],
        "recordCount": record_bytes.iter().filter(|byte| **byte == b'\n').count(),
        "includedContent": true,
        "backendOmissions": [],
        "integrityDigest": integrity
    });
    std::fs::write(envelope, serde_json::to_vec_pretty(&envelope_doc)?)?;
    Ok(())
}

async fn import_scope(data: &Path, project_name: &str, envelope: &Path,
                      records: &Path) -> Result<()> {
    let envelope_doc: serde_json::Value = serde_json::from_slice(&std::fs::read(envelope)?)?;
    if envelope_doc["schemaVersion"] != 1 || envelope_doc["scope"] != "project" {
        return Err(anyhow!("unsupported SCH-10 envelope"));
    }
    let bytes = std::fs::read(records)?;
    if format!("{:x}", Sha256::digest(&bytes)) != envelope_doc["integrityDigest"] {
        return Err(anyhow!("SCH-10 integrity digest mismatch"));
    }
    let lines: Vec<&str> = std::str::from_utf8(&bytes)?.lines().collect();
    if lines.len() as u64 != envelope_doc["recordCount"].as_u64().unwrap_or(u64::MAX) {
        return Err(anyhow!("SCH-10 record count mismatch"));
    }
    let store = Store::open(data)?;
    let (ws, project) = scope(&store, project_name).await?;
    for line in lines {
        let record: serde_json::Value = serde_json::from_str(line)?;
        let path = record["path"].as_str().context("record.path")?.to_owned();
        let imported = NewPage {
            workspace_id: ws,
            project_id: project,
            path: PagePath::new(path)?,
            title: record["title"].as_str().context("record.title")?.to_owned(),
            body: record["body"].as_str().context("record.body")?.to_owned(),
            tier: Tier::Semantic,
            frontmatter_json: record["frontmatter"].clone(),
            pinned: record["pinned"].as_bool().unwrap_or(false),
            links: Vec::new(),
            author_id: None,
        };
        store.writer.upsert_page(imported).await?;
    }
    Ok(())
}

async fn purge(data: &Path, project_name: &str, report: &Path) -> Result<()> {
    let store = Store::open(data)?;
    let (ws, project) = scope(&store, project_name).await?;
    let summary = store.writer.purge_project(ws, project, "pt03-r2/export", None).await?;
    let queryable = store.reader.recent_pages_for_project(ws, project, 100_000).await?.len();
    let mut files = Vec::new();
    for entry in walk(data)? {
        let metadata = std::fs::metadata(&entry)?;
        files.push(json!({
            "path": entry.strip_prefix(data)?.to_string_lossy(),
            "kind": if metadata.is_dir() {"directory"} else {"file"},
            "bytes": if metadata.is_file() {metadata.len()} else {0}
        }));
    }
    let result = json!({
        "purgeSummary": {
            "label": summary.label,
            "pagePaths": summary.page_paths,
            "pagesDeleted": summary.pages_deleted,
            "sessionsDeleted": summary.sessions_deleted,
            "observationsDeleted": summary.observations_deleted,
            "handoffsDeleted": summary.handoffs_deleted,
            "embeddingsDeleted": summary.embeddings_deleted
        },
        "queryableResidue": queryable,
        "physicalInventory": files,
        "categoriesInventoried": ["DB","WAL","SHM","exports","temp files","backups","indices"],
        "note": "DB/WAL/SHM and internal indices are shared backend files; the governed export remains external physical residue and is reported, not silently deleted."
    });
    std::fs::write(report, serde_json::to_vec_pretty(&result)?)?;
    Ok(())
}

fn walk(root: &Path) -> Result<Vec<PathBuf>> {
    fn visit(path: &Path, output: &mut Vec<PathBuf>) -> Result<()> {
        for entry in std::fs::read_dir(path)? {
            let path = entry?.path();
            output.push(path.clone());
            if path.is_dir() { visit(&path, output)?; }
        }
        Ok(())
    }
    let mut output = Vec::new();
    visit(root, &mut output)?;
    output.sort();
    Ok(output)
}

async fn probe(data: &Path) -> Result<()> {
    match Store::open(data) {
        Err(error) => {
            println!("{}", json!({"status":"FAIL_CLOSED","stage":"open","error":error.to_string()}));
            Ok(())
        }
        Ok(store) => match store.reader.recent_pages(10).await {
            Err(error) => {
                println!("{}", json!({"status":"FAIL_CLOSED","stage":"read","error":error.to_string()}));
                Ok(())
            }
            Ok(pages) => {
                println!("{}", json!({"status":"SILENT_OPEN","queryablePages":pages.len()}));
                Err(anyhow!("corrupted store opened without error"))
            }
        }
    }
}

async fn probe_path(data: &Path, project_name: &str, path: &str) -> Result<()> {
    match Store::open(data) {
        Err(error) => {
            println!("{}", json!({"status":"FAIL_CLOSED","stage":"open","error":error.to_string()}));
            Ok(())
        }
        Ok(store) => {
            let ids = scope(&store, project_name).await;
            match ids {
                Err(error) => {
                    println!("{}", json!({"status":"FAIL_CLOSED","stage":"scope","error":error.to_string()}));
                    Ok(())
                }
                Ok((ws, project)) => match store.reader.page_body_by_ids(ws, project, path).await {
                    Err(error) => {
                        println!("{}", json!({"status":"FAIL_CLOSED","stage":"read","error":error.to_string()}));
                        Ok(())
                    }
                    Ok(Some(_)) => {
                        println!("{}", json!({"status":"SILENT_OPEN","path":path,"result":"present"}));
                        Err(anyhow!("corrupted WAL path read without error"))
                    }
                    Ok(None) => {
                        println!("{}", json!({"status":"SILENT_WRONG","path":path,"result":"missing"}));
                        Err(anyhow!("corrupted WAL was silently discarded"))
                    }
                }
            }
        }
    }
}

async fn wal_holder(data: &Path, marker: &Path) -> Result<()> {
    let store = Store::open(data)?;
    let (ws, project) = scope(&store, "wal-fault").await?;
    for sequence in 0..500usize {
        let path = format!("wal/{sequence:05}.md");
        store.writer.upsert_page(page(ws, project, path)?).await?;
    }
    let wal = PathBuf::from(format!("{}-wal", store.db_path().display()));
    std::fs::write(marker, format!("pid={}\nwal={}\n", std::process::id(), wal.display()))?;
    loop { tokio::time::sleep(Duration::from_secs(60)).await; }
}

#[tokio::main]
async fn main() -> Result<()> {
    let args: Vec<String> = std::env::args().collect();
    match args.get(1).map(String::as_str) {
        Some("seed") => seed(Path::new(&args[2]), &args[3], &args[4], args[5].parse()?).await,
        Some("worker") => worker(
            Path::new(&args[2]), &args[3], args[4].parse()?, args[5].parse()?,
            Path::new(&args[6]), args.get(7).map(|value| Path::new(value)),
        ).await,
        Some("in-process") => in_process(Path::new(&args[2]), Path::new(&args[3])).await,
        Some("verify") => verify(
            Path::new(&args[2]), &args[3], Path::new(&args[4]), Path::new(&args[5])
        ).await,
        Some("export") => export_scope(
            Path::new(&args[2]), &args[3], Path::new(&args[4]), Path::new(&args[5])
        ).await,
        Some("import") => import_scope(
            Path::new(&args[2]), &args[3], Path::new(&args[4]), Path::new(&args[5])
        ).await,
        Some("purge") => purge(Path::new(&args[2]), &args[3], Path::new(&args[4])).await,
        Some("probe") => probe(Path::new(&args[2])).await,
        Some("probe-path") => probe_path(Path::new(&args[2]), &args[3], &args[4]).await,
        Some("wal-holder") => wal_holder(Path::new(&args[2]), Path::new(&args[3])).await,
        _ => Err(anyhow!("unknown mode")),
    }
}
