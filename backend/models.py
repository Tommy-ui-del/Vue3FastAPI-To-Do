#作用：定义数据库表的结构。例如，定义一个 Todo 类，包含 id、title、completed 等字段，对应数据库中的表。
#配合：ORM（对象关系映射）工具会根据这个文件自动创建或操作数据库表

#定义数据库表结构，实现表关联、通用字段复用，是数据库操作的核心映射层
#软删除：is_deleted字段替代物理删除，便于数据恢复和审计；
#表关联：User和Task的一对多关系，通过user_id外键实现；
#通用字段：BaseModel减少重复代码，所有表共享创建 / 更新时间

#Mapped[T]：是 SQLAlchemy 提供的泛型类型，用来声明模型属性对应的 Python 类型（比如 int、str、uuid.UUID）。
#它会告诉 IDE 和类型检查工具这个属性在 Python 代码中的类型，同时也会映射到对应的数据库类型。
#mapped_column(...)：用来定义数据库列的具体配置（比如主键、唯一约束、默认值、数据类型等），替代了旧版的 Column(...)

import uuid
from datetime import date, datetime

#uuid根据当前电脑的各种状态生成不同的字符串来保证唯一性
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
    #SQLAlchemy 查询返回的是模型对象（比如 User 实例），而不是字典，前端需要 JSON 格式数据
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
    #作用（ORM 层面）
    #这是ORM 级别的正向访问方式，让 User 实例可以直接通过 user.tasks 获取该用户关联的所有 Task 实例，无需手动编写 JOIN 查询
    #没有正向关联的后果要获取用户的任务，必须手动写 WHERE 查询
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
    #作用（数据库层面）
    #这是数据库级别的约束，它强制 task 表的 user_id 字段的值，必须对应 user 表中存在的 id（即一个任务必须属于一个真实存在的用户）。
    #防止出现 “任务关联了不存在的用户” 这种脏数据，保证了数据的完整性和一致性。
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    
    # 反向关联：任务归属的用户
    #这是ORM 级别的反向访问方式，让 Task 实例可以直接通过 task.user 获取该任务所属的 User 实例，同样无需手动查询
    #没有反向关联的后果要获取任务所属的用户，必须手动写 WHERE 查询：
    user: Mapped["User"] = relationship(back_populates="tasks")



#back_populates 用来建立双向关联的映射，让 User.tasks 和 Task.user 互相指向对方，确保两边的关联是同步的。
#比如：当你给 user.tasks 添加一个 Task 实例时，该 Task 的 user_id 会自动更新为该 user 的 id，反之亦然。
#没有 back_populates，双向关联会失效，需要手动维护两边的关联，容易出现数据不一致的情况。
