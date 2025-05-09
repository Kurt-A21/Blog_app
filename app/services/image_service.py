import secrets
from pathlib import Path
from PIL import Image
from fastapi import UploadFile, HTTPException
from starlette import status
from typing import Optional
from app.db import Users, Posts


async def upload_image(file: UploadFile):
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

    return token_name


async def update_image(
    file: UploadFile, user: Optional[Users] = None, post: Optional[Posts] = None
):
    filename = file.filename
    extension = filename.rsplit(".")[-1].lower()

    if extension not in ["png", "jpg", "jpeg"]:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="File extension not allowed",
        )

    FILEPATH = Path(__file__).resolve().parent.parent / "static"
    FILEPATH.mkdir(parents=True, exist_ok=True)

    if user and user.avatar:
        old_image_path = FILEPATH / user.avatar
        if old_image_path.exists():
            old_image_path.unlink()

    if post and post.image_url:
        old_image_path = FILEPATH / post.image_url
        if old_image_path.exists():
            old_image_path.unlink()

    token_name = secrets.token_hex(10) + "." + extension
    generated_name = FILEPATH / token_name
    file_content = await file.read()

    with open(generated_name, "wb") as f:
        f.write(file_content)

    img = Image.open(generated_name)
    resized_img = img.resize(size=(200, 200))
    resized_img.save(generated_name)

    await file.close()

    return token_name


def remove_image(user: Optional[Users] = None, post: Optional[Posts] = None):
    FILEPATH = Path(__file__).resolve().parent.parent / "static"

    if user and user.avatar:
        old_avatar_path = FILEPATH / user.avatar

    if post and post.image_url:
        old_avatar_path = FILEPATH / post.image_url

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

    if post:
        return None

    if user:
        return default_avatar
