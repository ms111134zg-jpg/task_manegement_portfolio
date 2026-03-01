#####====== Import Lib =====#####
import io
import logging
from datetime import date, datetime
from dataclasses import dataclass


from fastapi import FastAPI, Depends, Query, Form, Response, Request, status
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from .db import get_db
from .crud.user import read_users_list, read_user, create_user
from .crud.task import read_tasks_list, read_task, create_task, stats_tasks_by_status, update_task, delete_task
from .schema_pydantic.user import UserRead, UserCreate
from .schema_pydantic.task import TaskCreate, TaskPatch, TaskRead, TaskDelete, TaskListResponse
from .schema_pydantic.stats import StatsResponse
from .models import Task, User
from .errors import AppError, ConflictError, NotFoundError, ValidationError

app = FastAPI()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("app.db")

#####====== CORS =====#####

#####====== DATACLASS =====#####

#####====== API =====#####


##== 疎通チェック ==##
@app.get("/health")
def health_check():
    return {"status": "running"}

@app.get("/health/db")
async def health_db(db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT 1;"))
    return {"ok":True, "value": result.scalar_one()}



##== 例外ハンドラ ==##
@app.exception_handler(AppError)
async def app_error_handler(request : Request, exc : AppError):

    status_map = {
        "not_found" : 404, 
        "conflict" : 409,
        "validation_error" : 400,
        "app_error" : 400
    }
    status = status_map.get(exc.code, 400)

    logger.warning(
        "app_error",
        extra={"code": exc.code, "status": status, "path": str(request.url.path)}
    )   

    return JSONResponse(
        status_code = status,
        content = {"detail" : exc.message, "code" : exc.code} 
    )


@app.exception_handler(IntegrityError)
async def integrity_error_handler(request : Request, e: IntegrityError):

    orig = getattr(e, "orig", None)
    sqlstate = None
    for attr in ("sqlstate", "pgcode", "code"):
        sqlstate = getattr(orig, attr, None)
        if isinstance(sqlstate, str) and sqlstate:
            break
        sqlstate = None
    
    constraint = getattr(getattr(orig, "diag", None), "constraint_name", None)
    
    extra = {"sqlstate" : sqlstate,
             "constraint_name" : constraint}

    logger.exception(msg= "integrity error", extra= extra )    

    if sqlstate == "23505":
        
        return JSONResponse(
            status_code = 409,
            content = {"detail" : "already exists", "code" : "already_exists" }
        )
    
    if sqlstate == "23503":
        return JSONResponse(
            status_code = 400,
            content = {"detail" : "not found", "code" : "foreign_key_violation" }
        )
    
    if sqlstate == "23514":
        return JSONResponse(
            status_code = 400,
            content = {"detail" : "status is allowed  {todo, doing, done}, priority is allowed 1 <= x <= 5", 
                       "code" : "check_violation" }
        )
    
    if sqlstate == "23502":
        return JSONResponse(
            status_code = 400,
            content = {"detail" : "missing required field", "code" : "not_null_violation" }
        )
    
    return JSONResponse(
            status_code = 400,
            content = {"detail" : "integrity error", "code" : "integrity_error"}
        )
            


@app.exception_handler(Exception)
async def  exception_hendler(request : Request, e : Exception ):

    logger.exception(msg= "unexpected error")

    return JSONResponse(
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
        content = {"detail" : "internal server error", "code" : "internal_error"} 
    )


##== users ==##
@app.post("/api/users", response_model=UserRead)
async def post_user(payload: UserCreate, db: AsyncSession = Depends(get_db)):

    user = await create_user(db=db, data=payload)
    return user



@app.get("/api/users", response_model=list[UserRead])
async def get_users(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    
    users = await read_users_list(db, limit=limit, offset=offset)
    return users



@app.get("/api/users/{id}", response_model=UserRead)
async def get_user(
    id: int,
    db: AsyncSession = Depends(get_db)
):
    user = await read_user(db=db, id=id)
    if user is None:
        raise NotFoundError()
    return user



##== tasks ==##
@app.get("/api/tasks", response_model=TaskListResponse)
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


@app.get("/api/tasks/{id}", response_model=TaskRead)
async def get_task(
    id: int,
    db: AsyncSession = Depends(get_db)
):
    
    task = await read_task(db=db, id=id)
    if task is None:
        raise  NotFoundError()   #HTTPException(status_code=404, detail="task not found")
    
    return task


@app.post("/api/tasks", response_model=TaskRead)
async def post_task(
    payload: TaskCreate,
    db: AsyncSession = Depends(get_db)
):
    # try:
    task = await create_task(db=db, data=payload)
        
    # except IntegrityError as e:
    #     await db.rollback()
    #     orig = getattr(e, "orig", None)
    #     logger.exception(
    #         "DB IntegrityError sqlstate=%s constraint=%s",
    #         getattr(orig, "pgcode", None),
    #         getattr(getattr(orig, "diag", None), "constraint_name", None),
    #     )
    #     raise

    return task


@app.patch("/api/tasks/{task_id}", response_model= TaskRead)
async def patch_tasks( task_id: int, payload : TaskPatch,  db: AsyncSession = Depends(get_db) ) :
    
    # try:
    task = await update_task(db= db, task_id= task_id, patch= payload)
    # except :
    #     raise

    return task


@app.delete("/api/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task_api(task_id : int, db: AsyncSession = Depends(get_db)) :

    # try: 
    result = await delete_task(db = db, task_id = task_id)
    
    # except :
    #     raise

    # return TaskDelete(id= result)

    





@app.get("/api/stats/tasks-by-status", response_model = StatsResponse)
async def get_tasks_by_status(db: AsyncSession = Depends(get_db)):

    # try:
    stats = await stats_tasks_by_status(db)
    



    # except IntegrityError as e:
    #     await db.rollback()
    #     orig = getattr(e, "orig", None)
    #     logger.exception(
    #         "DB IntegrityError sqlstate=%s constraint=%s",
    #         getattr(orig, "pgcode", None),
    #         getattr(getattr(orig, "diag", None), "constraint_name", None),
    #     )
    #     raise

    return stats