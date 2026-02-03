#封装任务相关的数据库 CRUD 操作，关联用户权限（仅操作当前用户的任务）
#权限校验：所有任务操作都关联user_id，确保用户只能操作自己的任务；
#批量更新：bulk_update_priorities使用 SQLAlchemy 的批量更新，减少数据库交互次数；
#排序：查询任务时按priority升序，保证优先级高的任务排在前面

from datetime import date

from fastapi import HTTPException, status
from sqlalchemy import and_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models import Task, User
from backend.schemas import CreateTaskSchema, UpdateTaskSchema


class TaskRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    # 按ID查询任务
    async def get_task_by_id(self, task_id: int) -> Task | None:
        task = await self.db_session.get(Task, task_id)
        return task

     # 按日期+用户ID查询任务（按优先级升序排序）
    async def get_tasks_by_date(self, selected_date: date, current_user: User) -> list[Task]:
        statement = (
            select(Task)
            .where(and_(Task.posted_at == selected_date, Task.user_id == current_user.id))
            .order_by(Task.priority.asc())
        )
        result = await self.db_session.execute(statement)
        tasks = result.scalars().all()
        return tasks

    # 创建任务（关联当前用户）
    async def create_task(self, create_task_schema: CreateTaskSchema, current_user: User) -> Task:
        task = Task(
            priority=create_task_schema.priority,
            text=create_task_schema.text,
            user_id=current_user.id,   # 绑定当前用户
            posted_at=create_task_schema.posted_at,
        )

        self.db_session.add(task)
        await self.db_session.commit()
        await self.db_session.refresh(task)
        return task


    # 删除任务（校验任务归属）
    async def delete_task(self, task_id: int, user_id: int) -> bool:
        # 仅删除当前用户的任务
        result = await self.db_session.execute(select(Task).where(and_(Task.id == task_id, Task.user_id == user_id)))
        task = result.scalar_one_or_none()
        if not task:
            return False

        await self.db_session.delete(task)
        await self.db_session.commit()
        return True

    # 更新任务（部分字段更新）
    async def update_task(self, task: Task, new_task: UpdateTaskSchema) -> Task:
        if new_task.text:
            task.text = new_task.text
        if new_task.priority:
            task.priority = new_task.priority
        if new_task.completed is not None:
            task.completed = new_task.completed

        await self.db_session.commit()
        await self.db_session.refresh(task)

        return task

    # 批量更新任务优先级（核心逻辑）
    async def bulk_update_priorities(self, priorities: dict[int, int], current_user: User):
        """
        priorities hold id:new_priority key-pair dictonary
        """
        # 校验所有任务ID是否属于当前用户
        # make sure all tasks (ids) belong to the current user
        result = await self.db_session.execute(
            select(Task.id).where(and_(Task.user_id == current_user.id, Task.id.in_(priorities))),
        )
        task_ids = result.scalars().all()  # returns list of ids
        # 若传入的ID数与用户的任务ID数不匹配，抛出异常
        # task ids provided doesn't match task ids found for user
        if not len(priorities) == len(task_ids):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Provided ids doesn't match tasks of the user [{priorities}]",
            )

        # unpack into {id: key, priority:value}   构造更新数据：[{id:1, priority:2}, ...]
        priorities_to_update = [{"id": task_id, "priority": priority} for task_id, priority in priorities.items()]
        # 批量更新（高效，一次SQL操作）
        await self.db_session.execute(update(Task), priorities_to_update)
        await self.db_session.commit()
