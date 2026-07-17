from datetime import UTC, datetime

from sqlalchemy import delete

from app.core.celery_app import celery_app
from app.db.session import SessionLocal
from app.modules.authentication.models import RefreshToken


@celery_app.task(name="maintenance.cleanup_expired_refresh_tokens")
def cleanup_expired_refresh_tokens() -> int:
    """Delete expired or revoked refresh-token records and return the row count."""
    now = datetime.now(UTC)
    with SessionLocal() as db:
        result = db.execute(
            delete(RefreshToken).where(
                (RefreshToken.expires_at < now) | (RefreshToken.revoked_at.is_not(None))
            )
        )
        db.commit()
        return int(result.rowcount or 0)
