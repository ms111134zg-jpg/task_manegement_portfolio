from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.user import User
from ..schema_pydantic.user import UserCreate


async def read_users_list(db: AsyncSession, limit: int = 50, offset: int = 0) -> list[User]:
    stmt = select(User).order_by(User.id).limit(limit).offset(offset)
    result = await db.execute(stmt)

    return result.scalars().all()


async def read_user(db: AsyncSession, id: int) -> User:
    stmt = select(User).where(User.id == id)
    result = await db.execute(stmt)
    
    return result.scalar_one_or_none()


async  def create_user(db: AsyncSession, data: UserCreate):
    user = User(name=data.name, email=data.email)
    db.add(user)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise

    await db.refresh(user)
    return user