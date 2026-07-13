from app.modules.authentication.models import User
from app.modules.authentication.service import AuthenticationService, decode_access_token, hash_password


def test_authentication_issues_and_rotates_refresh_tokens(db_session):
    user = User(
        college_id="college-demo",
        username="admin",
        email="admin@example.com",
        full_name="Admin User",
        hashed_password=hash_password("secret-password"),
        role="administrator",
    )
    db_session.add(user)
    db_session.commit()

    service = AuthenticationService(db_session)
    authenticated = service.authenticate("admin", "secret-password", "college-demo")
    access_token, refresh_token = service.issue_tokens(authenticated)

    claims = decode_access_token(access_token)
    assert claims["sub"] == user.id
    assert claims["role"] == "administrator"

    new_access_token, new_refresh_token = service.refresh(refresh_token)
    assert new_access_token != access_token
    assert new_refresh_token != refresh_token
