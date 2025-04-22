from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from starlette import status
from database import db_dependency
from models import Users
from passlib.context import CryptContext
from typing import Annotated
from jose import jwt, JWTError
from schemes import TokenResponse, UserCreate, UserVerification
from enum import Enum
import os
from dotenv import load_dotenv
from pathlib import Path

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/auth/token")


def authenticate_user(username: str, password: str, db):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.password):
        return False
    return user


def create_access_token(
    username: str, user_id: int, role: Enum, expires_delta: timedelta
):
    encode = {"sub": username, "id": user_id, "role": role}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({"exp": expires})

    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        user_role: Enum = payload.get("role")
        if username is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not valdate user credentials",
            )
        return {"username": username, "id": user_id, "user_role": user_role}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not valdate user credentials",
        )


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def create_user(create_user_request: UserCreate, db: db_dependency):
    hashed_password = bcrypt_context.hash(create_user_request.password)

    create_user_model = Users(
        username=create_user_request.username,
        email=create_user_request.email,
        password=hashed_password,
        bio=create_user_request.bio,
        avatar=create_user_request.avatar,
        role=create_user_request.user_role,
    )

    db.add(create_user_model)
    db.commit()
    return {"detail": "User created successfully"}


@router.post("/token", status_code=status.HTTP_200_OK, response_model=TokenResponse)
async def login_for_access_token(
    db: db_dependency, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):

    validate_user = authenticate_user(form_data.username, form_data.password, db)

    if not validate_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Failed Authentication"
        )

    token = create_access_token(
        validate_user.username,
        validate_user.id,
        validate_user.role,
        timedelta(minutes=20),
    )

    return TokenResponse(access_token=token, token_type="bearer")
