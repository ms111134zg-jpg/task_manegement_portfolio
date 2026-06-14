#####=====  import =====#####
##== 標準ライブラリ ==##
##== 外部ライブラリ ==##
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

##== ローカルモジュール ==##
from ..db import get_db
from ..schema.user import UserRead, UserCreate
from ..crud.user import read_users_list, read_user, create_user
from ..errors import NotFoundError



#####=====  APIRouter定義  =====#####
router = APIRouter(prefix="/api/users", tags=["users"])


#####=====  users router  =====#####
@router.post("", response_model=UserRead, status_code=201)
async def post_user(payload: UserCreate, db: AsyncSession = Depends(get_db)):

    user = await create_user(db=db, data=payload)
    return user



@router.get("", response_model=list[UserRead])
async def get_users(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    
    users = await read_users_list(db, limit=limit, offset=offset)
    return users



@router.get("/{id}", response_model=UserRead)
async def get_user(
    id: int,
    db: AsyncSession = Depends(get_db)
):
    user = await read_user(db=db, id=id)
    if user is None:
        raise NotFoundError()
    return user

