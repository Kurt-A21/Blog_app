from fastapi import APIRouter, HTTPException, Path
from starlette import status
from database import db_dependency
from schemes import UsersRequest
from models import Users
from passlib.context import CryptContext
from schemes import UserCreate, UserUpdate, UserResponse

router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_iser(create_user_request: UserCreate, db: db_dependency):
    create_user_model = Users(**create_user_request.model_dump())
    db.add(create_user_model)
    db.commit()
    return {"message": "User createds"}