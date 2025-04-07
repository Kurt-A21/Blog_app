from fastapi import APIRouter, HTTPException, Path, Query
from starlette import status
from database import db_dependency
from .users import user_dependency
from models import Users, Posts
from constants import UserRole
from schemes import UserResponse
from typing import Optional
from uuid import UUID

router = APIRouter()

@router.get("/", status_code=status.HTTP_200_OK)
async def get_users(user: user_dependency, db: db_dependency):
    if user is None or user.get("user_role") != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )
        
    get_user_model = db.query(Users).all()
    
    if not get_user_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No users found"
        )
    return get_user_model

@router.get(
    "/get_user_by_id/", status_code=status.HTTP_200_OK, response_model=UserResponse
)
async def get_user_by_id_or_accound_id(
    user: user_dependency,
    db: db_dependency,
    user_id: Optional[int] = Query(None),
    account_id: Optional[UUID] = Query(None),
):
    
    if user is None or user.get("user_role") != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )
          
    if not user_id and not account_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one ID (user_id or account_id) must be provided",
        )

    user_query = db.query(Users)

    if user_id:
        user_query = user_query.filter(Users.id == user_id)
    if account_id:
        user_query = user_query.filter(Users.account_id == account_id)

    user = user_query.first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    user_response = UserResponse(
        id=user.id,
        account_id=user.account_id,
        username=user.username,
        email=user.email,
        bio=user.bio,
        avatar=user.avatar,
        user_type=user.role,
        is_active=user.is_active,
        created_at=user.created_at,
        last_login=user.last_login,
    )

    return user_response

@router.delete("/delete_user/{user_id}", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency, user_id: int = Path(gt=0)):
    if user is None or user.get("user_role") != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

    delete_user_model = db.query(Users).filter(Users.id == user_id).first()

    if delete_user_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    db.query(Users).filter(Users.id == user_id).delete()
    db.commit()
    return {"detail": "User deleted successfully"}

@router.delete("/delete_post/{post_id}", status_code=status.HTTP_200_OK)
async def delete_post(user: user_dependency, db: db_dependency, post_id: int = Path(gt=0)):
    if user is None or user.get("user_role") != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )
        
    query_model = db.query(Posts).filter(Posts.id == post_id).first()
    
    if query_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    
    db.query(Posts).filter(Posts.id == post_id).delete()
    db.commit()
    
    return {"detail": "Post deleted successfully"}
    
