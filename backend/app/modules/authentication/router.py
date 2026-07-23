from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.login_throttle import login_throttle
from app.db.session import get_db
from app.modules.authentication.schemas import LoginRequest, LogoutRequest, RefreshRequest, TokenResponse
from app.modules.authentication.service import AuthenticationService

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)) -> TokenResponse:
    client_host = request.client.host if request.client else "unknown"
    login_throttle.ensure_allowed(client_host, payload.college_id, payload.username)
    service = AuthenticationService(db)
    try:
        user = service.authenticate(payload.username, payload.password, payload.college_id)
    except HTTPException as exc:
        if exc.status_code == status.HTTP_401_UNAUTHORIZED:
            login_throttle.register_failure(client_host, payload.college_id, payload.username)
        raise
    login_throttle.reset(client_host, payload.college_id, payload.username)
    access_token, refresh_token = service.issue_tokens(user)
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)) -> TokenResponse:
    access_token, refresh_token = AuthenticationService(db).refresh(payload.refresh_token)
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(payload: LogoutRequest, db: Session = Depends(get_db)) -> Response:
    AuthenticationService(db).logout(payload.refresh_token)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
