"""
Pydantic schemas for request/response validation and serialization.
Separate from SQLModel database models for clean API contracts.
"""

import uuid
from datetime import datetime
from typing import Optional, List, Literal, Any
from pydantic import BaseModel, EmailStr, Field, ConfigDict


# ==================== USER SCHEMAS ====================

class UserRegister(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserPublic(BaseModel):
    id: uuid.UUID
    name: str
    email: str
    avatar_url: Optional[str] = None
    status: Literal["online", "busy", "away", "offline"] = "offline"
    custom_status: Optional[str] = None
    bio: Optional[str] = None
    phone: Optional[str] = None
    is_bot: bool = False

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    bio: Optional[str] = None
    custom_status: Optional[str] = Field(default=None, max_length=200)
    phone: Optional[str] = Field(default=None, max_length=20)
    avatar_url: Optional[str] = None
    status: Optional[Literal["online", "busy", "away", "offline"]] = None


# ==================== CHANNEL SCHEMAS ====================

class ChannelCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: Optional[str] = None
    is_private: bool = False
    topic: Optional[str] = Field(default=None, max_length=200)


class ChannelPublic(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str] = None
    is_private: bool = False
    topic: Optional[str] = None
    created_at: datetime
    created_by: uuid.UUID
    invite_code: Optional[str] = None
    only_admins_can_post: bool = False
    member_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class ChannelUpdateSettings(BaseModel):
    topic: Optional[str] = Field(default=None, max_length=200)
    description: Optional[str] = None
    only_admins_can_post: Optional[bool] = None


class ChannelJoinRequest(BaseModel):
    invite_code: Optional[str] = None


class ChannelMemberPublic(BaseModel):
    user_id: uuid.UUID
    is_admin: bool
    joined_at: datetime
    user: Optional[UserPublic] = None


# ==================== MESSAGE SCHEMAS ====================

class AttachmentPublic(BaseModel):
    id: uuid.UUID
    name: str
    type: Literal["image", "file"]
    url: str
    size_bytes: int

    model_config = ConfigDict(from_attributes=True)


class ReactionPublic(BaseModel):
    emoji: str
    count: int
    user_ids: List[uuid.UUID]


class MessagePublic(BaseModel):
    id: uuid.UUID
    chat_id: str
    chat_type: Literal["channel", "dm"]
    sender_id: uuid.UUID
    sender_name: str
    sender_avatar: Optional[str] = None
    content: str
    timestamp: datetime
    edited_at: Optional[datetime] = None
    is_pinned: bool = False
    reply_to_id: Optional[uuid.UUID] = None
    reply_to_content: Optional[str] = None
    reply_to_sender_name: Optional[str] = None
    attachments: List[AttachmentPublic] = []
    reactions: List[ReactionPublic] = []
    reply_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class MessageSend(BaseModel):
    chat_id: str
    content: str = Field(min_length=1)
    attachments: List[AttachmentPublic] = []
    reply_to_id: Optional[uuid.UUID] = None


class MessageEdit(BaseModel):
    message_id: uuid.UUID
    content: str = Field(min_length=1)


class MessageDelete(BaseModel):
    message_id: uuid.UUID


class MessageReact(BaseModel):
    message_id: uuid.UUID
    emoji: str = Field(min_length=1, max_length=50)


class MessagePin(BaseModel):
    message_id: uuid.UUID


# ==================== WEBSOCKET EVENT SCHEMAS ====================

# Client-to-Server Events
class WsClientEvent(BaseModel):
    type: str
    payload: dict


# Server-to-Client Events
class WsServerEvent(BaseModel):
    type: str
    payload: Any


class InitPayload(BaseModel):
    users: List[UserPublic]
    channels: List[ChannelPublic]
    messages: List[MessagePublic]
    pinned_ids: List[uuid.UUID] = []


class TypingUpdatePayload(BaseModel):
    chat_id: str
    user_ids: List[uuid.UUID]
    user_names: List[str]


# ==================== UPLOAD SCHEMAS ====================

class UploadResponse(BaseModel):
    url: str
    name: str
    type: str
    size_bytes: int


# ==================== PAGINATION ====================

class PaginatedMessages(BaseModel):
    messages: List[MessagePublic]
    has_more: bool
    next_cursor: Optional[str] = None


# ==================== ERROR RESPONSES ====================

class ErrorResponse(BaseModel):
    detail: str
    code: Optional[str] = None
