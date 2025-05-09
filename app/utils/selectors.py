from starlette import status
from fastapi import HTTPException
from app.db.models import *


def is_user_authenticated(user):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )
    return user

def is_user_admin(user):
    if user is None or user.get("user_role") != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed"
        )

def get_user(db, user):
    query_user = db.query(Users).filter(Users.id == user.get("id")).first()
    return query_user

def get_user_by_id_or_404(db, user_id):
    query_user = db.query(Users).filter(Users.id == user_id).first()
    if query_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return query_user


def get_post_or_404(db, post_id: int):
    query_post = db.query(Posts).filter(Posts.id == post_id).first()

    if query_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    return query_post


def get_comment_or_404(db, comment_id: int):
    query_comment = db.query(Comments).filter(Comments.id == comment_id).first()

    if query_comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
        )
    return query_comment


def get_reply_or_404(db, reply_id: int):
    query_reply = db.query(CommentReply).filter(CommentReply.id == reply_id).first()

    if query_reply is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Reply not found"
        )
    return query_reply


def get_reaction_or_404(db, reaction_id: int, action: str):
    query_reaction = db.query(Reactions).filter(Reactions.id == reaction_id).first()

    if not query_reaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Reaction to {action} not found"
        )


def get_existing_reaction(db, user_id, post_id=None, comment_id=None, reply_id=None):
    if post_id:
        return (
            db.query(Reactions)
            .filter(
                Reactions.owner_id == user_id,
                Reactions.post_id == post_id,
                Reactions.comment_id == None,
                Reactions.reply_id == None,
            )
            .first()
        )
    elif comment_id:
        return (
            db.query(Reactions)
            .filter(
                Reactions.owner_id == user_id,
                Reactions.comment_id == comment_id,
                Reactions.post_id == None,
                Reactions.reply_id == None,
            )
            .first()
        )
    elif reply_id:
        return (
            db.query(Reactions)
            .filter(
                Reactions.owner_id == user_id,
                Reactions.reply_id == reply_id,
                Reactions.post_id == None,
                Reactions.comment_id == None,
            )
            .first()
        )
    return None
