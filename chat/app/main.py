from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect, Depends
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
import json

app = FastAPI()

# In-memory storage for online users
online_users = []

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

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        disconnected_connections = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except WebSocketDisconnect:
                disconnected_connections.append(connection)
        for connection in disconnected_connections:
            self.disconnect(connection)

    async def broadcast_message(self, message: MessageModel):
        await self.broadcast(json.dumps({"type": "message", "data": message.to_dict()}))

    async def broadcast_clear(self):
        await self.broadcast(json.dumps({"type": "clear"}))

    async def broadcast_users(self):
        users = [user['username'] for user in online_users]
        await self.broadcast(json.dumps({"type": "users", "data": users}))

manager = ConnectionManager()

@app.post("/api/messages", response_model=Message)
async def create_message(message: MessageCreate, db: AsyncSession = Depends(get_db)):
    new_message = MessageModel(
        username=message.username,
        content=message.content,
        timestamp=datetime.datetime.utcnow()
    )
    db.add(new_message)
    await db.commit()
    await db.refresh(new_message)
    await manager.broadcast_message(new_message)
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
    await manager.broadcast_clear()
    return {"message": "All messages cleared"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            if message['type'] == 'join':
                online_users.append({"username": message['username'], "websocket": websocket})
                await manager.broadcast_users()
            elif message['type'] == 'leave':
                user = next((user for user in online_users if user["websocket"] == websocket), None)
                if user:
                    online_users.remove(user)
                await manager.broadcast_users()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        user = next((user for user in online_users if user["websocket"] == websocket), None)
        if user:
            online_users.remove(user)
        await manager.broadcast_users()

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
