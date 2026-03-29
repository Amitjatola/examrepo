from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.core.database import get_session
from app.domains.auth import schemas, services

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
