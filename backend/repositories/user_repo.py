#封装用户相关的数据库 CRUD 操作，隔离业务逻辑与数据库操作，遵循「单一职责原则」
#凭据验证：authenticate_user封装用户名 / 密码校验，路由层只需调用；
#Google 登录：verify_google_token验证第三方令牌，create_user_from_google_credentials自动创建用户；
#密码安全：创建用户时自动加密密码，登录时验证哈希，全程不存储明文密码

import secrets
import string
from datetime import datetime, timezone

from fastapi import status
from httpx import AsyncClient, Response
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models import User
from backend.schemas import UserCreate
from backend.utils import get_hashed_password, verify_hashed_password

# 用户数据访问类：所有用户数据库操作集中在这里
class UserRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session   # 注入数据库会话

# 验证用户凭据（登录核心逻辑）
    async def authenticate_user(self, username: str, password: str):
         # 按用户名/邮箱查询用户
        user: User | None = await self.get_user_by_username_or_email(username)
        if not user:
            return False
        # check if passwords match - use hashed_password to check
         # 验证密码（明文 vs 哈希）
        if not verify_hashed_password(plain_password=password, hashed_password=user.password):
            return False
        return user

    # 按ID查询用户
    async def get_user_by_id(self, user_id: int) -> User:
        return await self.db_session.get(User, user_id)
    
    # 按用户名/邮箱查询用户（登录时支持两种方式）
    async def get_user_by_username_or_email(self, username: str) -> User:
        result = await self.db_session.execute(
            select(User).where(or_(User.username == username, User.email == username)),
        )
        return result.scalar_one_or_none()   # 返回单个结果或None

    # 按用户名查询用户（注册时校验唯一性）
    async def get_user_by_username(self, username: str) -> User:
        result = await self.db_session.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()
    
    # 按邮箱查询用户（注册时校验唯一性）
    async def get_user_by_email(self, email: str) -> User:
        result = await self.db_session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()


     # 创建用户（注册核心逻辑）
    async def create_user(self, user_schema: UserCreate) -> User:
         # 密码加密
        hashed_password = get_hashed_password(user_schema.password)
         # 创建User模型实例
        user = User(
            email=user_schema.email,
            name=user_schema.name,
            username=user_schema.username,
            password=hashed_password,
        )
         # 提交到数据库
        self.db_session.add(user)
        await self.db_session.commit()
        await self.db_session.refresh(user)  # 刷新实例，获取数据库生成的字段（如id）# 刷新实例，获取数据库生成的字段（如id）
        return user

    # 按ID删除用户（软删除/物理删除？这里是物理删除，可改为软删除）
    async def delete_user_by_id(self, user_id: int) -> bool:
        user = await self.db_session.get(User, user_id)
        if not user:
            return False

        await self.db_session.delete(user)
        await self.db_session.commit()
        return True

    # 从Google凭据创建用户（Google登录）
    async def create_user_from_google_credentials(self, **kwargs) -> User:
        # 生成随机密码（Google用户无需密码登录，仅用于入库）
        # generate random password for google user and hash it
        alphabet = string.ascii_letters + string.digits + string.punctuation
        password = "".join(secrets.choice(alphabet) for _ in range(20))
        hashed_password = get_hashed_password(password)
        # 创建用户（用Google邮箱作为用户名）
        user = User(
            username=kwargs.get("email"),  # Using Google email as username
            email=kwargs.get("email"),
            name=f"{kwargs.get('given_name')} {kwargs.get('family_name')}",
            password=hashed_password,
        )
        self.db_session.add(user)
        await self.db_session.commit()

        return user

    # https://stackoverflow.com/questions/16501895/how-do-i-get-user-profile-using-google-access-token
    # Verify the auth token received by client after google signin
    # 验证Google令牌，获取用户信息
    async def verify_google_token(self, google_access_token: str) -> dict[str, str] | None:
        # 调用Google API验证令牌
        google_url = f"https://www.googleapis.com/oauth2/v3/userinfo?access_token={google_access_token}"

        async with AsyncClient() as client:
            response: Response = await client.get(google_url)
            if response.status_code == status.HTTP_200_OK:
                user_info: dict = response.json()
            else:
                return None
        # 校验返回的用户信息是否包含必要字段
        # check that user_info contains email, given and family name
        if {"email", "given_name", "family_name"}.issubset(set(user_info)):
            return user_info

        return None

    # 更新用户最后登录时间
    async def update_user_last_login(self, user: User) -> None:
        user.last_login = datetime.now(timezone.utc)
        await self.db_session.commit()
