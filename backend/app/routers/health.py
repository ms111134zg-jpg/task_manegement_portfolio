#####=====  import =====#####
##== 標準ライブラリ ==##
##== 外部ライブラリ ==##
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

##== ローカルモジュール ==##
from ..db import get_db




#####=====  APIRouter定義  =====#####
router = APIRouter(prefix="/api/health", tags=["health"])



##== 疎通チェック ==##
@router.get("")
def health_api_check():
    return {"status": "running"}

@router.get("/db")
async def health_db(db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT 1;"))
    return {"ok":True, "value": result.scalar_one()}
