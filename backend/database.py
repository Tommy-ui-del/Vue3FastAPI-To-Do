#配置异步 SQLite 数据库连接，提供 FastAPI 依赖注入的数据库会话，管理连接生命周期
#异步引擎：使用aiosqlite驱动，适配 FastAPI 的异步特性；
#会话管理：通过生成器自动释放会话，避免连接泄露；
#路径处理：使用Path保证跨平台兼容性（Windows/Linux 路径格式统一）

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool
from pathlib import Path

# 获取backend目录路径（保证数据库文件路径统一）
BACKEND_DIR = Path(__file__).parent
# 拼接SQLite数据库文件路径（存储在backend目录下的sql_app.db）
DATABASE_URL = f"sqlite+aiosqlite:///{BACKEND_DIR / 'sql_app.db'}"

# 创建异步引擎（适配SQLite）
engine = create_async_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite必需参数：允许异步线程访问
    poolclass=NullPool,  # 避免SQLite连接池问题
    echo=True  # 可选：显示SQL日志，方便调试
)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

# 数据库会话依赖函数（FastAPI注入用）
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session