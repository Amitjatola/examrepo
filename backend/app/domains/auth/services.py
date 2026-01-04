from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
# from passlib.context import CryptContext
import bcrypt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.domains.auth.models import User
from app.domains.auth.schemas import UserCreate

# SECRET_KEY should ideally be in env vars
SECRET_KEY = "supersecretkey"  # TODO: Move to .env
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 3000  # Long expiry for convenience

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    # return pwd_context.verify(plain_password, hashed_password)
    password_byte = plain_password.encode('utf-8')
    # Handle cases where hashed_password might be string or bytes
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode('utf-8')
        
    return bcrypt.checkpw(password_byte, hashed_password)


def get_password_hash(password):
    # return pwd_context.hash(password)
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_user_by_email(session: AsyncSession, email: str):
    result = await session.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def create_user(session: AsyncSession, user: UserCreate):
    from app.domains.subscriptions.service import SubscriptionService
    
    hashed_password = get_password_hash(user.password)
    db_user = User(email=user.email, hashed_password=hashed_password, full_name=user.full_name)
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    
    # Auto-create 7-day trial subscription for new users
    subscription_service = SubscriptionService(session)
    await subscription_service.create_trial_subscription(db_user.id, trial_days=7)
    
    return db_user
