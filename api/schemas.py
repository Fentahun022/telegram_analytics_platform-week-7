from pydantic import BaseModel
from datetime import datetime

class ProductMention(BaseModel):
    product: str
    mentions: int

class ChannelActivity(BaseModel):
    channel_name: str
    post_count: int

class Message(BaseModel):
    message_id: int
    message_text: str | None
    posted_at: datetime
    channel_name: str

    class Config:
        orm_mode = True # Enables compatibility with SQLAlchemy objects