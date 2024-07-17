from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from app.models import MessageModel
from app.database import get_db
from pydantic import BaseModel
from typing import List
import os
import datetime

app = FastAPI()

class Message(BaseModel):
    id: int
    username: str
    content: str
    timestamp: datetime.datetime

    class Config:
        orm_mode = True

class MessageCreate(BaseModel):
    username: str
    content: str

# In-memory storage for online users
online_users = []

@app.post("/api/messages", response_model=Message)
async def create_message(message: MessageCreate, db: AsyncSession = Depends(get_db)):
    # Convert the timestamp to a timezone-naive datetime
    timestamp_naive = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
    new_message = MessageModel(
        username=message.username,
        content=message.content,
        timestamp=timestamp_naive
    )
    db.add(new_message)
    await db.commit()
    await db.refresh(new_message)
    return new_message

@app.get("/api/messages", response_model=List[Message])
async def get_messages(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(MessageModel))
    messages = result.scalars().all()
    return messages

@app.delete("/api/messages")
async def clear_messages(db: AsyncSession = Depends(get_db)):
    await db.execute(delete(MessageModel))
    await db.commit()
    return {"message": "All messages cleared"}

@app.get("/api/active-users")
async def get_active_users(username: str):
    current_time = datetime.datetime.now(datetime.timezone.utc)
    # Remove users who have not sent a heartbeat in the last 10 seconds
    online_users[:] = [user for user in online_users if (current_time - user["last_seen"]).total_seconds() < 10]

    # Update the current user's timestamp
    for user in online_users:
        if user["username"] == username:
            user["last_seen"] = current_time
            break
    else:
        online_users.append({"username": username, "last_seen": current_time})

    active_usernames = [user["username"] for user in online_users]
    return {"users": active_usernames}

# Serve static files
app.mount("/static", StaticFiles(directory="frontend/build/static"), name="static")

# Serve the main HTML file
@app.get("/", response_class=HTMLResponse)
async def read_index():
    return FileResponse(os.path.join("frontend", "build", "index.html"))

# Serve the React app for any other route
@app.get("/{full_path:path}", response_class=HTMLResponse)
async def catch_all(request: Request, full_path: str):
    if not full_path.startswith("api/"):
        return FileResponse(os.path.join("frontend", "build", "index.html"))
    return {"message": "This endpoint does not exist"}
