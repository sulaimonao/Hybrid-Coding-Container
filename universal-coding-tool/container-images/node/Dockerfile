FROM node:20-slim

ENV NODE_ENV=production \
    PATH="/home/sandbox/.local/bin:$PATH"

RUN apt-get update \
    && apt-get install -y --no-install-recommends git build-essential python3 tini \
    && rm -rf /var/lib/apt/lists/*

COPY entrypoint.sh /usr/local/bin/uct-entrypoint
RUN chmod +x /usr/local/bin/uct-entrypoint

WORKDIR /work

ENTRYPOINT ["/usr/local/bin/uct-entrypoint"]
