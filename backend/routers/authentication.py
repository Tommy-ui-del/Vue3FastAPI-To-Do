#定义登录（密码 / Google）、刷新令牌的 HTTP 接口，处理认证逻辑并返回令牌
#兼容 Swagger：OAuth2PasswordRequestForm 适配 Swagger 的登录表单，token_type: Bearer 符合 OAuth2 规范；
#Google 登录：自动创建用户（无需手动注册），提升用户体验；
#令牌刷新：生成新的访问 / 刷新令牌，延长登录态，避免频繁登录

from datetime import timedelta
from typing import TYPE_CHECKING

import jwt
from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from backend.auth import create_access_token, create_refresh_token
from backend.config import settings
from backend.database import get_async_session
from backend.repositories.user_repo import UserRepository
from backend.schemas import GoogleLoginSchema, RefreshTokenSchema

# 类型检查：仅在类型检查时导入，避免循环导入
if TYPE_CHECKING:
    from backend.models import User


router = APIRouter(prefix="/user", tags=["user"])

# 用户名密码登录接口：POST /user/jwt/create/
@router.post("/jwt/create/")
async def login(
    db_session: AsyncSession = Depends(get_async_session),
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    """
    ## LogIn a User
    This requires the following fields:
    ```
        username: str
        password: str

    and returns a token pair 'access' and 'refresh' tokens
    ```
    LogIn a User: 需要username和password，返回access/refresh令牌
    """
    user_repo = UserRepository(db_session)
     # 验证用户凭据
    user = await user_repo.authenticate_user(username=form_data.username, password=form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # 生成令牌
    access_token = create_access_token(subject=user.username)
    refresh_token = create_refresh_token(subject=user.username)
      # 构造响应（兼容Swagger文档）
    response = {
        "access_token": access_token,  # must have as access_token to avoid errors with Swagger
        "refresh_token": refresh_token,
        "token_type": "Bearer",  # need this to avoid errors with Swagger
    }

    return jsonable_encoder(response)


# Google登录接口：POST /user/google-login/
@router.post(
    "/google-login/",
    summary="Login with Google oauth2",
)
async def login_with_google(
    response: Response,
    google_login_schema: GoogleLoginSchema,
    db_session: AsyncSession = Depends(get_async_session),
):
    # 验证Google令牌
    user_repo = UserRepository(db_session)
    google_access_token: str = google_login_schema.access_token

    user_info: dict[str, str] | None = await user_repo.verify_google_token(google_access_token=google_access_token)

    if not user_info:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not verify Google credentials")
    # 处理邮箱（转小写，保证唯一性）
    # email field is case insensitive, db holds only lower case representation
    email: str = user_info.get("email", "").lower()
    if not email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email was not provided")
    # 检查用户是否存在：不存在则创建，存在则更新最后登录时间
    if not (user := await user_repo.get_user_by_email(email=email)):
        user: User = await user_repo.create_user_from_google_credentials(**user_info)

    else:
        # update last login for existing user
        await user_repo.update_user_last_login(user=user)
    # 生成令牌
    access_token: str = create_access_token(email)
    refresh_token: str = create_refresh_token(email)

    response = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer",
    }

    return jsonable_encoder(response)

# 刷新令牌接口：POST /user/jwt/refresh/
@router.post("/jwt/refresh/", summary="Create new access token for user")
async def get_new_access_token_from_refresh_token(
    refresh_token_schema: RefreshTokenSchema,
    db_session: AsyncSession = Depends(get_async_session),
):
    user_repo = UserRepository(db_session)

    try:
        # 解码刷新令牌
        payload = jwt.decode(
            refresh_token_schema.refresh_token,
            settings.JWT_REFRESH_SECRET_KEY,
            algorithms=[settings.ENCRYPTION_ALGORITHM],
        )
        username: str = payload.get("sub")
        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except jwt.ExpiredSignatureError:   # 令牌过期
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.InvalidTokenError:   # 令牌无效
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Access Token")
    except jwt.PyJWTError:    # 其他JWT错误
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
     # 校验用户是否存在且未被删除
    user: User | None = await user_repo.get_user_by_username_or_email(username)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is not active",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # 生成新的访问令牌和刷新令牌
    new_access_token = create_access_token(
        username, expires_delta=timedelta(minutes=settings.NEW_ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    new_refresh_token = create_refresh_token(
        username, expires_delta=timedelta(minutes=settings.NEW_REFRESH_TOKEN_EXPIRE_MINUTES)
    )

    return {"access_token": new_access_token, "refresh_token": new_refresh_token}
