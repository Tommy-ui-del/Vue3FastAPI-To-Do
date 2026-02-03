#定义用户注册、删除的 HTTP 接口，处理请求参数校验和响应返回
#唯一性校验：注册时校验用户名和邮箱，避免重复；
#响应模型：response_model=UserDisplay 自动隐藏密码，仅返回安全字段；
#状态码：使用标准 HTTP 状态码（409 冲突、404 未找到、204 无内容）

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_async_session
from backend.repositories.user_repo import UserRepository
from backend.schemas import UserCreate, UserDisplay

# 创建路由实例：前缀/users，标签user（Swagger文档分组）
router = APIRouter(prefix="/users", tags=["user"])

# 注册用户接口：POST /users/register/
@router.post("/register/", response_model=UserDisplay)
async def add_user(user_schema: UserCreate, db_session: AsyncSession = Depends(get_async_session)):
    user_repo = UserRepository(db_session)
    
    # 校验用户名是否已存在
    user = await user_repo.get_user_by_username(user_schema.username)
    if user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists")
    
    # 校验邮箱是否已存在
    # checking if email already exists
    user = await user_repo.get_user_by_email(user_schema.email)
    if user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")
    
    # 创建用户并返回（自动序列化为UserDisplay）
    return await user_repo.create_user(user_schema)


# 删除用户接口：DELETE /users/{user_id}/
@router.delete("/{user_id}/")
async def delete_user_by_id(user_id: int, db_session: AsyncSession = Depends(get_async_session)):
    user_repo = UserRepository(db_session)
     # 校验用户是否存在
    if not await user_repo.delete_user_by_id(user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} is not found",
        )
    # 返回204无内容（成功删除）
    return Response(status_code=status.HTTP_204_NO_CONTENT)
