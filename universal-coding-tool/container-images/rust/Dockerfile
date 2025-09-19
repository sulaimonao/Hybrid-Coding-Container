FROM rust:1.80-slim

ENV CARGO_HOME=/home/sandbox/.cargo \
    RUSTUP_HOME=/home/sandbox/.rustup \
    PATH="/home/sandbox/.cargo/bin:$PATH"

RUN apt-get update \
    && apt-get install -y --no-install-recommends pkg-config libssl-dev clang tini \
    && rm -rf /var/lib/apt/lists/*

COPY entrypoint.sh /usr/local/bin/uct-entrypoint
RUN chmod +x /usr/local/bin/uct-entrypoint

WORKDIR /work

ENTRYPOINT ["/usr/local/bin/uct-entrypoint"]
