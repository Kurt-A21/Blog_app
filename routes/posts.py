from fastapi import APIRouter, HTTPException, Path
from starlette import status
from database import db_dependency
from pydantic import BaseModel, Field
from models import Posts

router = APIRouter()
