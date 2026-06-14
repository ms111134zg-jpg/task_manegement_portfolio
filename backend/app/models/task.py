from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Text, BigInteger, SmallInteger, Date, DateTime, func, ForeignKey, Index
from .base import Base

# class Base(DeclarativeBase):
#     pass

class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, 
        ForeignKey("users.id", name="tasks_user_id_fk", ondelete="RESTRICT"), 
        nullable=False)
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str|None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(10), server_default="todo", nullable=False)
    priority: Mapped[int] = mapped_column(SmallInteger, server_default="3", nullable=False)
    due_date: Mapped["Date|None"] = mapped_column(Date, nullable=True)
    created_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        Index("idx_id", "id"),
        Index("idx_status", "status"),
        Index("idx_due", "due_date"),
        Index("idx_update", "updated_at")
    )