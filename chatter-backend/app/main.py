# app/main.py
from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect, Query
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from . import models, schemas, crud, dependencies, matchmaker
from typing import List
from .websocket import ConnectionManager
import json

app = FastAPI()
manager = ConnectionManager()

# CORS configuration
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows all origins, you can restrict to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/register/", response_model=schemas.User)
def register_user(user: schemas.UserCreate, db: Session = Depends(dependencies.get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)

@app.delete("/user/{user_id}")
def delete_user(user_id: int, db: Session = Depends(dependencies.get_db)):
    success = crud.delete_user(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}

@app.post("/login/")
def login_user(user: schemas.UserCreate, db: Session = Depends(dependencies.get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if not db_user or db_user.password != user.password:
        raise HTTPException(status_code=400, detail="Invalid username or password")
    return {"id": db_user.id, "message": "Login successful"}

@app.post("/startchat/")
def start_chat(user_id: int = Query(...), db: Session = Depends(dependencies.get_db)):
    chatroom = matchmaker.add_user(user_id, db)
    if chatroom:
        return chatroom
    return {"message": "Waiting for another user"}

@app.delete("/chatroom/{chatroom_id}")
def delete_chatroom(chatroom_id: str, db: Session = Depends(dependencies.get_db)):
    crud.delete_messages_by_chatroom(db, chatroom_id)
    success = crud.delete_chatroom(db, chatroom_id)
    if not success:
        raise HTTPException(status_code=404, detail="Chat room not found")
    return {"message": "Chat room deleted successfully"}

@app.get("/activechats/", response_model=List[schemas.ChatRoom])
def get_active_chats(db: Session = Depends(dependencies.get_db)):
    return crud.get_active_chats(db)

@app.get("/chatsbyuser/", response_model=List[schemas.ChatRoom])
def get_chats_by_user(user_id: int = Query(...), db: Session = Depends(dependencies.get_db)):
    return crud.get_chats_by_user(db, user_id)

@app.get("/waitingusers/")
def get_waiting_users():
    return matchmaker.waiting_users

@app.get("/activeconnections/")
def get_active_connections():
    return manager.get_active_connections()

@app.get("/chatdetails/{chatroom_id}", response_model=schemas.ChatRoomWithMessages)
def get_chat_details(chatroom_id: str, db: Session = Depends(dependencies.get_db)):
    chat_details = crud.get_chat_details(db, chatroom_id)
    if not chat_details:
        raise HTTPException(status_code=404, detail="Chat room not found")
    return chat_details

@app.post("/chatroom/", response_model=schemas.ChatRoom)
def create_chatroom(chatroom: schemas.ChatRoomCreate, db: Session = Depends(dependencies.get_db)):
    return crud.create_chatroom(db=db, chatroom=chatroom)

@app.websocket("/ws/{chatroom_id}")
async def websocket_endpoint(websocket: WebSocket, chatroom_id: str, db: Session = Depends(dependencies.get_db)):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            user_id = message_data.get("user_id")
            content = message_data.get("content")
            print(f"Saving message to DB: user_id={user_id}, content={content}")
            if user_id and content:
                message = crud.create_message(db, chatroom_id, user_id, content)
                response = {
                    "user_id": message.user_id,
                    "content": message.content,
                    "timestamp": message.timestamp.isoformat()
                }
                # await manager.send_personal_message(json.dumps(response), websocket)
                await manager.broadcast(json.dumps(response))
                # print(f"Broadcasting message: {response_json}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
