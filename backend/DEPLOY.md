# Deploy to Google Cloud Run

Target setup: container on Cloud Run, database on managed Postgres (Neon or
Supabase) reached over TCP+TLS, secrets in Secret Manager, and schema migrations
run as a one-off Cloud Run Job.

The app reads `DATABASE_URL` and normalizes it automatically: a pasted
`postgresql://...?sslmode=require` is coerced to the `asyncpg` driver, the
libpq-only params (`sslmode`, `channel_binding`) are stripped, and TLS is enabled
via connect-args. So you can paste the provider URL as-is.

## 0. Prerequisites

- `gcloud` CLI installed and authenticated: `gcloud auth login`
- A GCP project with billing enabled
- A Postgres database (Neon or Supabase) and its connection string

Set shell variables (run everything from the `backend/` directory):

```bash
export PROJECT_ID=your-gcp-project
export REGION=us-central1
export REPO=backend
export SERVICE=backend
export TAG=v1
export IMAGE="$REGION-docker.pkg.dev/$PROJECT_ID/$REPO/backend:$TAG"

gcloud config set project "$PROJECT_ID"
```

## 1. Get your database URL

- Neon: copy the POOLED connection string (host contains `-pooler`).
  Looks like `postgresql://user:pass@ep-xxx-pooler.region.aws.neon.tech/neondb?sslmode=require`.
- Supabase: for the running service use the connection pooler (Transaction mode,
  port 6543), host `aws-0-REGION.pooler.supabase.com`, user `postgres.PROJECTREF`.
  For migrations prefer the direct/session connection (port 5432), since the
  transaction pooler can interfere with some DDL.

The app already sets `statement_cache_size=0`, so transaction poolers (pgbouncer)
are safe.

## 2. Enable APIs and create the image repository

```bash
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  secretmanager.googleapis.com

gcloud artifacts repositories create "$REPO" \
  --repository-format=docker \
  --location="$REGION" \
  --description="Backend images"
```

## 3. Create secrets

```bash
# Database URL (paste your Neon/Supabase string). printf avoids a trailing newline.
printf '%s' 'postgresql://USER:PASSWORD@HOST/DB?sslmode=require' \
  | gcloud secrets create DATABASE_URL --data-file=-

# JWT signing key (32+ random bytes)
printf '%s' "$(openssl rand -hex 32)" \
  | gcloud secrets create JWT_SECRET_KEY --data-file=-
```

Grant the Cloud Run runtime service account read access to both secrets
(default runtime SA is the Compute default account):

```bash
PROJECT_NUMBER=$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)')
RUNTIME_SA="$PROJECT_NUMBER-compute@developer.gserviceaccount.com"

for S in DATABASE_URL JWT_SECRET_KEY; do
  gcloud secrets add-iam-policy-binding "$S" \
    --member="serviceAccount:$RUNTIME_SA" \
    --role=roles/secretmanager.secretAccessor
done
```

## 4. Build and push the image

Cloud Build builds the Dockerfile and pushes to Artifact Registry:

```bash
gcloud builds submit --tag "$IMAGE" .
```

## 5. Run migrations (one-off Cloud Run Job)

The job runs `alembic upgrade head` using the same image. Run it before deploying
a revision that depends on the new schema.

```bash
gcloud run jobs deploy backend-migrate \
  --image "$IMAGE" \
  --region "$REGION" \
  --command alembic \
  --args upgrade,head \
  --set-secrets DATABASE_URL=DATABASE_URL:latest \
  --set-env-vars ENV=prod \
  --max-retries 1 \
  --task-timeout 600

gcloud run jobs execute backend-migrate --region "$REGION" --wait
```

(If Supabase, point the job at the direct/session URL instead of the pooler:
add `--set-secrets DATABASE_URL=DATABASE_URL_DIRECT:latest` after creating that
secret.)

## 6. Deploy the service

```bash
gcloud run deploy "$SERVICE" \
  --image "$IMAGE" \
  --region "$REGION" \
  --allow-unauthenticated \
  --port 8080 \
  --cpu 1 --memory 512Mi \
  --min-instances 0 --max-instances 5 \
  --set-env-vars "ENV=prod,CORS_ORIGINS_STR=https://your-frontend.example" \
  --set-secrets "DATABASE_URL=DATABASE_URL:latest,JWT_SECRET_KEY=JWT_SECRET_KEY:latest"
```

Notes:
- `--port 8080` matches the container, which binds `$PORT` (Cloud Run injects
  `PORT=8080`).
- `CORS_ORIGINS_STR` is comma-separated; leave unset/empty to allow all (`*`).
- `WEB_CONCURRENCY` (gunicorn workers, default 2) can be set via `--set-env-vars`.
- Set `--min-instances 1` to avoid cold starts (higher cost).

## 7. Verify

```bash
URL=$(gcloud run services describe "$SERVICE" --region "$REGION" --format='value(status.url)')
curl -s "$URL/health"
curl -s -o /dev/null -w '%{http_code}\n' "$URL/docs"   # OpenAPI UI
echo "MCP endpoint: $URL/mcp"
```

Smoke test the API:

```bash
curl -s "$URL/api/v1/users/register" -H 'content-type: application/json' \
  -d '{"email":"a@b.com","password":"Password1","full_name":"A B"}'

TOKEN=$(curl -s "$URL/api/v1/users/login" -H 'content-type: application/json' \
  -d '{"email":"a@b.com","password":"Password1"}' \
  | python -c 'import sys,json;print(json.load(sys.stdin)["access_token"])')

curl -s "$URL/api/v1/users/me" -H "authorization: Bearer $TOKEN"
```

## 8. Redeploy / update flow

```bash
export TAG=v2
export IMAGE="$REGION-docker.pkg.dev/$PROJECT_ID/$REPO/backend:$TAG"

gcloud builds submit --tag "$IMAGE" .

# Only if you added a new migration:
gcloud run jobs update backend-migrate --image "$IMAGE" --region "$REGION"
gcloud run jobs execute backend-migrate --region "$REGION" --wait

gcloud run deploy "$SERVICE" --image "$IMAGE" --region "$REGION"
```

Rotate a secret and roll it out:

```bash
printf '%s' "$(openssl rand -hex 32)" \
  | gcloud secrets versions add JWT_SECRET_KEY --data-file=-
gcloud run services update "$SERVICE" --region "$REGION" \
  --set-secrets "JWT_SECRET_KEY=JWT_SECRET_KEY:latest"
```

## Troubleshooting

- Container fails to start / "failed to listen on PORT": confirm gunicorn binds
  `$PORT` (it does in the Dockerfile) and the deploy uses `--port 8080`.
- DB connection errors: check the secret value, that the provider allows external
  connections, and that the URL uses `sslmode=require` for Neon/Supabase.
- `prepared statement ... already exists`: you are on a transaction pooler without
  `statement_cache_size=0`; this app sets it, so verify you did not override the
  connection args.
- Secret access denied: confirm the IAM binding in step 3 for the runtime SA.
