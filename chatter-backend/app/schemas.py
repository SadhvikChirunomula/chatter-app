# app/schemas.py
from pydantic import BaseModel
from typing import List
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    password: str

class User(BaseModel):
    id: int
    username: str

    class Config:
        orm_mode = True

class ChatRoomCreate(BaseModel):
    user1_id: int
    user2_id: int

class ChatRoom(BaseModel):
    id: str
    user1_id: int
    user2_id: int

    class Config:
        orm_mode = True

class Message(BaseModel):
    id: int
    chatroom_id: str
    user_id: int
    content: str
    timestamp: datetime

    class Config:
        orm_mode = True

class ChatRoomWithMessages(ChatRoom):
    messages: List[Message] = []

    class Config:
        orm_mode = True
