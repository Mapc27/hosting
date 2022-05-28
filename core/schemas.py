from pydantic import BaseModel


class ChatCreate(BaseModel):
    user_id: int
