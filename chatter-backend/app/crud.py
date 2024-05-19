# app/crud.py
from sqlalchemy.orm import Session
from . import models, schemas
from uuid import uuid4

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(username=user.username, password=user.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False

def create_chatroom(db: Session, chatroom: schemas.ChatRoomCreate):
    chatroom_id = str(uuid4())
    db_chatroom = models.ChatRoom(id=chatroom_id, user1_id=chatroom.user1_id, user2_id=chatroom.user2_id)
    db.add(db_chatroom)
    db.commit()
    db.refresh(db_chatroom)
    return db_chatroom

def chatroom_exists(db: Session, user1_id: int, user2_id: int):
    return db.query(models.ChatRoom).filter(
        ((models.ChatRoom.user1_id == user1_id) & (models.ChatRoom.user2_id == user2_id)) |
        ((models.ChatRoom.user1_id == user2_id) & (models.ChatRoom.user2_id == user1_id))
    ).first() is not None

def delete_chatroom(db: Session, chatroom_id: str):
    db_chatroom = db.query(models.ChatRoom).filter(models.ChatRoom.id == chatroom_id).first()
    if db_chatroom:
        db.delete(db_chatroom)
        db.commit()
        return True
    return False

def get_active_chats(db: Session):
    return db.query(models.ChatRoom).all()

def get_chats_by_user(db: Session, user_id: int):
    return db.query(models.ChatRoom).filter((models.ChatRoom.user1_id == user_id) | (models.ChatRoom.user2_id == user_id)).all()

def create_message(db: Session, chatroom_id: str, user_id: int, content: str):
    db_message = models.Message(chatroom_id=chatroom_id, user_id=user_id, content=content)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def get_chat_details(db: Session, chatroom_id: str):
    chatroom = db.query(models.ChatRoom).filter(models.ChatRoom.id == chatroom_id).first()
    if chatroom:
        chatroom_data = schemas.ChatRoomWithMessages(
            id=chatroom.id,
            user1_id=chatroom.user1_id,
            user2_id=chatroom.user2_id,
            messages=[
                schemas.Message(
                    id=message.id,
                    chatroom_id=message.chatroom_id,
                    user_id=message.user_id,
                    content=message.content,
                    timestamp=message.timestamp
                )
                for message in db.query(models.Message).filter(models.Message.chatroom_id == chatroom_id).all()
            ]
        )
        return chatroom_data
    return None

def delete_messages_by_chatroom(db: Session, chatroom_id: str):
    db.query(models.Message).filter(models.Message.chatroom_id == chatroom_id).delete()
    db.commit()
    return True
