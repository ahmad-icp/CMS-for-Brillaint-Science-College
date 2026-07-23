from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import CurrentUser, Permission, require_permission
from app.db.session import get_db
from app.modules.tenant_settings.models import TenantSettings
from app.modules.tenant_settings.schemas import TenantSettingsPayload, TenantSettingsResponse

router = APIRouter()


@router.get("/me", response_model=TenantSettingsResponse)
def get_tenant_settings(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission(Permission.ACADEMIC_READ)),
) -> TenantSettings:
    settings = db.get(TenantSettings, current_user.college_id)
    if settings is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Institution setup has not been completed")
    return settings


@router.put("/me", response_model=TenantSettingsResponse)
def save_tenant_settings(
    payload: TenantSettingsPayload,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_permission(Permission.ACADEMIC_WRITE)),
) -> TenantSettings:
    settings = db.get(TenantSettings, current_user.college_id)
    if settings is None:
        settings = TenantSettings(college_id=current_user.college_id, **payload.model_dump())
        db.add(settings)
    else:
        for name, value in payload.model_dump().items():
            setattr(settings, name, value)
    db.commit()
    db.refresh(settings)
    return settings
