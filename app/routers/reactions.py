from fastapi import APIRouter, HTTPException, Path
from starlette import status
from database import db_dependency
from .users import user_dependency
from models import Posts, Reactions, Comments
from schemes import Reaction, ReactionResponse
from typing import Optional

router = APIRouter()


@router.post(
    "/{post_id}/reactions",
    status_code=status.HTTP_201_CREATED,
    response_model=ReactionResponse,
)
async def add_reaction_to_post(
    user: user_dependency,
    db: db_dependency,
    reaction_request: Reaction,
    post_id: int = Path(gt=0),
):
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

    query_post_model = db.query(Posts).filter(Posts.id == post_id).first()

    if query_post_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    existing_reaction = (
        db.query(Reactions)
        .filter(Reactions.post_id == post_id, Reactions.owner_id == user.get("id"))
        .first()
    )

    if existing_reaction is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already reacted to post",
        )

    reaction_model = Reactions(
        **reaction_request.model_dump(), owner_id=user.get("id"), post_id=post_id
    )

    db.add(reaction_model)
    db.commit()

    return ReactionResponse(
        detail="Reaction added to post",
        post_content=query_post_model.content,
        reaction_type=reaction_model.reaction_type,
    )


@router.post(
    "/{post_id}/comments/{comment_id}/reactions",
    status_code=status.HTTP_201_CREATED,
    response_model=ReactionResponse,
)
async def add_reaction_to_comment(
    user: user_dependency,
    db: db_dependency,
    reaction_request: Reaction,
    post_id: int = Path(gt=0),
    comment_id: int = Path(gt=0),
):
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

    query_post_model = db.query(Posts).filter(Posts.id == post_id).first()

    if query_post_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    query_comment_model = db.query(Comments).filter(Comments.id == comment_id).first()

    if query_comment_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
        )

    existing_reaction = (
        db.query(Reactions)
        .filter(
            Reactions.comment_id == comment_id, Reactions.owner_id == user.get("id")
        )
        .first()
    )

    if existing_reaction is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already reacted to comment",
        )

    if query_comment_model.post_id != post_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comment does not belong to the given post",
        )

    reaction_model = Reactions(
        **reaction_request.model_dump(), owner_id=user.get("id"), comment_id=comment_id
    )

    db.add(reaction_model)
    db.commit()

    return ReactionResponse(
        detail="Reaction added to comment",
        post_content=query_post_model.content,
        comment_content=query_comment_model.content,
        reaction_type=reaction_model.reaction_type,
    )


@router.put(
    "/{post_id}/reactions/{reaction_id}",
    status_code=status.HTTP_200_OK,
    response_model=ReactionResponse,
)
async def update_post_reaction(
    user: user_dependency,
    db: db_dependency,
    update_reaction_request: Reaction,
    post_id: int = Path(gt=0),
    reaction_id: int = Path(gt=0),
):
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

    query_post_model = db.query(Posts).filter(Posts.id == post_id).first()

    if query_post_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    update_reaction_model = (
        db.query(Reactions).filter(Reactions.id == reaction_id).first()
    )

    if not update_reaction_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Reaction to update not found"
        )

    check_reaction_owner = (
        db.query(Reactions)
        .filter(Reactions.id == reaction_id, Reactions.owner_id == user.get("id"))
        .first()
    )

    if check_reaction_owner is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not authorized to update this reaction",
        )

    update_reaction_model.reaction_type = update_reaction_request.reaction_type

    db.add(update_reaction_model)
    db.commit()

    return ReactionResponse(
        detail="Reaction type updated successfully",
        post_content=query_post_model.content,
        reaction_type=update_reaction_model.reaction_type,
    )


@router.put(
    "/{post_id}/comments/{comment_id}/reactions/{reaction_id}",
    status_code=status.HTTP_200_OK,
    response_model=ReactionResponse,
)
async def update_comment_reaction(
    user: user_dependency,
    db: db_dependency,
    update_reaction_request: Reaction,
    post_id: int = Path(gt=0),
    comment_id: int = Path(gt=0),
    reaction_id: int = Path(gt=0),
):
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

    query_post_model = db.query(Posts).filter(Posts.id == post_id).first()

    if query_post_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    query_comment_model = db.query(Comments).filter(Comments.id == comment_id).first()

    if query_comment_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
        )

    if query_comment_model.post_id != post_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comment does not belong to the given post",
        )

    check_reaction_owner = (
        db.query(Reactions)
        .filter(Reactions.id == reaction_id, Reactions.owner_id == user.get("id"))
        .first()
    )

    if check_reaction_owner is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this reaction",
        )

    update_reaction_model = (
        db.query(Reactions).filter(Reactions.id == reaction_id).first()
    )

    if not update_reaction_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Reaction to update not found"
        )

    update_reaction_model.reaction_type = update_reaction_request.reaction_type

    db.add(update_reaction_model)
    db.commit()

    return ReactionResponse(
        detail="Reaction type updated successfully",
        post_content=query_post_model.content,
        comment_content=query_comment_model.content,
        reaction_type=update_reaction_model.reaction_type,
    )


@router.delete(
    "/{post_id}/reactions/{reaction_id}",
    status_code=status.HTTP_200_OK,
)
async def undo_post_reaction(
    user: user_dependency,
    db: db_dependency,
    post_id: int = Path(gt=0),
    reaction_id: int = Path(gt=0),
):
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

    query_post_model = db.query(Posts).filter(Posts.id == post_id).first()

    if query_post_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    delete_reaction_model = (
        db.query(Reactions).filter(Reactions.id == reaction_id).first()
    )

    if delete_reaction_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Reaction to undo not found"
        )

    check_reaction_owner = (
        db.query(Reactions).filter(Reactions.id == reaction_id).first()
    )

    if check_reaction_owner.owner_id != user.get("id"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to undo this reaction",
        )

    db.query(Reactions).filter(Reactions.id == reaction_id).delete()
    db.commit()

    return {"detail": "Reaction deleted successfully"}


@router.delete(
    "/{post_id}/comments/{comment_id}reactions/{reaction_id}",
    status_code=status.HTTP_200_OK,
)
async def undo_comment_reaction(
    user: user_dependency,
    db: db_dependency,
    post_id: int = Path(gt=0),
    comment_id: int = Path(gt=0),
    reaction_id: int = Path(gt=0),
):
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

    query_post_model = db.query(Posts).filter(Posts.id == post_id).first()

    if query_post_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    query_comment_model = db.query(Comments).filter(Comments.id == comment_id).first()

    if query_comment_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
        )

    if query_comment_model.post_id != post_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comment does not belong to the given post",
        )

    check_reaction_owner = (
        db.query(Reactions)
        .filter(Reactions.id == reaction_id, Reactions.owner_id == user.get("id"))
        .first()
    )

    if check_reaction_owner is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this reaction",
        )

    delete_reaction_model = (
        db.query(Reactions).filter(Reactions.id == reaction_id).first()
    )

    if delete_reaction_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Reaction to undo not found"
        )

    check_reaction_owner = (
        db.query(Reactions).filter(Reactions.id == reaction_id).first()
    )

    if check_reaction_owner.owner_id != user.get("id"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to undo this reaction",
        )

    db.query(Reactions).filter(Reactions.id == reaction_id).delete()
    db.commit()

    return {"detail": "Reaction deleted successfully"}
