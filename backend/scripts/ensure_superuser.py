#!/usr/bin/env python3
"""
Create or update a superuser with lifetime Premium (all Pro features).

Usage (from repo root or backend, with DATABASE_URL or backend/.env loaded):

  cd backend
  export AEROGATE_SUPERUSER_EMAIL=you@example.com
  export AEROGATE_SUPERUSER_PASSWORD='a-strong-password'
  python scripts/ensure_superuser.py

Or one-liner:
  AEROGATE_SUPERUSER_EMAIL=dev@qbt.world AEROGATE_SUPERUSER_PASSWORD='...' \\
    PYTHONPATH=. python scripts/ensure_superuser.py

After this, sign in with email/password in the app (set VITE_ENABLE_EMAIL_LOGIN=true on the frontend)
or use Google with the *same* email — both resolve to the same user row and Pro subscription.
"""

import asyncio
import os
import sys

# Allow running as `python scripts/ensure_superuser.py` from backend/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import get_session_context
from app.domains.auth.schemas import UserCreate
from app.domains.auth import services
from app.domains.subscriptions.service import SubscriptionService


async def main() -> None:
    email = (os.environ.get("AEROGATE_SUPERUSER_EMAIL") or "").strip()
    password = os.environ.get("AEROGATE_SUPERUSER_PASSWORD") or ""
    if not email or not password:
        print(
            "Set AEROGATE_SUPERUSER_EMAIL and AEROGATE_SUPERUSER_PASSWORD (non-empty).",
            file=sys.stderr,
        )
        sys.exit(1)

    name = os.environ.get("AEROGATE_SUPERUSER_NAME", "Superuser (Pro)").strip() or "Superuser (Pro)"

    async with get_session_context() as session:
        user = await services.get_user_by_email(session, email)
        if not user:
            user = await services.create_user(
                session,
                UserCreate(email=email, password=password, full_name=name),
            )
            print(f"Created user {email} (id={user.id})")
        else:
            user.hashed_password = services.get_password_hash(password)
            user.full_name = name
            session.add(user)
            await session.commit()
            await session.refresh(user)
            print(f"Updated password + name for existing user {email} (id={user.id})")

        sub_svc = SubscriptionService(session)
        await sub_svc.set_lifetime_premium(user.id)
        resp = await sub_svc.get_subscription_response(user.id)
        print(f"Subscription: type={resp.subscription_type.value} is_premium={resp.is_premium}")


if __name__ == "__main__":
    asyncio.run(main())
