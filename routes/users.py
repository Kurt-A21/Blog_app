from fastapi import APIRouter, HTTPException, Path
from starlette import status
from database import db_dependency
from schemes import UsersRequest
from models import Users

router = APIRouter()
