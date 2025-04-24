from fastapi import FastAPI
from db import engine, Base, models
from routers import router
import uvicorn

app = FastAPI(title="Social Media App")

models.Base.metadata.create_all(bind=engine)

app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
