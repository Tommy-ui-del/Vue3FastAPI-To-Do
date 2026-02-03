#基于 Pydantic Settings 管理多环境（开发 / 测试 / 生产）的全局配置，集中管理敏感信息和业务参数，支持从.env文件读取配置
#配置优先级：.env文件 > 类默认值 > 环境变量；
#多环境隔离：不同环境可覆写不同配置（如生产环境使用更长的令牌过期时间）；
#敏感信息保护：JWT 秘钥等参数不硬编码在代码，通过.env注入（.env已加入.gitignore）。

import os

from pydantic_settings import BaseSettings, SettingsConfigDict

# 基础配置类，所有环境共享
class GlobalSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    ENVIRONMENT: str = "development" # 默认环境为开发环境

    # authentication related
    # JWT认证相关配置（核心安全参数）
    JWT_ACCESS_SECRET_KEY: str = "9d9bc4d77ac3a6fce1869ec8222729d2"  # 访问令牌秘钥（默认值，实际从.env覆盖）
    JWT_REFRESH_SECRET_KEY: str = "fdc5635260b464a0b8e12835800c9016"  # 刷新令牌秘钥
    ENCRYPTION_ALGORITHM: str = "HS256"  # JWT加密算法
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # 访问令牌过期时间（分钟）
    NEW_ACCESS_TOKEN_EXPIRE_MINUTES: int = 120  # 刷新后新访问令牌过期时间
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 4  # 刷新令牌过期时间（4小时）
    NEW_REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 2  # 刷新后新刷新令牌过期时间（2天）

    # Database configuration 数据库配置（预留PostgreSQL，实际用SQLite）
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_HOST: str = "localhost"
    DB_PORT: str = "5432"
    DB_NAME: str = "postgres"
    # specify single database url
    DATABASE_URL: str | None = None

# 测试环境配置（继承基础配置，可覆写）
class TestSettings(GlobalSettings):
    pass


# 开发环境配置
class DevelopmentSettings(GlobalSettings):
    pass

# 生产环境配置（可覆写敏感参数，如秘钥从环境变量读取）
class ProductionSettings(GlobalSettings):
    pass

# 根据环境变量动态加载对应配置
def get_settings():
    env = os.environ.get("ENVIRONMENT", "development")
    if env == "test":
        return TestSettings()
    elif env == "development":
        return DevelopmentSettings()
    elif env == "production":
        return ProductionSettings()

    return GlobalSettings()

# 全局配置实例，其他文件直接导入使用
settings = get_settings()
