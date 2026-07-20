Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Write-Host "Starting the complete local College ERP stack without deleting Docker volumes..."
docker compose config | Out-Null
docker compose up --build -d

Write-Host "Local ERP: http://localhost:8080"
Write-Host "API docs:  http://localhost:8000/docs"
Write-Host "Ready:     http://localhost:8000/health/ready"
