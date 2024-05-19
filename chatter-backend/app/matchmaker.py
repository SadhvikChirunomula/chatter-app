# app/matchmaker.py
from typing import List, Dict
from sqlalchemy.orm import Session
from . import crud, schemas
from uuid import uuid4

waiting_users: List[Dict] = []

def add_user(user_id: int, db: Session):
    waiting_users.append({"user_id": user_id})
    if len(waiting_users) > 1:
        user1 = waiting_users.pop(0)
        user2 = waiting_users.pop(0)
        if not crud.chatroom_exists(db, user1["user_id"], user2["user_id"]):
            return create_chatroom(user1["user_id"], user2["user_id"], db)
    return None

def create_chatroom(user1_id: int, user2_id: int, db: Session) -> Dict:
    chatroom = schemas.ChatRoomCreate(user1_id=user1_id, user2_id=user2_id)
    return crud.create_chatroom(db=db, chatroom=chatroom)
