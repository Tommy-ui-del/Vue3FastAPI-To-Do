#作用：这是 FastAPI 应用的入口。它负责创建应用实例 (app = FastAPI())，挂载路由，配置中间件（如 CORS 跨域设置），并启动服务器。
#配合：它将 routers（路由）引入，告诉服务器当访问 /todos 时该去哪里找处理函数

#初始化 FastAPI 应用，注册路由，配置跨域，启动时创建数据库表

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database import engine
from backend.models import metadata
from backend.routers import authentication, task, user


# 应用生命周期钩子：启动时创建表，关闭时无操作
@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()  # 启动时创建所有表，无需手动执行 SQL
    yield  # 应用运行中
    # 关闭时可添加清理逻辑（如关闭数据库连接）


# 创建FastAPI实例，绑定生命周期钩子
app = FastAPI(lifespan=lifespan)

# 注册路由：用户、任务、认证
app.include_router(user.router)
app.include_router(task.router)
app.include_router(authentication.router)

# 配置跨域中间件（允许前端访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],   # 前端开发服务器地址
    allow_credentials=True,   # 允许携带Cookie（如令牌）
    allow_methods=["*"],  # 允许所有HTTP方法（GET/POST/PATCH/DELETE）
    allow_headers=["*"],    # 允许所有请求头
)

# 创建数据库表（基于models.py的metadata）
async def create_tables() -> None:
    metadata.bind = engine
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
