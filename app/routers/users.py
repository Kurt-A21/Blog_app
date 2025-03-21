from fastapi import APIRouter, HTTPException, Path
from starlette import status
from database import db_dependency 
from models import Users
from passlib.context import CryptContext
from schemes import UserCreate, UserUpdate, UserResponse

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/create_user", status_code=status.HTTP_201_CREATED)
async def create_iser(create_user_request: UserCreate, db: db_dependency):
    hashed_password = pwd_context.hash(create_user_request.password)
    create_user_model = Users(
        username  = create_user_request.username,
        email = create_user_request.email,
        password = hashed_password,
        bio = create_user_request.bio,
        avatar = create_user_request.avatar
        )
    db.add(create_user_model)
    db.commit()
    return {"message": "User createds"}