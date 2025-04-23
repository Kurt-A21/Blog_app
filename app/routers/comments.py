from fastapi import APIRouter, HTTPException, Path
from starlette import status
from db import db_dependency, Comments, Posts
from .users import user_dependency
from schemes import CommentCreate, CommentResponse, CommentUpdate, GetComments
from sqlalchemy.orm import joinedload

router = APIRouter()


@router.post(
    "/{post_id}/comment",
    status_code=status.HTTP_201_CREATED,
    response_model=CommentResponse,
)
async def create_comment(
    user: user_dependency,
    db: db_dependency,
    comment_request: CommentCreate,
    post_id: int = Path(gt=0),
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

    query_model = db.query(Posts).filter(Posts.id == post_id).first()

    if query_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    comment_model = Comments(
        **comment_request.model_dump(), owner_id=user.get("id"), post_id=post_id
    )

    db.add(comment_model)
    db.commit()

    return CommentResponse(
        detail="Comment added successully",
        comment_id=query_model.owner_id,
        post_content=query_model.content,
        content=comment_model.content,
        created_at=comment_model.created_at,
    )


@router.put(
    "/{post_id}/comment/{comment_id}",
    status_code=status.HTTP_200_OK,
    response_model=CommentUpdate,
)
async def update_comment(
    user: user_dependency,
    db: db_dependency,
    update_comment_request: GetComments,
    post_id: int = Path(gt=0),
    comment_id: int = Path(gt=0),
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

    query_post_model = db.query(Posts).filter(Posts.id == post_id).first()

    if query_post_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    post = db.query(Posts).filter(Posts.owner_id == user.get("id")).first()

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized to update this post",
        )

    updated_comment_model = db.query(Comments).filter(Comments.id == comment_id).first()

    if updated_comment_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
        )

    updated_comment_model.content = update_comment_request.content

    db.add(updated_comment_model)
    db.commit()

    return CommentUpdate(
        detail="Comment updated successfully",
        content=updated_comment_model.content,
        created_at=updated_comment_model.created_at,
    )


@router.delete("/{post_id}/comment/{comment_id}", status_code=status.HTTP_200_OK)
async def delete_comment(
    user: user_dependency,
    db: db_dependency,
    post_id: int = Path(gt=0),
    comment_id: int = Path(gt=0),
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

    query_post_model = (
        db.query(Posts)
        .options(joinedload(Posts.comments))
        .filter(Posts.id == post_id)
        .first()
    )

    for comment in query_post_model.comments:
        if comment.id == comment_id:
            db.query(Comments).filter(Comments.id == comment_id).delete()
            db.commit()
            return {"detail": "Comment deleted succcessfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
            )
