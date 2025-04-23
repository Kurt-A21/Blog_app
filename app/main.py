from fastapi import FastAPI
from db import engine
import db as models
from routers import router

app = FastAPI(title="Social Media App")

models.Base.metadata.create_all(bind=engine)

app.include_router(router)
