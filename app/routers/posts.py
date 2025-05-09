from fastapi import APIRouter, HTTPException, UploadFile, File, Path as PathParam
from starlette import status
from pathlib import Path
from app.db import db_dependency, Posts, Comments, Users, CommentReply, Reactions
from .users import user_dependency
from app.schemes import (
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
from app.services import upload_image, update_image, remove_image
import json
from datetime import datetime
import pytz
from typing import List
from sqlalchemy.orm import joinedload
import os
from app.utils import load_environment, is_user_authenticated, get_post_or_404

router = APIRouter()

load_environment()
BASE_URL = os.getenv("BASE_URL")


@router.get("", status_code=status.HTTP_200_OK, response_model=List[PostResponse])
async def get_all_posts(db: db_dependency):
    query_posts = db.query(Posts).options(
        joinedload(Posts.comments).joinedload(Comments.user),
        joinedload(Posts.comments)
        .joinedload(Comments.reactions)
        .joinedload(Reactions.user),
        joinedload(Posts.comments)
        .joinedload(Comments.replies)
        .joinedload(CommentReply.user),
        joinedload(Posts.comments)
        .joinedload(Comments.replies)
        .joinedload(CommentReply.reactions)
        .joinedload(Reactions.user),
        joinedload(Posts.reactions).joinedload(Reactions.user),
    )

    if not query_posts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Posts not found"
        )

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
                    reaction_count=len(comment.reactions),
                    reactions=[
                        GetReactions(
                            id=comment_reaction.id,
                            owner=comment_reaction.user.username,
                            reaction_type=comment_reaction.reaction_type,
                        )
                        for comment_reaction in comment.reactions
                    ],
                    reply_count=len(comment.replies),
                    reply=[
                        GetReplies(
                            id=reply.id,
                            created_by=reply.user.username,
                            reply_content=reply.content,
                            created_at=reply.created_at,
                            reaction_count=len(reply.reactions),
                            reactions=[
                                GetReactions(
                                    id=reply_reactions.id,
                                    owner=reply_reactions.user.username,
                                    reaction_type=reply_reactions.reaction_type,
                                )
                                for reply_reactions in reply.reactions
                            ],
                        )
                        for reply in comment.replies
                    ],
                )
                for comment in post.comments
            ],
        )
        for post in query_posts
    ]


@router.get(
    "/user/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=List[PostResponse],
)
async def get_user_timeline(db: db_dependency, user_id: int = PathParam(gt=0)):
    query_posts = db.query(Posts).filter(Posts.owner_id == user_id).all()

    if not query_posts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Posts not found"
        )

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
                    reaction_count=len(comment.reactions),
                    reactions=[
                        GetReactions(
                            id=comment_reaction.id,
                            owner=comment_reaction.user.username,
                            reaction_type=comment_reaction.reaction_type,
                        )
                        for comment_reaction in comment.reactions
                    ],
                    reply_count=len(comment.replies),
                    reply=[
                        GetReplies(
                            id=reply.id,
                            created_by=reply.user.username,
                            reply_content=reply.content,
                            created_at=reply.created_at,
                            reaction_count=len(reply.reactions),
                            reactions=[
                                GetReactions(
                                    id=reply_reactions.id,
                                    owner=reply_reactions.user.username,
                                    reaction_type=reply_reactions.reaction_type,
                                )
                                for reply_reactions in reply.reactions
                            ],
                        )
                        for reply in comment.replies
                    ],
                )
                for comment in post.comments
            ],
        )
        for post in query_posts
    ]


@router.post(
    "/create", status_code=status.HTTP_201_CREATED, response_model=CreatePostResponse
)
async def create_post(
    user: user_dependency,
    db: db_dependency,
    post_request: PostCreate,
):
    check_auth = is_user_authenticated(user)
    tagged_users = post_request.tagged_users

    for username in tagged_users:
        if username == check_auth.get("username"):
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
        created_by=check_auth.get("username"),
        owner_id=check_auth.get("id"),
        content=post_request.post_content,
        image_url=None,
        created_at=datetime.now(pytz.utc),
    )

    post_model.set_tagged_user(tagged_users)

    db.add(post_model)
    db.commit()
    db.refresh(post_model)

    return {
        "detail": "Post created successfully",
        "post_details": PostResponse(
            id=check_auth.get("id"),
            created_by=check_auth.get("username"),
            tagged_users=post_model.get_tagged_user(),
            post_content=post_model.content,
            created_at=post_model.created_at,
        ),
    }


@router.put("/{posts_id}/update_post", status_code=status.HTTP_200_OK)
async def update_post(
    user: user_dependency,
    db: db_dependency,
    post_request: PostUpdate,
    posts_id: int = PathParam(gt=0),
):
    check_auth = is_user_authenticated(user)
    query_post = get_post_or_404(db=db, post_id=posts_id)

    if query_post.owner_id != check_auth.get("id"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized to update this post",
        )

    query_post.content = post_request.post_content
    query_post.updated_date = datetime.now(pytz.utc)

    db.add(query_post)
    db.commit()

    return {"detail": "Post updated successfully"}


@router.post("/{post_id}/upload_image", status_code=status.HTTP_200_OK)
async def upload_image_to_post(
    user: user_dependency,
    db: db_dependency,
    post_id: int = PathParam(gt=0),
    file: UploadFile = File(...),
):
    is_user_authenticated(user)
    query_post = get_post_or_404(db=db, post_id=post_id)

    if query_post.image_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already have an image for this post",
        )

    image = await upload_image(file)

    query_post.image_url = image
    db.commit()

    return {"detail": "Image on post uploaded successfully"}


@router.put("/{post_id}/update_image", status_code=status.HTTP_200_OK)
async def update_image_on_post(
    user: user_dependency,
    db: db_dependency,
    post_id: int = PathParam(gt=0),
    file: UploadFile = File(...),
):
    is_user_authenticated(user)
    query_post = get_post_or_404(db=db, post_id=post_id)

    if query_post.image_url:
        image = await update_image(post=query_post, file=file)

        query_post.image_url = image
        db.commit()

        return {"detail": "Image on post updated successfully"}


@router.delete("/{post_id}/remove_image", status_code=status.HTTP_200_OK)
async def remove_image_from_post(
    user: user_dependency, db: db_dependency, post_id: int = PathParam(gt=0)
):
    is_user_authenticated(user)
    query_post = get_post_or_404(db=db, post_id=post_id)

    if query_post.image_url is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User does not have a image on this post",
        )

    image = remove_image(post=query_post)

    query_post.image_url = image
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
    post_id: int = PathParam(gt=0),
):
    check_auth = is_user_authenticated(user)
    query_post = get_post_or_404(db=db, post_id=post_id)

    if query_post.owner_id != check_auth.get("id"):
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
        if username == check_auth.get("username"):
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
    db.refresh(query_post)

    return {"detail": "Added user tag successfully"}


@router.delete("/{post_id}/delete_tag", status_code=status.HTTP_200_OK)
async def remove_user_tags(
    user: user_dependency, db: db_dependency, post_id: int = PathParam(gt=0)
):
    check_auth = is_user_authenticated(user)
    query_post = get_post_or_404(db=db, post_id=post_id)

    if query_post.owner_id != check_auth.get("id"):
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
    user: user_dependency, db: db_dependency, post_id: int = PathParam(gt=0)
):
    check_auth = is_user_authenticated(user)
    query_post = get_post_or_404(db=db, post_id=post_id)

    if query_post.owner_id != check_auth.get("id"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized to delete this post",
        )

    db.delete(query_post)
    db.commit()

    return {"detail": "Post deleted successully"}
