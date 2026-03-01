import logging
from datetime import date, datetime 

from fastapi import HTTPException
from sqlalchemy import select, func, update, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.user import User
from ..models.task import Task
from ..schema_pydantic.task import TaskCreate, TaskPatch, TaskRead, TaskListResponse
from ..schema_pydantic.stats import StatsResponse
from ..errors import AppError, ConflictError, NotFoundError, ValidationError


logger = logging.getLogger("app.db")

async def read_tasks_list(
        db: AsyncSession, 
        q: str | None = None,
        status: str | None = None,
        user_id: int | None = None,
        due_from: date | None = None,
        due_to: date | None = None,
        sort: str | None = None,
        order: str = "desc",
        limit: int = 50, 
        offset: int = 0
) -> TaskListResponse:
    
    stmt = select(Task)
    count = select(func.count(Task.id)).select_from(Task)
    
    if q:
        stmt = stmt.where(Task.title.ilike(f"%{q}%"))
        count = count.where(Task.title.ilike(f"%{q}%"))


    status_list = ["todo", "doing", "done"]

    if status:

        if status not in status_list:
            raise ValidationError(message= f"not allowed status : {status}")

        stmt = stmt.where(Task.status == status)
        count = count.where(Task.status == status)

    if user_id is not None:
        stmt = stmt.where(Task.user_id == user_id)
        count = count.where(Task.user_id == user_id)
    
    if due_from:
        stmt = stmt.where(Task.due_date >= due_from)
        count = count.where(Task.due_date >= due_from)

    if due_to:
        stmt = stmt.where(Task.due_date <= due_to)
        count = count.where(Task.due_date <= due_to)
    
    sort_map = {
        "id" : Task.id,
        "user_id" : Task.user_id,
        "due_date" : Task.due_date,
        "priority" : Task.priority,
        "created_at" : Task.created_at,
        "updated_at" : Task.updated_at
    }
    
    if sort is not None:
        if sort_map.get(sort) is None:
            raise ValidationError(message= f"not allowed sort : {sort} ")

    sort_col = sort_map.get(sort or "id")


    if order not in ["desc", "asc"]:
        raise ValidationError(message= f"not allowed order : {order}")

    if order == "desc":
        stmt = stmt.order_by(sort_col.desc())
    else :
        stmt = stmt.order_by(sort_col.asc())


    stmt = stmt.limit(limit).offset(offset)
        
    result = await db.execute(stmt)
    total = await db.scalar(count) 


    return  TaskListResponse(items= result.scalars().all(), 
                             total= total,
                             limit= limit,
                             offset= offset
                             )




async def read_task(db: AsyncSession, id: int):
    stmt = select(Task).where(Task.id == id)
    result = await db.execute(stmt)
    
    return result.scalar_one_or_none()



async def create_task(db: AsyncSession, data: TaskCreate):

    res = await db.execute(select(User).where(User.id == data.user_id))
    if res.scalar_one_or_none() is None:
        raise ValidationError(message= "user_id not found")

    task = Task(
        user_id = data.user_id,
        title = data.title,
        description = data.description,
        status = data.status,
        priority = data.priority,
        due_date = data.due_date
    )

    db.add(task)
    # try:
    await db.commit()
    # except IntegrityError as e:
    #     await db.rollback()
    #     orig = getattr(e, "orig", None)
    #     logger.exception(
    #         "DB IntegrityError sqlstate=%s constraint=%s",
    #         getattr(orig, "pgcode", None),
    #         getattr(getattr(orig, "diag", None), "constraint_name", None),
    #     )
    #     raise

    await db.refresh(task)
    return task



async def update_task(db: AsyncSession, task_id: int, patch: TaskPatch) -> TaskRead:

    payload = patch.model_dump(exclude_unset=True, exclude_none=True)
    print(f"payload : {payload}")
    if not payload:
        raise ValidationError("no fields to update")

    #print(f"payload : {paypload}")

    stmt = (update(Task)
            .where(Task.id == task_id)
            .values(**payload, updated_at = func.now() )
            .returning(Task)
            )
    
    result = await db.execute(stmt)
    updated = result.scalar_one_or_none()
    if updated is None:
        await db.rollback()
        raise NotFoundError(message= "task not found")
    
    await db.commit()
    return updated
    
    

async def delete_task(db: AsyncSession, task_id : int) :
    
    stmt = delete(Task).where(Task.id == task_id).returning(Task.id)
    result = await db.execute(stmt)

    #print(f"result rowcount : {result.rowcount}")

    deleted_task = result.fetchone()

    #print(f"deleted_id : {deleted_id}")


    if deleted_task is None:
        await db.rollback()
        raise NotFoundError(message= "task not found")


    
    # deleted_id = deleted_task.id

    # print(f"deleted_id : {deleted_id}")
    await db.commit()

    # return deleted_id



async def stats_tasks_by_status(db: AsyncSession) -> StatsResponse:


    stats = select(Task.status, func.count()).select_from(Task).group_by(Task.status)
    rows = (await db.execute(stats)).all()

    counts = {"todo" : 0, "doing" : 0, "done" : 0}
    
    for status, cnt in rows:
        counts[status] = cnt

    return StatsResponse(todo= counts["todo"], doing= counts["doing"], done= counts["done"])