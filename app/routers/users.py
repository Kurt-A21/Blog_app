from fastapi import APIRouter, HTTPException, Path, Query
from starlette import status
from database import db_dependency 
from models import Users
from passlib.context import CryptContext
from schemes import UserCreate, UserUpdate, UserResponse
from typing import Optional
from uuid import UUID

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.get("/", status_code=status.HTTP_200_OK)
async def get_users(db: db_dependency):
    get_user_model = db.query(Users).all()
    if get_user_model is None:
        raise HTTPException(status_code=404, detail="No users found")
    return get_user_model

@router.get("/get_user_by_id", status_code=status.HTTP_200_OK, response_model=UserResponse)
async def get_user_by_id_or_accound_id(db: db_dependency,
                                        user_id: Optional[int] = Query(None),
                                        account_id: Optional[UUID] = Query(None)
                                    ):
    if not user_id and not account_id:
        raise HTTPException(status_code=400, detail="At least one ID (user_id or account_id) must be provided")
    
    user_query = db.query(Users)
    
    if user_id:
        user_query = user_query.filter(Users.id == user_id)
    if account_id:
        user_query = user_query.filter(Users.account_id == account_id)
    
    user = user_query.first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_response = UserResponse(
        id=user.id,
        account_id=user.account_id,
        username=user.username,
        email=user.email,
        bio=user.bio,
        avatar=user.avatar,
        user_type=user.user_type,
        is_active=user.is_active,
        created_at=user.created_at,
        last_login=user.last_login
    )

    return user_response
    

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
    return {"message": "User created successfully"}

@router.put("/updated_user/{account_id}", status_code=status.HTTP_202_ACCEPTED)
async def updated_user(db: db_dependency, update_user_request: UserUpdate, account_id: UUID = Path):
    check_user_exist = db.query(Users).filter(Users.account_id == account_id).first()
    
    if check_user_exist is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    updated_user_model = Users(
        username = update_user_request.username,
        email = update_user_request.email,
        bio = update_user_request.bio,
        avatar = update_user_request.avatar
    )
    db.add(updated_user_model)
    db.commit()
    return {"message": "User updated successfully"}

@router.delete("/delete_user/{account_id}", status_code=status.HTTP_200_OK)
async def delete_user(db: db_dependency, account_id: UUID = Path(min_length=1)):
    delete_user_model = db.query(Users).filter(Users.account_id == account_id).first()
    
    if not delete_user_model:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.query(Users).filter(Users.account_id == account_id).delete()
    db.commit()
    return {"message": "User deleted successfully"}
    

        