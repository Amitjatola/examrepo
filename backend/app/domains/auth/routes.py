from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.core.database import get_session
from app.domains.auth import schemas, services

router = APIRouter()


@router.post("/register", response_model=schemas.UserResponse)
async def register(user: schemas.UserCreate, session: AsyncSession = Depends(get_session)):
    db_user = await services.get_user_by_email(session, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return await services.create_user(session=session, user=user)


@router.post("/login", response_model=schemas.Token)
async def login(form_data: schemas.UserLogin, session: AsyncSession = Depends(get_session)):
    user = await services.get_user_by_email(session, email=form_data.email)
    if not user or not services.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = services.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


# For OAuth2 form compatibility if needed (e.g. Swagger UI)
@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), session: AsyncSession = Depends(get_session)):
    user = await services.get_user_by_email(session, email=form_data.username)
    if not user or not services.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = services.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}
