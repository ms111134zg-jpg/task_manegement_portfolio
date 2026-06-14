#####=====  import =====#####
##== 標準ライブラリ ==##
from datetime import date

##== 外部ライブラリ ==##
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

##== ローカルモジュール ==##
from ..db import get_db
from ..crud.task import read_tasks_list, read_task, create_task,  update_task, delete_task, stats_tasks_by_status
from ..schema.task import TaskCreate, TaskPatch, TaskRead, TaskListResponse
from ..schema.stats import StatsResponse
from ..errors import NotFoundError



#####=====  APIRouter定義  =====#####
router = APIRouter(prefix="/api/tasks", tags=["tasks"])



#####=====  tasks router  =====#####
@router.get("", response_model=TaskListResponse)
async def get_tasks(
    q: str | None = Query(None, max_length=50),
    status: str | None = Query(None),
    user_id: int | None = Query(None, ge = 1),
    due_from: date | None = Query(None),
    due_to: date | None = Query(None),
    sort: str | None = Query(None),
    order: str = Query("desc"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    tasks = await read_tasks_list(
        db=db, 
        q=q,
        status=status,
        user_id=user_id,
        due_from=due_from,
        due_to=due_to,
        sort=sort,
        order=order,
        limit=limit, 
        offset=offset
        )
    
    return tasks


@router.get("/{id}", response_model=TaskRead)
async def get_task(
    id: int,
    db: AsyncSession = Depends(get_db)
):
    
    task = await read_task(db=db, id=id)
    if task is None:
        raise  NotFoundError()   #HTTPException(status_code=404, detail="task not found")
    
    return task


@router.post("", response_model=TaskRead)
async def post_task(
    payload: TaskCreate,
    db: AsyncSession = Depends(get_db)
):

    task = await create_task(db=db, data=payload)


    return task


@router.patch("/{task_id}", response_model= TaskRead)
async def patch_tasks( task_id: int, payload : TaskPatch,  db: AsyncSession = Depends(get_db) ) :
    
    task = await update_task(db= db, task_id= task_id, patch= payload)

    return task


@router.delete("{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task_api(task_id : int, db: AsyncSession = Depends(get_db)) :


    result = await delete_task(db = db, task_id = task_id)
    



@router.get("/stats/tasks-by-status", response_model = StatsResponse)
async def get_tasks_by_status(db: AsyncSession = Depends(get_db)):


    stats = await stats_tasks_by_status(db)
    

    return stats