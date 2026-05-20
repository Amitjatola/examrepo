from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.domains.auth import schemas, services
from app.domains.auth.deps import get_current_user
from app.domains.auth.models import User

router = APIRouter()



@router.post("/google", response_model=schemas.Token)
async def login_with_google(token_data: schemas.GoogleAuthToken, session: AsyncSession = Depends(get_session)):
    google_user = await services.verify_google_token(token_data.token)
    
    if not google_user or not google_user.get("email"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google token",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    email = google_user["email"]
    user = await services.get_user_by_email(session, email=email)
    
    # Create user if they don't exist
    if not user:
        # Generate a high entropy dummy password for Google OAuth users
        dummy_password = __import__("secrets").token_urlsafe(32)
        
        user_create = schemas.UserCreate(
            email=email,
            password=dummy_password,
            full_name=google_user.get("full_name")
        )
        user = await services.create_user(session=session, user=user_create)

    # Issue access token
    access_token = services.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=schemas.Token)
async def register_with_email_password(
    body: schemas.UserCreate,
    session: AsyncSession = Depends(get_session),
):
    """Create account with email and password."""
    email = str(body.email).strip().lower()
    if len(body.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters",
        )

    existing = await services.get_user_by_email(session, email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists",
        )

    user_create = schemas.UserCreate(
        email=email,
        password=body.password,
        full_name=body.full_name,
    )
    user = await services.create_user(session=session, user=user_create)
    access_token = services.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login", response_model=schemas.Token)
async def login_with_email_password(
    body: schemas.UserLogin,
    session: AsyncSession = Depends(get_session),
):
    """
    Email + password login (for dev/superuser testing; production can disable via reverse proxy if needed).
    """
    user = await services.get_user_by_email(session, str(body.email))
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    if not services.verify_password(body.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    access_token = services.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=schemas.UserResponse)
async def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user
