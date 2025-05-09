from fastapi import APIRouter, HTTPException, Path as PathParam
from starlette import status
from app.db import db_dependency, Reactions
from .users import user_dependency
from app.schemes import Reaction, ReactionResponse
from app.utils import (
    is_user_authenticated,
    get_post_or_404,
    get_comment_or_404,
    get_reply_or_404,
    get_reaction_or_404,
    get_existing_reaction,
)

router = APIRouter()


@router.post(
    "/{post_id}/reaction",
    status_code=status.HTTP_201_CREATED,
    response_model=ReactionResponse,
)
async def add_reaction_to_post(
    user: user_dependency,
    db: db_dependency,
    reaction_request: Reaction,
    post_id: int = PathParam(gt=0),
):
    check_auth = is_user_authenticated(user)
    query_post = get_post_or_404(db=db, post_id=post_id)

    existing = get_existing_reaction(
        db=db, user_id=check_auth.get("id"), post_id=post_id
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already reacted to post",
        )

    reaction_model = Reactions(
        owner_id=check_auth.get("id"),
        post_id=post_id,
        reaction_type=reaction_request.reaction_type,
    )

    db.add(reaction_model)
    db.commit()

    return ReactionResponse(
        detail="Reaction added to post",
        post_content=query_post.content,
        reaction_type=reaction_model.reaction_type,
    )


@router.post(
    "/{post_id}/comment/{comment_id}/reaction",
    status_code=status.HTTP_201_CREATED,
    response_model=ReactionResponse,
)
async def add_reaction_to_comment(
    user: user_dependency,
    db: db_dependency,
    reaction_request: Reaction,
    post_id: int = PathParam(gt=0),
    comment_id: int = PathParam(gt=0),
):
    check_auth = is_user_authenticated(user)
    query_post = get_post_or_404(db=db, post_id=post_id)
    query_comment = get_comment_or_404(db=db, comment_id=comment_id)

    existing = get_existing_reaction(
        db=db, user_id=check_auth.get("id"), comment_id=comment_id
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already reacted to comment",
        )

    if query_comment.post_id != post_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comment does not belong to the given post",
        )

    reaction_model = Reactions(
        owner_id=check_auth.get("id"),
        post_id=post_id,
        comment_id=comment_id,
        reaction_type=reaction_request.reaction_type,
    )

    db.add(reaction_model)
    db.commit()

    return ReactionResponse(
        detail="Reaction added to comment",
        post_content=query_post.content,
        comment_content=query_comment.content,
        reaction_type=reaction_model.reaction_type,
    )


@router.post(
    "/{post_id}/comment/{comment_id}/reply/{reply_id}/reaction",
    status_code=status.HTTP_201_CREATED,
    response_model=ReactionResponse,
)
async def add_reaction_to_reply(
    user: user_dependency,
    db: db_dependency,
    reaction_request: Reaction,
    post_id: int = PathParam(gt=0),
    comment_id: int = PathParam(gt=0),
    reply_id: int = PathParam(gt=0),
):
    check_auth = is_user_authenticated(user)
    query_post = get_post_or_404(db=db, post_id=post_id)
    query_comment = get_comment_or_404(db=db, comment_id=comment_id)
    query_reply = get_reply_or_404(db=db, reply_id=reply_id)

    if query_reply is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Reply not found"
        )

    existing = get_existing_reaction(
        db=db, user_id=check_auth.get("id"), reply_id=reply_id
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already reacted to reply",
        )

    if query_reply.comment_id != comment_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reply does not belong to the given comment",
        )

    reaction_model = Reactions(
        owner_id=check_auth.get("id"),
        post_id=post_id,
        comment_id=comment_id,
        reply_id=reply_id,
        reaction_type=reaction_request.reaction_type,
    )

    db.add(reaction_model)
    db.commit()

    return ReactionResponse(
        detail="Reaction added to comment",
        post_content=query_post.content,
        comment_content=query_comment.content,
        reply_content=query_reply.content,
        reaction_type=reaction_model.reaction_type,
    )


@router.put(
    "/{post_id}/reaction/{reaction_id}",
    status_code=status.HTTP_200_OK,
    response_model=ReactionResponse,
)
async def update_post_reaction(
    user: user_dependency,
    db: db_dependency,
    update_reaction_request: Reaction,
    post_id: int = PathParam(gt=0),
    reaction_id: int = PathParam(gt=0),
):
    check_auth = is_user_authenticated(user)
    query_post = get_post_or_404(db=db, post_id=post_id)
    query_reaction = get_reaction_or_404(
        db=db, reaction_id=reaction_id, action="update"
    )

    if query_reaction.owner_id != check_auth.get("id"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this reaction",
        )

    query_reaction.reaction_type = update_reaction_request.reaction_type

    db.add(query_reaction)
    db.commit()

    return ReactionResponse(
        detail="Reaction type updated successfully",
        post_content=query_post.content,
        reaction_type=query_reaction.reaction_type,
    )


@router.put(
    "/{post_id}/comment/{comment_id}/reaction/{reaction_id}",
    status_code=status.HTTP_200_OK,
    response_model=ReactionResponse,
)
async def update_comment_reaction(
    user: user_dependency,
    db: db_dependency,
    update_reaction_request: Reaction,
    post_id: int = PathParam(gt=0),
    comment_id: int = PathParam(gt=0),
    reaction_id: int = PathParam(gt=0),
):
    check_auth = is_user_authenticated(user)
    query_post = get_post_or_404(db=db, post_id=post_id)
    query_comment = get_comment_or_404(db=db, comment_id=comment_id)

    if query_comment.post_id != post_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comment does not belong to the given post",
        )

    query_reaction = get_reaction_or_404(
        db=db, reaction_id=reaction_id, action="update"
    )

    if query_reaction.owner_id != check_auth.get("id"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this reaction",
        )

    query_reaction.reaction_type = update_reaction_request.reaction_type

    db.add(query_reaction)
    db.commit()

    return ReactionResponse(
        detail="Reaction type updated successfully",
        post_content=query_post.content,
        comment_content=query_comment.content,
        reaction_type=query_reaction.reaction_type,
    )


@router.put(
    "/{post_id}/comment/{comment_id}/reply/{reply_id}/reaction/{reaction_id}",
    status_code=status.HTTP_200_OK,
    response_model=ReactionResponse,
)
async def update_reply_reaction(
    user: user_dependency,
    db: db_dependency,
    update_reaction_request: Reaction,
    post_id: int = PathParam(gt=0),
    comment_id: int = PathParam(gt=0),
    reply_id: int = PathParam(gt=0),
    reaction_id: int = PathParam(gt=0),
):
    check_auth = is_user_authenticated(user)
    query_post = get_post_or_404(db=db, post_id=post_id)
    query_comment = get_comment_or_404(db=db, comment_id=comment_id)

    if query_comment.post_id != post_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comment does not belong to the given post",
        )

    query_reply = get_reply_or_404(db=db, reply_id=reply_id)

    if query_reply.comment_id != comment_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reply does not belong to the given commentd",
        )

    query_reaction = get_reaction_or_404(
        db=db, reaction_id=reaction_id, action="update"
    )

    if query_reaction.owner_id != check_auth.get("id"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this reaction",
        )

    query_reaction.reaction_type = update_reaction_request.reaction_type

    db.add(query_reaction)
    db.commit()

    return ReactionResponse(
        detail="Reaction type updated successfully",
        post_content=query_post.content,
        comment_content=query_comment.content,
        reply_content=query_reply.content,
        reaction_type=query_reaction.reaction_type,
    )


@router.delete(
    "/{post_id}/reaction/{reaction_id}",
    status_code=status.HTTP_200_OK,
)
async def undo_post_reaction(
    user: user_dependency,
    db: db_dependency,
    post_id: int = PathParam(gt=0),
    reaction_id: int = PathParam(gt=0),
):
    check_auth = is_user_authenticated(user)
    get_post_or_404(db=db, post_id=post_id)
    query_reactiom = get_reaction_or_404(db=db, reaction_id=reaction_id, action="undo")

    if query_reactiom.owner_id != check_auth.get("id"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to undo this reaction",
        )

    db.delete(query_reactiom)
    db.commit()

    return {"detail": "Reaction deleted successfully"}


@router.delete(
    "/{post_id}/comment/{comment_id}/reaction/{reaction_id}",
    status_code=status.HTTP_200_OK,
)
async def undo_comment_reaction(
    user: user_dependency,
    db: db_dependency,
    post_id: int = PathParam(gt=0),
    comment_id: int = PathParam(gt=0),
    reaction_id: int = PathParam(gt=0),
):
    check_auth = is_user_authenticated(user)
    get_post_or_404(db=db, post_id=post_id)
    query_comment = get_comment_or_404(db=db, comment_id=comment_id)

    if query_comment.post_id != post_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comment does not belong to the given post",
        )

    query_reaction = get_reaction_or_404(db=db, reaction_id=reaction_id, action="undo")

    if query_reaction.owner_id != check_auth.get("id"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to undo this reaction",
        )

    db.delete(query_reaction)
    db.commit()

    return {"detail": "Reaction deleted successfully"}


@router.delete(
    "/{post_id}/comment/{comment_id}/reply/{reply_id}/reaction/{reaction_id}",
    status_code=status.HTTP_200_OK,
)
async def undo_reply_reaction(
    user: user_dependency,
    db: db_dependency,
    post_id: int = PathParam(gt=0),
    comment_id: int = PathParam(gt=0),
    reply_id: int = PathParam(gt=0),
    reaction_id: int = PathParam(gt=0),
):
    check_auth = is_user_authenticated(user)
    get_post_or_404(db=db, post_id=post_id)
    query_comment = get_comment_or_404(db=db, comment_id=comment_id)

    if query_comment.post_id != post_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comment does not belong to the given post",
        )

    query_reply = get_reply_or_404(db=db, reply_id=reply_id)

    if query_reply.comment_id != comment_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reply does not belong to the given comment",
        )

    query_reaction = get_reaction_or_404(db=db, reaction_id=reaction_id, action="undo")

    if query_reaction.owner_id != check_auth.get("id"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to undo this reaction",
        )

    db.delete(query_reaction)
    db.commit()

    return {"detail": "Reaction deleted successfully"}
