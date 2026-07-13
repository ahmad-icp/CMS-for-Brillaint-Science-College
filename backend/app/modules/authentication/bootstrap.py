from __future__ import annotations

import argparse
from getpass import getpass

from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import Permission
from app.db.session import SessionLocal
from app.modules.authentication.models import PermissionModel, Role, User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    if len(password) < 12:
        raise ValueError("Password must be at least 12 characters")
    return pwd_context.hash(password)


def seed_rbac(db: Session, college_id: str = "global") -> None:
    permission_by_name = {p.name: p for p in db.scalars(select(PermissionModel)).all()}
    for permission in Permission:
        permission_by_name.setdefault(permission.value, PermissionModel(name=permission.value, description=permission.name.lower()))
    db.add_all(permission_by_name.values())
    admin_role = db.scalar(select(Role).where(Role.college_id == college_id, Role.name == "administrator"))
    if admin_role is None:
        admin_role = Role(college_id=college_id, name="administrator", description="Full administrative access")
        db.add(admin_role)
    admin_role.permissions = list(permission_by_name.values())
    db.commit()


def create_initial_admin(db: Session, email: str, password: str, college_id: str = "college-demo") -> User:
    if db.scalar(select(User).where(User.email == email)) is not None:
        raise ValueError("Admin user already exists")
    seed_rbac(db, college_id)
    role = db.scalar(select(Role).where(Role.college_id == college_id, Role.name == "administrator"))
    user = User(email=email, college_id=college_id, password_hash=hash_password(password), roles=[role] if role else [])
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def main() -> None:
    parser = argparse.ArgumentParser(description="Create the initial CMS administrator")
    parser.add_argument("--email", required=True)
    parser.add_argument("--college-id", default="college-demo")
    parser.add_argument("--password")
    args = parser.parse_args()
    password = args.password or getpass("Admin password: ")
    with SessionLocal() as db:
        user = create_initial_admin(db, args.email, password, args.college_id)
        print(f"Created admin {user.email} ({user.id})")


if __name__ == "__main__":
    main()
