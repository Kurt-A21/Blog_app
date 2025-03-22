from fastapi import APIRouter, HTTPException, Path, Depends
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status
from database import db_dependency 
from models import Users
from passlib.context import CryptContext
from typing import Optional, Annotated
from uuid import UUID


router = APIRouter()

bcryot_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def authenticate_user(usernamae: str, password: str, db):
    user = db.query(Users).filter(Users.username == usernamae)
    if not user:
        return False
    if not bcryot_context.verify(password, user.username):
        return False
    return True

@router.post("/token")
async def login_for_access_token(db: db_dependency,
                                 form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    
    validate_user = authenticate_user(form_data.username, form_data.password, db)
    
    if not validate_user:
        return {"message": "Failed Authentication"}
    return {"message": "Successfully Authenticated"}