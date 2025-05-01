from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from PIL import Image
import secrets
from pathlib import Path
from starlette import status
from db import db_dependency, Users, Follows
from schemes import (
    UserUpdate,
    UserEmailUpdate,
    GetUserResponse,
    UserVerification,
    UserResponse,
)
from typing import Annotated, List
from .auth import get_current_user, bcrypt_context
from sqlalchemy.orm import joinedload

router = APIRouter()

user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("", status_code=status.HTTP_200_OK, response_model=List[GetUserResponse])
async def get_users(db: db_dependency):
    get_user_model = (
        db.query(Users)
        .options(
            joinedload(Users.followers).joinedload(Follows.follower_user),
            joinedload(Users.following).joinedload(Follows.followed_user),
        )
        .all()
    )

    if not get_user_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No users found"
        )

    BASE_URL = "http://127.0.0.1:8000"

    return [
        GetUserResponse(
            id=user.id,
            username=user.username,
            bio=user.bio,
            avatar=f"{BASE_URL}/static/{user.avatar or 'avatar.png'}",
            followers=len([f for f in user.followers if f.follower_user]),
            following=len([f for f in user.following if f.followed_user]),
            is_active=user.is_active,
        )
        for user in get_user_model
    ]


@router.get(
    "/current_user", status_code=status.HTTP_200_OK, response_model=UserResponse
)
async def get_current_user_details(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

    get_user_model = db.query(Users).filter(Users.id == user.get("id")).first()

    BASE_URL = "http://127.0.0.1:8000"
    avatar_url = f"{BASE_URL}/static/{get_user_model.avatar or 'avatar.png'}"

    return UserResponse(
        id=get_user_model.id,
        account_id=get_user_model.account_id,
        username=get_user_model.username,
        email=get_user_model.email,
        bio=get_user_model.bio,
        avatar=avatar_url,
        user_type=get_user_model.role,
        is_active=get_user_model.is_active,
        created_at=get_user_model.created_at,
        last_login=get_user_model.last_seen,
    )


@router.post("/upload_profile_picture", status_code=status.HTTP_200_OK)
async def upload_profile_picture(
    user: user_dependency, db: db_dependency, file: UploadFile = File(...)
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

    check_user = db.query(Users).filter(Users.id == user.get("id")).first()

    if check_user.avatar:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has a profile picture",
        )

    filename = file.filename
    extension = filename.rsplit(".")[-1].lower()
    if extension not in ["png", "jpg", "jpeg"]:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="File extension not allowed",
        )

    FILEPATH = Path(__file__).resolve().parent.parent / "static"
    FILEPATH.mkdir(parents=True, exist_ok=True)

    token_name = secrets.token_hex(10) + "." + extension
    generated_name = FILEPATH / token_name
    file_content = await file.read()

    with open(generated_name, "wb") as f:
        f.write(file_content)

    img = Image.open(generated_name)
    resized_img = img.resize(size=(200, 200))
    resized_img.save(generated_name)

    await file.close()

    check_user.avatar = token_name
    db.commit()

    return {"detail": "Profile picture uploaded successfully"}


@router.put("/update_profile_picture", status_code=status.HTTP_200_OK)
async def update_profile_picture(
    user: user_dependency, db: db_dependency, file: UploadFile = File(...)
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

    check_user = db.query(Users).filter(Users.id == user.get("id")).first()

    if check_user.avatar:
        filename = file.filename
        extension = filename.rsplit(".")[-1].lower()

        if extension not in ["png", "jpg", "jpeg"]:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="File extension not allowed",
            )

        FILEPATH = Path(__file__).resolve().parent.parent / "static"
        FILEPATH.mkdir(parents=True, exist_ok=True)

        if check_user.avatar:
            old_avatar_path = FILEPATH / check_user.avatar
            if old_avatar_path.exists():
                old_avatar_path.unlink()

        token_name = secrets.token_hex(10) + "." + extension
        generated_name = FILEPATH / token_name
        file_content = await file.read()

        with open(generated_name, "wb") as f:
            f.write(file_content)

        img = Image.open(generated_name)
        resized_img = img.resize(size=(200, 200))
        resized_img.save(generated_name)

        await file.close()

        check_user.avatar = token_name
        db.commit()

        return {"detail": "Profile picture updated successfully"}


@router.delete("/remove_profile_picture", status_code=status.HTTP_200_OK)
async def remove_profile_picture(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

    check_user = db.query(Users).filter(Users.id == user.get("id")).first()

    if check_user.avatar is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User does not have a profile picture",
        )

    FILEPATH = Path(__file__).resolve().parent.parent / "static"
    old_avatar_path = FILEPATH / check_user.avatar

    try:
        old_avatar_path.unlink()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to delete profile picture: {e}"
        )

    default_avatar = "avatar.png"
    default_avatar_path = FILEPATH / default_avatar

    if default_avatar_path is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Default avatar image not found",
        )

    check_user.avatar = default_avatar
    db.commit()

    return {"detail": "Profile picture removed successfully"}


@router.put("/change_password", status_code=status.HTTP_200_OK)
async def change_password(
    user: user_dependency, db: db_dependency, verify_user: UserVerification
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

    user_model = db.query(Users).filter(Users.id == user.get("id")).first()

    if not bcrypt_context.verify(verify_user.password, user_model.password):
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password"
        )

    user_model.password = bcrypt_context.hash(verify_user.new_password)

    db.add(user_model)
    db.commit()

    return {"detail": "Password updated successfully"}


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

    user_details = db.query(Users).filter(Users.id == user.get("id")).first()

    user_details.username = update_user_request.username
    user_details.bio = update_user_request.bio

    db.add(user_details)
    db.commit()
    return {"detail": "User updated successfully"}


@router.put("/update_email", status_code=status.HTTP_200_OK)
async def update_user_email(
    user: user_dependency, db: db_dependency, update_email_request: UserEmailUpdate
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

    user_details = db.query(Users).filter(Users.id == user.get("id")).first()

    user_details.email = update_email_request.email

    db.add(user_details)
    db.commit()
    return {"detail": "User email updated successfully"}


@router.delete("/deactivate_account", status_code=status.HTTP_200_OK)
async def deactivate_account(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

    db_user = db.query(Users).filter(Users.id == user.get("id")).first()

    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    try:
        db.delete(db_user)
        db.commit()
        return {"detail": "User and all related data deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while deactivating the account: {str(e)}",
        )
