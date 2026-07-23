"""Create the first College ERP administrator safely and idempotently."""

import argparse
import getpass
import os

from sqlalchemy import or_, select

import app.db.models  # noqa: F401
from app.db.session import SessionLocal
from app.modules.authentication.models import User
from app.modules.authentication.service import hash_password


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create the first College ERP administrator.")
    parser.add_argument("--college-id", required=True)
    parser.add_argument("--username", default="admin")
    parser.add_argument("--email", required=True)
    parser.add_argument("--full-name", default="System Administrator")
    parser.add_argument("--password", help="Prefer BOOTSTRAP_ADMIN_PASSWORD or the secure prompt.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    password = args.password or os.getenv("BOOTSTRAP_ADMIN_PASSWORD") or getpass.getpass("Administrator password: ")
    if len(password) < 12:
        raise SystemExit("Administrator password must contain at least 12 characters.")

    with SessionLocal() as db:
        existing = db.scalar(
            select(User).where(
                or_(
                    (User.college_id == args.college_id) & (User.username == args.username),
                    User.email == args.email,
                )
            )
        )
        if existing is not None:
            print(f"Administrator already exists: {existing.username} ({existing.college_id})")
            return 0

        user = User(
            college_id=args.college_id,
            username=args.username,
            email=args.email,
            full_name=args.full_name,
            hashed_password=hash_password(password),
            role="administrator",
            is_active=True,
        )
        db.add(user)
        db.commit()
        print(f"Administrator created: {user.username} ({user.college_id})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
