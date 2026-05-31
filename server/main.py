import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from routes.analyze import router as analyze_router
from routes.user import router as user_router
from routes.gallery import router as gallery_router
from models.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs("static", exist_ok=True)
    await init_db()
    yield


app = FastAPI(title="光影参谋 API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(analyze_router)
app.include_router(user_router)
app.include_router(gallery_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
