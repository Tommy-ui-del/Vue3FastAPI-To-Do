#定义任务的增删改查、批量更新优先级的 HTTP 接口，所有接口需登录验证
#登录校验：所有接口依赖get_current_user，未登录无法访问；
#权限二次校验：更新 / 删除任务时，额外校验task.user_id == current_user.id，防止越权；
#响应模型：response_model=list[DisplayTaskSchema] 自动序列化任务列表，保证数据格式统一

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.auth import get_current_user
from backend.database import get_async_session
from backend.models import User
from backend.repositories.task_repo import TaskRepository
from backend.schemas import (
    CreateTaskSchema,
    DisplayTaskSchema,
    UpdateTaskPrioritiesSchema,
    UpdateTaskSchema,
)

router = APIRouter(prefix="/task", tags=["task"])

# 创建任务接口：POST /task/
@router.post("/", response_model=DisplayTaskSchema)
async def add_task(
    create_task_schema: CreateTaskSchema,
    db_session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),  # 登录校验
):
    task_repo = TaskRepository(db_session)
    task = await task_repo.create_task(create_task_schema, current_user)
    return task


# 按日期查询任务接口：GET /task/
@router.get("/", response_model=list[DisplayTaskSchema])
async def get_tasks(
    selected_date: date,
    db_session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    task_repo = TaskRepository(db_session)
    tasks = await task_repo.get_tasks_by_date(selected_date, current_user)
    return tasks


# 批量更新优先级接口：PATCH /task/update-order/
@router.patch("/update-order/")
async def update_tasks_order(
    priorities_schema: UpdateTaskPrioritiesSchema,
    db_session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    task_repo = TaskRepository(db_session)

    await task_repo.bulk_update_priorities(priorities_schema.priorities, current_user)

    return "Priorities have been updated"


# 更新任务接口：PATCH /task/{task_id}/
@router.patch("/{task_id}/", response_model=DisplayTaskSchema)
async def update_task(
    task_id: int,
    update_task_schema: UpdateTaskSchema,
    db_session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    task_repo = TaskRepository(db_session)
    # 校验任务是否存在
    task = await task_repo.get_task_by_id(task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )
     # 校验任务归属
    if not task.user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Task does not belong to the current user",
        )
     # 更新任务
    updated_task = await task_repo.update_task(task, new_task=update_task_schema)

    return updated_task


# 删除任务接口：DELETE /task/{task_id}/
@router.delete("/{task_id}/")
async def delete_task_by_id(
    task_id: str,
    db_session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    task_repo = TaskRepository(db_session)
     # 校验任务是否存在且归属当前用户
    if not await task_repo.delete_task(task_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"task with id {task_id} not found",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
