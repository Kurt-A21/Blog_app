from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from PIL import Image
import secrets
from pathlib import Path
from starlette import status
from db import db_dependency, Users, Follows
from schemes import UserUpdate, UserEmailUpdate, GetUserResponse, UserVerification
from typing import Annotated, List
from .auth import get_current_user, bcrypt_context
from sqlalchemy.orm import joinedload

router = APIRouter()
router.mount("/static", StaticFiles(directory="static"), name="static")

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

    return [
        GetUserResponse(
            id=user.id,
            username=user.username,
            bio=user.bio,
            avatar=user.avatar or "/static/avatar.png",
            followers=len([f for f in user.followers if f.follower_user]),
            following=len([f for f in user.following if f.followed_user]),
            is_active=user.is_active,
        )
        for user in get_user_model
    ]


@router.get("/current_user", status_code=status.HTTP_200_OK)
async def get_current_user_details(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

    get_user_model = db.query(Users).filter(Users.id == user.get("id")).first()

    return get_user_model


@router.post("/upload_profile_picture", status_code=status.HTTP_200_OK)
async def upload_profile_picture(
    user: user_dependency, db: db_dependency, file: UploadFile = File(...)
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

    FILEPATH = Path(__file__).resolve().parent.parent / "static"
    FILEPATH.mkdir(parents=True, exist_ok=True)
    filename = file.filename
    extension = filename.rsplit(".")[-1].lower()

    if extension not in ["png", "jpg", "jpeg"]:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="File extension not allowed",
        )

    token_name = secrets.token_hex(10) + "." + extension
    generated_name = FILEPATH / token_name
    file_content = await file.read()

    with open(generated_name, "wb") as file:
        file.write(file_content)

    img = Image.open(generated_name)
    img.resize(size=(200, 200))
    img.save(generated_name)

    file.close()

    return {"detail": "Profile picture uploaded successfully"}


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
