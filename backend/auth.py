#处理 JWT 令牌的生成、验证，校验当前登录用户的合法性，是系统的核心安全层
#令牌分层：访问令牌（短期）+ 刷新令牌（长期），平衡安全性和用户体验；
#依赖校验：get_current_user作为依赖，所有需要登录的接口自动校验令牌；
#异常处理：细分 JWT 错误类型（过期、无效），返回精准提示

from datetime import datetime, timedelta
from typing import Any

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config import settings
from backend.database import get_async_session
from backend.models import User
from backend.repositories.user_repo import UserRepository

# 定义OAuth2密码模式：指定令牌获取接口，用于Swagger文档自动识别
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="user/jwt/create/", scheme_name="JWT")  # important path to get token

# 获取当前登录用户（依赖函数，FastAPI注入）
async def get_current_user(
    access_token: str = Depends(oauth2_scheme),
    db_session: AsyncSession = Depends(get_async_session),
) -> User:
    user_repo = UserRepository(db_session)
    try:
        # 解码JWT令牌：验证签名和算法
        payload = jwt.decode(
            access_token,
            settings.JWT_ACCESS_SECRET_KEY,
            algorithms=[settings.ENCRYPTION_ALGORITHM],
        )
        # 提取令牌中的用户名/邮箱（subject）
        username: str = payload.get("sub")
        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except jwt.ExpiredSignatureError:   # 令牌过期
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.InvalidTokenError:  # 令牌无效（如篡改）
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Access Token")
    except jwt.PyJWTError: # 其他JWT错误
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 根据用户名/邮箱查询用户
    user: User | None = await user_repo.get_user_by_username_or_email(username)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # 校验用户是否被软删除
    if user.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is not active",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


# 访问令牌（Access Token）：短期有效，用于日常API请求认证 （访问令牌泄露后影响时间短）
def create_access_token(subject: str | Any, expires_delta: int = None) -> str:
     # 设置过期时间：默认使用配置中的30分钟，否则使用传入的过期时间
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    # 令牌载荷：包含过期时间和主题（用户名/邮箱） exp：过期时间戳sub：主题（用户标识）
    to_encode = {"exp": expires_delta, "sub": str(subject)}
    #使用不同的密钥（JWT_ACCESS_SECRET_KEY和JWT_REFRESH_SECRET_KEY）分别加密两种令牌
    encoded_jwt = jwt.encode(to_encode, settings.JWT_ACCESS_SECRET_KEY, settings.ENCRYPTION_ALGORITHM)
    return encoded_jwt

# 生成刷新令牌（Refresh Token）：长期有效，用于获取新的访问令牌 （用户无需频繁登录）
def create_refresh_token(subject: str | Any, expires_delta: int = None) -> str:
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)

    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.JWT_REFRESH_SECRET_KEY, settings.ENCRYPTION_ALGORITHM)
    return encoded_jwt
