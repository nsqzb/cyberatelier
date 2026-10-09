FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    ATELIER_HOST=0.0.0.0 \
    ATELIER_PORT=8080 \
    WORKSPACES_DIR=/workspaces \
    DATA_DIR=/data \
    LAB_PORT=8000

RUN apt-get update \
    && apt-get install -y --no-install-recommends git bash openssh-client ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --system --gid 10001 atelier \
    && useradd --system --uid 10001 --gid atelier --home-dir /home/atelier \
       --create-home --shell /bin/bash atelier \
    && mkdir -p /app /workspaces /data \
    && chown -R atelier:atelier /workspaces /data /home/atelier \
    && chmod 0755 /app /workspaces /data

WORKDIR /app

# Application files are installed as root and remain read-only to the service.
COPY --chown=root:root . /app
RUN find /app -type d -exec chmod 0555 {} + \
    && find /app -type f -exec chmod 0444 {} +

USER atelier:atelier
EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/api/health', timeout=2).read()"]

CMD ["python", "server.py"]
