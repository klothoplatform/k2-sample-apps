from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from .models import Message

async def get_messages(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(Message).order_by(Message.timestamp).offset(skip).limit(limit))
    return result.scalars().all()

async def create_message(db: AsyncSession, username: str, content: str):
    db_message = Message(username=username, content=content)
    db.add(db_message)
    await db.commit()
    await db.refresh(db_message)
    return db_message
