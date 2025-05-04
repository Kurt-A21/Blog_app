from fastapi import APIRouter, HTTPException, UploadFile, File, Path
from starlette import status
from PIL import Image
import secrets
from pathlib import Path
from db import db_dependency, Posts, Comments, Users
from .users import user_dependency
from schemes import (
    PostCreate,
    CreatePostResponse,
    PostResponse,
    PostUpdate,
    ReactionListResponse,
    GetComments,
    GetReactions,
    UserTag,
    GetReplies,
)
import json
from datetime import datetime
import pytz
from typing import List
from sqlalchemy.orm import joinedload

router = APIRouter()


@router.get("", status_code=status.HTTP_200_OK, response_model=List[PostResponse])
async def get_all_posts(db: db_dependency):
    get_posts_model = (
        db.query(Posts)
        .options(
            joinedload(Posts.comments).joinedload(Comments.user),
            joinedload(Posts.reply),
        )
        .all()
    )

    if not get_posts_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Posts not found"
        )

    BASE_URL = "http://127.0.0.1:8000"

    return [
        PostResponse(
            id=post.id,
            created_by=post.created_by,
            tagged_users=post.get_tagged_user(),
            post_content=post.content,
            image_url=f"{BASE_URL}/static/{post.image_url or 'avatar.png'}",
            created_at=post.created_at,
            reaction_count=len(post.reactions),
            reactions=[
                ReactionListResponse(
                    id=reaction.id,
                    owner=reaction.user.username,
                    reaction_type=reaction.reaction_type,
                    reaction_count=len(post.reactions),
                )
                for reaction in post.reactions
            ],
            comment_count=len(post.comments),
            comments=[
                GetComments(
                    id=comment.id,
                    created_by=comment.user.username,
                    comment_content=comment.content,
                    created_at=comment.created_at,
                    reaction_count=len(post.reactions),
                    reactions=[
                        GetReactions(
                            id=reaction.id,
                            owner=reaction.user.username,
                            reaction_type=reaction.reaction_type,
                        )
                        for reaction in comment.reactions
                    ],
                )
                for comment in post.comments
            ],
            reply_count=len(post.reply),
            reply=[
                GetReplies(
                    id=reply.id,
                    created_by=reply.user.username,
                    reply_content=reply.content,
                    created_at=reply.created_at,
                    reaction_count=len(post.reactions),
                    reactions=[
                        GetReactions(
                            id=reactions.id,
                            owner=reactions.user.username,
                            reaction_type=reactions.reaction_type,
                        )
                        for reactions in reply.reactions
                    ],
                )
                for reply in post.reply
            ],
        )
        for post in get_posts_model
    ]


@router.get(
    "/user/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=List[PostResponse],
)
async def get_user_timeline(db: db_dependency, user_id: int = Path(gt=0)):
    get_posts_model = db.query(Posts).filter(Posts.owner_id == user_id).all()

    if not get_posts_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Posts not found"
        )

    BASE_URL = "http://127.0.0.1:8000"

    return [
        PostResponse(
            id=post.id,
            created_by=post.created_by,
            tagged_users=post.get_tagged_user(),
            post_content=post.content,
            image_url=f"{BASE_URL}/static/{post.image_url or 'avatar.png'}",
            created_at=post.created_at,
            reaction_count=len(post.reactions),
            reactions=[
                ReactionListResponse(
                    id=reaction.id,
                    owner=reaction.user.username,
                    reaction_type=reaction.reaction_type,
                    reaction_count=len(post.reactions),
                )
                for reaction in post.reactions
            ],
            comment_count=len(post.comments),
            comments=[
                GetComments(
                    id=comment.id,
                    created_by=comment.user.username,
                    content=comment.content,
                    created_at=comment.created_at,
                    reaction_count=len(post.reactions),
                    reactions=[
                        GetReactions(
                            id=reaction.id,
                            owner=reaction.user.username,
                            reaction_type=reaction.reaction_type,
                        )
                        for reaction in comment.reactions
                    ],
                )
                for comment in post.comments
            ],
            reply_count=len(post.reply),
            reply=[
                GetReplies(
                    id=reply.id,
                    created_by=reply.user.username,
                    reply_content=reply.content,
                    created_at=reply.created_at,
                    reaction_count=len(post.reactions),
                    reactions=[
                        GetReactions(
                            id=reactions.id,
                            owner=reactions.user.username,
                            reaction_type=reactions.reaction_type,
                        )
                        for reactions in reply.reactions
                    ],
                )
                for reply in post.reply
            ],
        )
        for post in get_posts_model
    ]


@router.post(
    "/create/", status_code=status.HTTP_201_CREATED, response_model=CreatePostResponse
)
async def create_post(
    user: user_dependency,
    db: db_dependency,
    post_request: PostCreate,
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed"
        )

    tagged_users = post_request.tagged_users

    for username in tagged_users:
        if tagged_users == user.get("username"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User can't tag themself",
            )

        check_tagged_users = db.query(Users).filter(Users.username == username).first()
        if check_tagged_users is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User to tag not found"
            )

    post_model = Posts(
        created_by=user.get("username"),
        owner_id=user.get("id"),
        content=post_request.post_content,
        created_at=datetime.now(pytz.utc),
    )

    post_model.set_tagged_user(tagged_users)

    db.add(post_model)
    db.commit()
    db.refresh(post_model)

    return {
        "detail": "Post created successfully",
        "post_details": PostResponse(
            id=user.get("id"),
            created_by=user.get("username"),
            tagged_users=post_model.get_tagged_user(),
            post_content=post_model.content,
            image_url=post_model.image_url,
            created_at=post_model.created_at,
        ),
    }


@router.put("/{posts_id}/update_post", status_code=status.HTTP_200_OK)
async def update_post(
    user: user_dependency,
    db: db_dependency,
    post_request: PostUpdate,
    posts_id: int = Path(gt=0),
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed"
        )

    post = db.query(Posts).filter(Posts.owner_id == user.get("id")).first()

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized to update this post",
        )

    update_posts_model = db.query(Posts).filter(Posts.id == posts_id).first()

    if not update_posts_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post to update not found"
        )

    update_posts_model.content = post_request.post_content
    update_posts_model.updated_date = datetime.now(pytz.utc)

    db.add(update_posts_model)
    db.commit()

    return {"detail": "Post updated successfully"}


@router.post("/{post_id}/upload_image", status_code=status.HTTP_200_OK)
async def upload_image_to_post(
    user: user_dependency,
    db: db_dependency,
    post_id: int = Path(gt=0),
    file: UploadFile = File(...),
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

    check_post = db.query(Posts).filter(Posts.id == post_id).first()

    if check_post.image_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has an image for this post",
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

    check_post.image_url = token_name
    db.commit()

    return {"detail": "Image on post uploaded successfully"}


@router.put("/{post_id}/update_image", status_code=status.HTTP_200_OK)
async def update_image_on_post(
    user: user_dependency,
    db: db_dependency,
    post_id: int = Path(gt=0),
    file: UploadFile = File(...),
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

    check_post = db.query(Posts).filter(Posts.id == post_id).first()

    if check_post.image_url:
        filename = file.filename
        extension = filename.rsplit(".")[-1].lower()

        if extension not in ["png", "jpg", "jpeg"]:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="File extension not allowed",
            )

        FILEPATH = Path(__file__).resolve().parent.parent / "static"
        FILEPATH.mkdir(parents=True, exist_ok=True)

        if check_post.image_url:
            old_avatar_path = FILEPATH / check_post.image_url
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

        check_post.image_url = token_name
        db.commit()

        return {"detail": "Image on post updated successfully"}


@router.delete("{post_id}/remove_image", status_code=status.HTTP_200_OK)
async def remove_image_from_post(
    user: user_dependency, db: db_dependency, post_id: int = Path(gt=0)
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

    check_post = db.query(Posts).filter(Posts.id == post_id).first()

    if check_post.image_url is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User does not have a image on this post",
        )

    FILEPATH = Path(__file__).resolve().parent.parent / "static"
    old_avatar_path = FILEPATH / check_post.image_url

    try:
        old_avatar_path.unlink()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete image: {e}")

    check_post.image_url = None
    db.commit()

    return {"detail": "Image removed from post"}


@router.post(
    "/{post_id}/add_user_tag",
    status_code=status.HTTP_200_OK,
)
async def add_user_tag(
    user: user_dependency,
    db: db_dependency,
    user_tag: UserTag,
    post_id: int = Path(gt=0),
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed"
        )

    query_post = db.query(Posts).filter(Posts.id == post_id).first()

    if query_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    post = db.query(Posts).filter(Posts.owner_id == user.get("id")).first()

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized to update this post",
        )

    if query_post.tagged_user:
        try:
            existing_tags = json.loads(query_post.tagged_user)
            if existing_tags:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Post already has user tags",
                )

        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Server error: tagged_user data is invalid JSON",
            )

    for username in user_tag.tagged_users:
        if username == user.get("username"):
            raise HTTPException(status_code=400, detail="User can't tag themselves")

        if query_post.is_user_tagged(username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User '{username}' already tagged",
            )

        tagged_user = db.query(Users).filter(Users.username == username).first()
        if not tagged_user:
            raise HTTPException(status_code=404, detail=f"User '{username}' not found")

    query_post.tagged_user = json.dumps(user_tag.tagged_users)
    db.commit()
    db.refresh(post)

    return {"detail": "Added user tag successfully"}


@router.delete("/{post_id}/delete_tag", status_code=status.HTTP_200_OK)
async def remove_user_tags(
    user: user_dependency, db: db_dependency, post_id: int = Path(gt=0)
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed"
        )

    query_post = db.query(Posts).filter(Posts.id == post_id).first()

    if query_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    post = db.query(Posts).filter(Posts.owner_id == user.get("id")).first()

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized to update this post",
        )

    if query_post.tagged_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post has no user tags"
        )

    db.query(Posts).filter(Posts.id == post_id).update(
        {Posts.tagged_user: json.dumps([])}
    )
    db.commit()

    return {"detail": "Tagged users removed from post"}


@router.delete("/{post_id}/delete", status_code=status.HTTP_200_OK)
async def delete_post(
    user: user_dependency, db: db_dependency, post_id: int = Path(gt=0)
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed"
        )

    query_post = db.query(Posts).filter(Posts.id == post_id).first()

    if query_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    post = db.query(Posts).filter(Posts.owner_id == user.get("id")).first()

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized to delete this post",
        )

    db.query(Posts).filter(Posts.id == post_id).delete()
    db.commit()

    return {"detail": "Post deleted successully"}
