from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routes.analyze import router as analyze_router
from routes.scene import router as scene_router
from routes.user import router as user_router
from routes.gallery import router as gallery_router
from models.database import init_db

app = FastAPI(title="光影参谋 API")

# 静态文件（缩略图）
app.mount("/static", StaticFiles(directory="static"), name="static")

# 注册路由
app.include_router(analyze_router)
app.include_router(scene_router)
app.include_router(user_router)
app.include_router(gallery_router)


@app.on_event("startup")
async def startup():
    await init_db()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
