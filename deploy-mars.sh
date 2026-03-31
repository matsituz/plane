#!/bin/bash
set -euo pipefail

# Deploy Plane with Mars ID SSO to core.marsit.uz
# Usage: ssh mars@core.marsit.uz 'bash -s' < deploy-mars.sh

PLANE_DIR="$HOME/plane"
REPO_URL="git@github.com:matsituz/plane.git"
BRANCH="preview"

echo "=== Plane + Mars ID deployment ==="

# 1. Clone or update repo
if [ -d "$PLANE_DIR/repo" ]; then
    echo "[1/5] Updating repo..."
    cd "$PLANE_DIR/repo"
    git fetch origin "$BRANCH"
    git reset --hard "origin/$BRANCH"
else
    echo "[1/5] Cloning repo..."
    mkdir -p "$PLANE_DIR"
    git clone --depth=1 --branch "$BRANCH" "$REPO_URL" "$PLANE_DIR/repo"
fi

# 2. Build custom backend image
echo "[2/5] Building plane-backend with Mars ID auth..."
cd "$PLANE_DIR/repo"
docker build \
    -t marsit/plane-backend:latest \
    -f apps/api/Dockerfile.api \
    apps/api/

# 3. Copy deployment files
echo "[3/5] Setting up deployment..."
mkdir -p "$PLANE_DIR/deploy"
cp deployments/cli/community/docker-compose.yml "$PLANE_DIR/deploy/"

# 4. Create env file if not exists
if [ ! -f "$PLANE_DIR/deploy/plane.env" ]; then
    echo "[4/5] Creating plane.env (EDIT THIS!)..."
    cat > "$PLANE_DIR/deploy/plane.env" << 'ENVEOF'
APP_DOMAIN=plane.marshub.uz
APP_RELEASE=stable

WEB_REPLICAS=1
SPACE_REPLICAS=1
ADMIN_REPLICAS=1
API_REPLICAS=1
WORKER_REPLICAS=1
BEAT_WORKER_REPLICAS=1
LIVE_REPLICAS=1

# Ports — don't conflict with host Caddy
LISTEN_HTTP_PORT=3080
LISTEN_HTTPS_PORT=3443
SITE_ADDRESS=:80

WEB_URL=https://plane.marshub.uz
DEBUG=0
CORS_ALLOWED_ORIGINS=https://plane.marshub.uz
API_BASE_URL=http://api:8000

# DB
PGHOST=plane-db
PGDATABASE=plane
POSTGRES_USER=plane
POSTGRES_PASSWORD=CHANGE_ME_DB_PASSWORD
POSTGRES_DB=plane
POSTGRES_PORT=5432
PGDATA=/var/lib/postgresql/data
DATABASE_URL=

# Redis
REDIS_HOST=plane-redis
REDIS_PORT=6379
REDIS_URL=

# RabbitMQ
RABBITMQ_HOST=plane-mq
RABBITMQ_PORT=5672
RABBITMQ_USER=plane
RABBITMQ_PASSWORD=CHANGE_ME_MQ_PASSWORD
RABBITMQ_VHOST=plane
AMQP_URL=

# No cert — host Caddy handles TLS
CERT_EMAIL=
CERT_ACME_CA=
CERT_ACME_DNS=
TRUSTED_PROXIES=0.0.0.0/0

# Secret
SECRET_KEY=CHANGE_ME_SECRET_KEY

# Storage
USE_MINIO=1
AWS_REGION=
AWS_ACCESS_KEY_ID=CHANGE_ME_MINIO_ACCESS
AWS_SECRET_ACCESS_KEY=CHANGE_ME_MINIO_SECRET
AWS_S3_ENDPOINT_URL=http://plane-minio:9000
AWS_S3_BUCKET_NAME=uploads
FILE_SIZE_LIMIT=5242880
MINIO_ENDPOINT_SSL=0

GUNICORN_WORKERS=1
API_KEY_RATE_LIMIT=60/minute
LIVE_SERVER_SECRET_KEY=CHANGE_ME_LIVE_SECRET

# === MARS ID SSO ===
MARS_ID_SECRET=CHANGE_ME_MARS_ID_JWT_SECRET
ENVEOF
    echo "  >>> EDIT $PLANE_DIR/deploy/plane.env before starting! <<<"
else
    echo "[4/5] plane.env exists, skipping..."
fi

# 5. Create override to use custom backend image
cat > "$PLANE_DIR/deploy/docker-compose.override.yml" << 'EOF'
services:
  api:
    image: marsit/plane-backend:latest
    environment:
      MARS_ID_SECRET: ${MARS_ID_SECRET:-}
  worker:
    image: marsit/plane-backend:latest
    environment:
      MARS_ID_SECRET: ${MARS_ID_SECRET:-}
  beat-worker:
    image: marsit/plane-backend:latest
    environment:
      MARS_ID_SECRET: ${MARS_ID_SECRET:-}
  migrator:
    image: marsit/plane-backend:latest
    environment:
      MARS_ID_SECRET: ${MARS_ID_SECRET:-}
EOF

echo ""
echo "=== Done! ==="
echo ""
echo "Next steps:"
echo "  1. Edit secrets in: $PLANE_DIR/deploy/plane.env"
echo "  2. Add to Caddyfile:"
echo "     plane.marshub.uz {"
echo "         reverse_proxy localhost:3080"
echo "     }"
echo "  3. Start Plane:"
echo "     cd $PLANE_DIR/deploy"
echo "     docker compose --env-file plane.env up -d"
echo ""
