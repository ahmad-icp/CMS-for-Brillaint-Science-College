Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if (-not (Test-Path ".env.production")) {
  throw ".env.production is required. Copy .env.production.example, fill real secrets, and keep it private."
}

$envText = Get-Content ".env.production" -Raw
if ($envText -match "replace-with|change-me|placeholder") {
  throw ".env.production still contains placeholder values."
}

docker compose --env-file .env.production -f docker-compose.production.yml config | Out-Null
docker compose --env-file .env.production -f docker-compose.production.yml build backend celery-worker celery-beat frontend migrate
docker compose --env-file .env.production -f docker-compose.production.yml up -d postgres redis

Write-Host "Waiting for PostgreSQL and Redis health checks..."
docker compose --env-file .env.production -f docker-compose.production.yml up --wait postgres redis

Write-Host "Stopping old application processes before migrations..."
docker compose --env-file .env.production -f docker-compose.production.yml stop backend celery-worker celery-beat backup frontend

Write-Host "Running one-time migration..."
docker compose --env-file .env.production -f docker-compose.production.yml run --rm migrate

Write-Host "Starting application services..."
docker compose --env-file .env.production -f docker-compose.production.yml up -d backend celery-worker celery-beat backup frontend
Write-Host "Production stack started. Database volumes were not deleted."
