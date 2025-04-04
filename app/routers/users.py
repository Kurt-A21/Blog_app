from fastapi import APIRouter, HTTPException, Depends, Query, Path
from starlette import status
from database import db_dependency
from models import Users
from schemes import UserUpdate, UserResponse, UserEmailUpdate
from typing import Optional, Annotated
from uuid import UUID
from .auth import get_current_user
from constants import UserRole, ReactionType

router = APIRouter()

user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/", status_code=status.HTTP_200_OK)
async def get_users(db: db_dependency):
    get_user_model = db.query(Users).all()
    if not get_user_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No users found"
        )
    return get_user_model


@router.get(
    "/get_user_by_id", status_code=status.HTTP_200_OK, response_model=UserResponse
)
async def get_user_by_id_or_accound_id(
    db: db_dependency,
    user_id: Optional[int] = Query(None),
    account_id: Optional[UUID] = Query(None),
):
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


@router.put("/update_user", status_code=status.HTTP_200_OK)
async def update_user(
    user: user_dependency,
    db: db_dependency,
    update_user_request: UserUpdate,
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

    user_id = user.get("id")
    user_details = db.query(Users).filter(Users.id == user_id).first()

    if not user_details:
        raise HTTPException(status_code=404, detail="User not found")

    user_details.username = update_user_request.username
    user_details.bio = update_user_request.bio
    user_details.avatar = update_user_request.avatar

    db.add(user_details)
    db.commit()
    return {"detail": "User updated successfully"}


@router.put("/update_email", status_code=status.HTTP_202_ACCEPTED)
async def update_user_email(
    user: user_dependency, db: db_dependency, update_email_request: UserEmailUpdate
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

    user_id = user.get("id")
    user_details = db.query(Users).filter(Users.id == user_id).first()

    if not user_details:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    user_details.email = update_email_request.email

    db.add(user_details)
    db.commit()
    return {"detail": "User email updated successfully"}


@router.delete("/delete_user/{user_id}", status_code=status.HTTP_200_OK)
async def delete_user(
    user: user_dependency, db: db_dependency, user_id: int = Path(ge=0)
):

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )

    user_id = user.get("id")

    db.query(Users).filter(Users.id == user_id).delete()
    db.commit()
    if Users.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not authorized",
        )
    return {"detail": "User deleted successfully"}
