from fastapi import APIRouter
from pydantic import BaseModel
from db import create_chat, update_chat_title, append_message, get_user_chats, get_chat, delete_chat

router = APIRouter(prefix="/chats", tags=["chats"])

class ChatCreate(BaseModel):
    user_id: int
    title: str

class TitleUpdate(BaseModel):
    chat_id: int
    title: str

class ChatAppend(BaseModel):
    chat_id: int
    role: str
    text: str


@router.post("/create")
def create_chat_route(body: ChatCreate):
    return create_chat(body.user_id, body.title)


@router.post("/update_title")
def update_title(body: TitleUpdate):
    print("Updating title:", body.chat_id, body.title)
    update_chat_title(body.chat_id, body.title)
    return {"success": True}


@router.get("/{user_id}")
def get_chats_route(user_id: int):
    return get_user_chats(user_id)


@router.get("/get/{chat_id}")
def get_chat_route(chat_id: int):
    return get_chat(chat_id)


@router.delete("/{chat_id}")
def delete_chat_route(chat_id: int):
    print("Deleting chat:", chat_id)
    delete_chat(chat_id)
    return {"success": True}


@router.post("/append")
def append_message_route(body: ChatAppend):
    append_message(body.chat_id, body.role, body.text)
    return {"status": "ok"}
