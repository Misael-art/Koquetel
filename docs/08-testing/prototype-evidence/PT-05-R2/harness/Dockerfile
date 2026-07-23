FROM ubuntu:24.04
COPY pt05_core_r2 /usr/local/bin/pt05_core_r2
COPY container-run.sh /usr/local/bin/container-run.sh
RUN chmod 0755 /usr/local/bin/pt05_core_r2 /usr/local/bin/container-run.sh \
    && groupadd --gid 1001 owner \
    && useradd --uid 1001 --gid 1001 --no-create-home owner \
    && groupadd --gid 1002 outsider \
    && useradd --uid 1002 --gid 1002 --no-create-home outsider
ENTRYPOINT ["/usr/local/bin/container-run.sh"]
