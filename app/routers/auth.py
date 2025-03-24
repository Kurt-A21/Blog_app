from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from starlette import status
from database import db_dependency
from models import Users
from passlib.context import CryptContext
from typing import Annotated
from jose import jwt, JWTError
from schemes.auth import TokenResponse

# import os
# from dotenv import load_dotenv
# from uuid import UUID

router = APIRouter()

SECRET_KEY = "9bac69e01d5a681e023c8cdd8fe513898fcfe5697f8a913100b57a85151e203"
ALGORITHM = "HS256"

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/auth/token")

def authenticate_user(username: str, password: str, db):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.password):
        return False
    return user


def create_access_token(username: str, user_id: int, expires_delta: timedelta):
    encode = {"sub": username, "id": user_id}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({"exp": expires})

    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not valdate user credentials")
        return {"username": username, "id": user_id}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not valdate user credentials")

@router.post("/token", status_code=status.HTTP_200_OK, response_model=TokenResponse)
async def login_for_access_token(
    db: db_dependency, 
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):

    validate_user = authenticate_user(form_data.username, form_data.password, db)

    if not validate_user:
        raise HTTPException(status_code=401, detail="Failed Authentication")

    token = create_access_token(
        validate_user.username, validate_user.id, timedelta(minutes=20)
    )

    return TokenResponse(access_token=token, token_type="bearer")
