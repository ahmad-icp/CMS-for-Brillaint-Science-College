import pytest
from fastapi import HTTPException

from app.core.security import CurrentUser, Permission


def test_legacy_admin_role_is_normalized() -> None:
    user = CurrentUser(user_id="user-1", college_id="college-001", role="admin")

    assert user.role == "administrator"
    assert Permission.ACADEMIC_WRITE in user.permissions


def test_unknown_role_is_rejected() -> None:
    with pytest.raises(HTTPException) as exc_info:
        CurrentUser(user_id="user-1", college_id="college-001", role="made-up-role")

    assert exc_info.value.status_code == 403
