FROM python:3.11-slim

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/home/sandbox/.local/bin:$PATH"

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential curl git tini \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uv pipx

COPY entrypoint.sh /usr/local/bin/uct-entrypoint
RUN chmod +x /usr/local/bin/uct-entrypoint

WORKDIR /work

ENTRYPOINT ["/usr/local/bin/uct-entrypoint"]
