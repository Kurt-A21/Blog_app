from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .db import engine, Base
from .routers import router
import uvicorn
from pathlib import Path

app = FastAPI(title="Social Media App")

static_dir = Path(__file__).resolve().parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")

Base.metadata.create_all(bind=engine)

app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
