# app/models.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)

class ChatRoom(Base):
    __tablename__ = "chatrooms"
    id = Column(String, primary_key=True, index=True)
    user1_id = Column(Integer)
    user2_id = Column(Integer)
    messages = relationship("Message", back_populates="chatroom")

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    chatroom_id = Column(String, ForeignKey("chatrooms.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    content = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    chatroom = relationship("ChatRoom", back_populates="messages")
    user = relationship("User")
