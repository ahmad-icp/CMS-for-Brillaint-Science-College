# College ERP Platform (CEP)

College ERP Platform is planned as an enterprise-grade, multi-tenant ERP for colleges and schools. The platform is designed so each institution can configure branding, academics, fees, grading, calendars, and workflows without changing source code.

## Vision

Build one customizable ERP platform for many colleges and schools with independent modules, strong role-based access control, audited operations, automated backups, and plugin-friendly growth.

## Architecture at a Glance

```text
React + TypeScript PWA
        │ HTTPS
        ▼
FastAPI Backend (versioned REST API)
        │
PostgreSQL + Redis
        │
Local Document Storage + Google Drive Backup Archive
```

## Technology Stack

| Layer | Technology |
| --- | --- |
| Frontend | React + TypeScript |
| UI | Material UI |
| Backend | FastAPI |
| ORM | SQLAlchemy |
| Validation | Pydantic |
| Database | PostgreSQL |
| Cache | Redis |
| Background Jobs | Celery |
| File Storage | Local Storage |
| Backup | Google Drive API |
| Authentication | JWT |
| Reports | ReportLab |
| Charts | Chart.js |
| Web Server | Nginx |
| Containerization | Docker |

## Repository Layout

```text
frontend/      React + TypeScript PWA shell
backend/       FastAPI application, modules, services, workers
docs/          SRS, ERD, API, and architecture documentation
database/      Schema notes, migrations, and seed data
storage/       Local runtime document folders for development
scripts/       Operational and developer scripts
docker/        Docker and Nginx assets
tests/         Automated tests
deployment/    Deployment manifests and runbooks
.github/       CI workflows and repository automation
```

## Initial Development Roadmap

1. Requirements Specification (SRS)
2. System Architecture
3. UI/UX Design
4. Database ER Diagram
5. Authentication and Roles
6. Admissions Module
7. Student Information System
8. Attendance
9. Examination and Results
10. Fee Management
11. Reports
12. Parent and Student Portals
13. Notifications
14. Backup and Restore
15. Testing, Security, and Deployment

See `docs/Architecture/ARCHITECTURE.md` for the detailed target architecture and module boundaries.

## Local Docker hosting

The default `docker-compose.yml` starts the complete local ERP without using the production environment file or production volume names:

- PostgreSQL and Redis
- One-time Alembic migration container
- FastAPI backend
- Celery worker and Celery beat
- PostgreSQL backup loop
- React/Nginx frontend

Start it from the repository root:

```powershell
.\scripts\start-local.ps1
```

Or run the equivalent Compose command:

```sh
docker compose up --build -d
```

Local URLs:

- ERP frontend: <http://localhost:8080>
- API documentation: <http://localhost:8000/docs>
- Backend readiness: <http://localhost:8000/health/ready>

Use the values of `FRONTEND_PORT` and `BACKEND_PORT` from `.env` if you changed them.

## First administrator and sign-in

After the migration container exits successfully, create the first administrator with the supported,
idempotent bootstrap command:

```powershell
docker compose exec backend python -m app.modules.authentication.bootstrap --college-id college-001 --email admin@college.local --full-name "System Administrator"
```

Enter a password of at least 12 characters at the secure prompt. Do not put the password in shell
history. The command reports success without creating a duplicate if that username or email already
exists. Then open the frontend and sign in using the same college ID, username `admin`, and password.

The `migrate` container is a one-time job. `Exited (0)` means it successfully brought the database
schema up to date; it is not expected to stay running.

## Institution setup

After sign-in, open **Institution setup** in the sidebar. Save the official institution name, campus,
principal, address, contact details, academic year, timezone, currency, logo, and brand colour. These
values are tenant-scoped and remain in PostgreSQL until deliberately changed or the database volume
is removed. Use the existing backup service before any destructive volume operation.

If PostgreSQL reports authentication failures, do **not** delete volumes. The local Compose project intentionally uses separate local credentials and volume names so it does not collide with production. Check whether the existing local volume was created with older credentials, then decide whether to migrate or back up that data before making destructive changes.

## Production Docker hosting

Production uses `docker-compose.production.yml` and requires a private `.env.production` file. The repository tracks `.env.production.example` only; never commit `.env.production`.

```powershell
Copy-Item .env.production.example .env.production
# Edit .env.production with real secrets, exact PostgreSQL credentials, Redis password, CORS origins, and trusted hosts.
.\scripts\start-production.ps1
```

The production script validates Compose, builds images, starts PostgreSQL and Redis, waits for health checks, stops old app processes, runs migrations once, and then starts backend, Celery, backups, and frontend. It does not remove Docker volumes.

Production validation rejects placeholder or short JWT secrets, development authentication headers, missing or mismatched PostgreSQL credentials, missing or mismatched Redis passwords, wildcard/malformed CORS origins, wildcard trusted hosts, URL values in `TRUSTED_HOSTS`, and invalid timeout/backup settings.

## Backup safety

Database backups are written under `storage/backups` so dumps can survive Docker volume removal. Generated dump, checksum, and partial files are ignored by Git while `storage/backups/.gitkeep` keeps the folder present.

Backups are written to a temporary `.partial` file first, renamed only after `pg_dump` succeeds, and accompanied by a SHA-256 checksum file. Retention cleanup only targets this application's matching `.dump` and `.dump.sha256` files; it does not delete unrelated files in the backup directory.

Local backups on the same computer are not a complete disaster-recovery plan. Regularly copy backup dumps and checksum files to another physical disk or secure cloud storage.

## Troubleshooting

- `migrate` must exit successfully before backend and Celery start. If it fails with an advisory-lock message, another migration is already running; wait for that process or investigate it rather than waiting indefinitely.
- If the frontend works locally but remote browsers call `localhost:8000`, check `VITE_API_BASE_URL`. Production builds default to `/api/v1` so the browser calls the same host serving the frontend.
- If `DATABASE_URL` and `POSTGRES_*` disagree in production, fix `.env.production`; do not change or delete existing database volumes.
- If `REDIS_URL` and `REDIS_PASSWORD` disagree in production, fix `.env.production` so the password appears in both places.
