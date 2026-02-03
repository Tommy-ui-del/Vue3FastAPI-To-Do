#定义数据库表结构，实现表关联、通用字段复用，是数据库操作的核心映射层
#软删除：is_deleted字段替代物理删除，便于数据恢复和审计；
#表关联：User和Task的一对多关系，通过user_id外键实现；
#通用字段：BaseModel减少重复代码，所有表共享创建 / 更新时间

import uuid
from datetime import date, datetime

from sqlalchemy import (
    UUID,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    MetaData,
    String,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

metadata = MetaData()  # 元数据：管理所有表结构，用于创建表

# 抽象基类：封装通用字段，所有表继承
class BaseModel(DeclarativeBase):
    __abstract__ = True # 标记为抽象类，不生成实际表
    metadata = metadata

    # 通用字段：创建时间（数据库自动生成）
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    # 通用字段：更新时间（创建时生成，更新时自动刷新）
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
    # 通用字段：软删除标记（避免物理删除数据）
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)


    # 模型转字典：方便序列化返回前端
    def to_dict(self):
        return {field.name: getattr(self, field.name) for field in self.__table__.c}


# 用户表
class User(BaseModel):
    __tablename__ = "user"  # 数据库表名

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)  # 主键
    guid: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), unique=True, default=uuid.uuid4)  # 唯一标识（替代主键暴露）
    password: Mapped[str] = mapped_column(String(128)) # 哈希后的密码
    username: Mapped[str] = mapped_column(String(150), unique=True)  # 用户名（唯一）
    name: Mapped[str] = mapped_column(String(150), default="")   # 真实姓名
    email: Mapped[str] = mapped_column(String(254), unique=True)   # 邮箱（唯一）
    last_login: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)  # 最后登录时间
    # 一对多关联：一个用户对应多个任务
    tasks: Mapped[list["Task"]] = relationship(back_populates="user")


# 任务表
class Task(BaseModel):
    __tablename__ = "task"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    guid: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), unique=True, default=uuid.uuid4)
    priority: Mapped[int] = mapped_column(Integer)  # 任务优先级（数字越小优先级越高）
    text: Mapped[str] = mapped_column(String)
    completed: Mapped[bool] = mapped_column(Boolean, default=False) # 完成状态
    posted_at: Mapped[date] = mapped_column(Date)  # 任务关联日期
    # 外键：关联用户表主键
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
     # 反向关联：任务归属的用户
    user: Mapped["User"] = relationship(back_populates="tasks")
