# Prompt de continuação da fundação do Koquetel

Copie integralmente o bloco abaixo para o agente de IA na outra IDE.

---

Você está assumindo o trabalho de fundação do projeto **Koquetel**. Trabalhe no
repositório clonado, preserve todo o histórico existente e leia integralmente,
antes de qualquer ação:

1. `AGENTS.md`;
2. `docs/FOUNDATION-GOVERNANCE.md`;
3. `FOUNDATION-READINESS-REPORT.md`;
4. `docs/00-vision/VISION.md`;
5. `docs/01-product/PRD.md` e `ACCEPTANCE-CRITERIA.md`;
6. `docs/adr/ADR-0001-INDEPENDENT-CORE.md`;
7. `docs/KNOWN-GAPS.md`, `OPEN-QUESTIONS.md`, `ASSUMPTIONS.md` e `WORKLOG.md`.

## Estado e limite obrigatório

O projeto está em fase de fundação documental e classificado como **NOT READY —
FOUNDATION IN PROGRESS**. Não existe `APPROVED_TO_IMPLEMENT`. Portanto:

- NÃO escreva código de produção;
- NÃO crie instaladores, serviços, pacotes ou artefatos de release;
- NÃO altere o host;
- NÃO crie o marcador `APPROVED_TO_IMPLEMENT`;
- NÃO declare prontidão por quantidade de documentos;
- NÃO copie código de projetos pesquisados.

Sua missão é tornar a fundação decision-complete, verificável e pronta para uma
revisão independente futura.

## Invariante confirmado pelo proprietário

Koquetel deve construir, testar, instalar, operar, atualizar, reparar, recuperar,
exportar e desinstalar sem depender de SteamZero ou PhaseZero. Ambos são fontes
históricas de pesquisa somente.

É proibido introduzir nos artefatos padrão:

- imports, pacotes, submódulos ou downloads desses projetos;
- comandos, serviços, ownership markers ou caminhos exigidos deles;
- leitura do estado vivo ou dos formatos internos deles;
- degradação de capacidade quando seus repositórios não existem.

Uma futura migração do PhaseZero, se mantida, deve ser ferramenta offline,
separada, opcional e removível. Após importar um snapshot, o Koquetel deve operar
sem o importador e sem o snapshot. Preserve P-13, NFR-13, AC-17 e IT-01..IT-08.

## Método obrigatório

1. Explore antes de perguntar. Resolva fatos pelo repositório e por fontes
   oficiais pinadas.
2. Use somente fontes primárias para decisões técnicas: especificações, código e
   documentação oficial.
3. Registre toda afirmação sobre implementação com repositório, commit, arquivo,
   linhas e comportamento observado.
4. Trate repositórios pesquisados como somente leitura e verifique `git status`
   antes/depois.
5. Mantenha IDs estáveis. Nunca renumere identificadores publicados.
6. Toda obrigação normativa nova deve mapear requisito → ameaça/modo de falha →
   aceitação → teste → evidência.
7. Decisões do proprietário ficam em `OPEN-QUESTIONS.md`; não as feche por
   preferência do agente.
8. Registre premissas, lacunas e trabalho executado nos arquivos de honestidade.
9. Quando documentos conflitarem, siga a precedência da governança e corrija
   todas as referências afetadas.
10. Faça commits pequenos, temáticos e auditáveis; nunca inclua segredos ou
    artefatos gerados acidentalmente.

## Próxima frente prioritária

Execute nesta ordem:

### F1 — Schemas normativos

Defina schemas versionados, com exemplos válidos/inválidos e compatibilidade, para:

- plano e confirmação vinculada ao hash;
- transação, journal, recuperação e ownership;
- perfil/capability probe e adapter descriptor;
- memória, proveniência, conflito, retenção e exportação;
- tool manifest, capability request e policy decision;
- delegação de agente, orçamento e task checkpoint;
- eventos/auditoria e support bundle;
- model route, usage, cost e outcome.

Não invente campos sem necessidade concreta. Cada campo sensível deve indicar
classificação, retenção e permissão de exportação.

### F2 — Auditorias externas equivalentes

Para qualquer projeto que possa virar dependência ou base de adapter — começando
por ai-memory, RTK, MCP, LiteLLM, OpenHands, Letta e Mem0 — fixe commit/release e
licença, inventarie artefatos, leia 2–4 arquivos estruturais integralmente e
registre padrões positivos, falhas e anti-requisitos com linhas exatas.

Não atribua score com base em README. Atualize matrizes somente após evidência de
implementação.

### F3 — Contratos de protótipos

Especifique, sem implementar produto, os gates mensuráveis para cinco protótipos
descartáveis:

1. lock realmente exclusivo sob concorrência;
2. recuperação de journal com última gravação truncada;
3. ai-memory: concorrência, corrupção, exportação e remoção;
4. sandbox rootless: mounts, rede, recursos, segredos e desempenho;
5. distribuição Rust: binário, SQLite, Unix socket e recuperação após kill.

Cada gate deve definir ambiente, entrada, falha injetada, resultado esperado,
artefato de evidência, critério passa/falha e descarte do protótipo.

### F4 — Rastreabilidade e revisão

- Expanda `docs/TRACEABILITY.md` para uma linha por requisito.
- Garanta testes específicos para cada SR crítico e cada mutação.
- Adicione lint documental para IDs duplicados, referências quebradas, requisitos
  sem teste e decisões aceitas ainda listadas como abertas.
- Atualize o relatório de prontidão honestamente; mantenha `NOT READY` enquanto
  qualquer bloqueador crítico permanecer.

## Entrega esperada desta sessão

Entregue:

- resumo executivo das alterações;
- tabela arquivo → IDs alterados → evidência;
- comandos de validação e resultados;
- decisões ainda exigidas do proprietário;
- lacunas novas ou fechadas;
- confirmação de que nenhum código de produção/host foi alterado;
- confirmação de que SteamZero e PhaseZero continuaram somente leitura e não foram
  introduzidos como dependências.

Não implemente o produto e não solicite aprovação de implementação até todos os
critérios de `docs/FOUNDATION-GOVERNANCE.md §5` estarem comprovados.

---

