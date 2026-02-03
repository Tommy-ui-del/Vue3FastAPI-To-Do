#定义前后端数据交互的「契约」，校验请求参数合法性，序列化响应数据（隐藏敏感字段）
#部分更新：UpdateTaskSchema所有字段设为可选，支持 PATCH 请求的部分更新；
#序列化配置：from_attributes = True 允许直接将 ORM 模型（如 Task 实例）转为响应数据；
#敏感字段隐藏：UserDisplay不包含 password，避免密码泄露


from datetime import date, datetime

from pydantic import BaseModel

# 刷新令牌请求模型：校验refresh_token参数
class RefreshTokenSchema(BaseModel):
    refresh_token: str


# 创建任务请求模型：校验任务创建的必填参数
class CreateTaskSchema(BaseModel):
    text: str     # 任务内容（必填）
    priority: int  # 优先级（必填）
    posted_at: date  # 关联日期（必填）


# 按日期查询任务请求模型：校验日期参数
class TasksByDateSchema(BaseModel):
    date: date


# 更新任务请求模型：支持部分字段更新（所有字段可选）
class UpdateTaskSchema(BaseModel):
    priority: int | None = None
    text: str | None = None
    completed: bool | None = None


# 批量更新任务优先级请求模型
class UpdateTaskPrioritiesSchema(BaseModel):
    """id:priority dictionary to update"""

    priorities: dict[int, int]  # 键：任务ID，值：新优先级


# 任务响应模型：序列化任务数据返回前端
class DisplayTaskSchema(BaseModel):
    id: int
    priority: int
    text: str
    completed: bool
    created_at: datetime
     # 配置：支持从ORM模型（如Task）直接转换
    class Config:
        from_attributes = True


# 内部用户模型（未直接使用，预留）
class User(BaseModel):
    user_id: str
    name: str
    email: str
    username: str
    password: str
    created_at: datetime


# 创建用户请求模型：注册时校验参数
class UserCreate(BaseModel):
    name: str
    email: str
    username: str
    password: str  # 明文密码（后端加密后入库）


# 用户响应模型：隐藏密码等敏感字段，仅返回安全信息
class UserDisplay(BaseModel):
    username: str
    email: str
    created_at: datetime


# Google登录请求模型：校验Google access_token
class GoogleLoginSchema(BaseModel):
    access_token: str
