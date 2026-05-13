from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routes.analyze import router as analyze_router
from routes.user import router as user_router
from routes.gallery import router as gallery_router
from models.database import init_db


# ==============================================
# 【新标准】生命周期管理器（替代废弃的 on_event）
# ==============================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 项目启动时执行：初始化数据库（建表、连接）
    await init_db()
    # 服务运行中
    yield
    # 项目关闭时执行（如需释放数据库连接，可在这里写）


# ==============================================
# 创建 FastAPI 应用，注册生命周期
# ==============================================
app = FastAPI(
    title="光影参谋 API",
    lifespan=lifespan  # 注册新的生命周期
)

# 静态文件服务（缩略图存放）
app.mount("/static", StaticFiles(directory="static"), name="static")

# 注册所有业务路由
app.include_router(analyze_router)
app.include_router(user_router)
app.include_router(gallery_router)

# 启动服务
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
