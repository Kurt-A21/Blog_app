from datetime import datetime, timedelta, timezone
import pytz
from fastapi import APIRouter, Security, HTTPException, Depends, Query
from pydantic import EmailStr
from fastapi.security import (
    OAuth2PasswordRequestForm,
    OAuth2PasswordBearer,
    APIKeyHeader,
)
from pathlib import Path
from starlette import status
from app.db import db_dependency, Users
from passlib.context import CryptContext
from typing import Annotated, Union
from jose import jwt, JWTError
from app.schemes import TokenResponse, UserCreate, ResetPassword
from enum import Enum
import os
from app.services import send_reset_email, create_reset_token, verify_reset_token
from app.utils import load_environment


load_environment()
router = APIRouter()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/auth/login")
api_key_scheme = APIKeyHeader(name="Authorization")


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


async def get_current_user(
    token: Annotated[str, Depends(oauth2_bearer)],
    token_from_header: Union[str, None] = Security(api_key_scheme),
):
    final_token = token or token_from_header

    if not final_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="No token provided"
        )

    try:
        payload = jwt.decode(final_token, SECRET_KEY, algorithms=[ALGORITHM])
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

    FILEPATH = Path(__file__).resolve().parent.parent / "static"
    default_avatar = "avatar.png"
    default_avatar_path = FILEPATH / default_avatar

    if default_avatar_path is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Default avatar image not found",
        )

    default_avatar = create_user_request.avatar

    create_user_model = Users(
        username=create_user_request.username,
        email=create_user_request.email,
        password=hashed_password,
        bio=create_user_request.bio,
        avatar=default_avatar,
        role=create_user_request.user_role,
        created_at=datetime.now(pytz.utc),
    )

    db.add(create_user_model)
    db.commit()
    return {"detail": "User created successfully"}


@router.post("/forgot_password/{email}", status_code=status.HTTP_200_OK)
async def forgot_password(email: EmailStr, db: db_dependency):

    existing_user = db.query(Users).filter(Users.email == email).first()

    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Email not found"
        )

    reset_token = create_reset_token(email, timedelta(minutes=20))

    # reset_link = f"http://localhost:8000/auth/reset_password?reset_token={reset_token}"

    send_reset_email(email, existing_user.username, reset_token)
    return {"detail": "Reset link sent to email"}


@router.put("/reset_password/", status_code=status.HTTP_201_CREATED)
async def reset_password(
    db: db_dependency,
    reset_password_request: ResetPassword,
    reset_token: str = Query(None),
):

    validate_user = verify_reset_token(reset_token)

    if not validate_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Failed Authentication"
        )

    validate_user = db.query(Users).filter(Users.email == validate_user).first()

    hashed_password = bcrypt_context.hash(reset_password_request.new_password)

    validate_user.password = hashed_password

    db.add(validate_user)
    db.commit()
    return {"detail": "Password reset successful"}


@router.post("/login", status_code=status.HTTP_200_OK, response_model=TokenResponse)
async def login_for_access_token(
    db: db_dependency, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):

    validate_user = authenticate_user(form_data.username, form_data.password, db)

    if not validate_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Failed Authentication"
        )

    validate_user.is_active = True
    db.commit()

    token = create_access_token(
        validate_user.username,
        validate_user.id,
        validate_user.role,
        timedelta(minutes=20),
    )

    return TokenResponse(access_token=token, token_type="bearer")


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(user: Annotated[dict, Depends(get_current_user)], db: db_dependency):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed"
        )

    get_current_user = db.query(Users).filter(Users.id == user.get("id")).first()

    get_current_user.is_active = False
    get_current_user.last_seen = datetime.now(pytz.utc)
    db.commit()
    return {"detail": "Logged out"}
