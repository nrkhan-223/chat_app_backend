"""
Messages API endpoints.
Handles message history retrieval with pagination and search.
"""

import uuid
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from sqlmodel import col

from database import get_session
from models import User, Message, Channel, ChannelMember, Attachment, Reaction, ChatType
from schemas import MessagePublic, PaginatedMessages, AttachmentPublic, ReactionPublic
from auth import get_current_user

router = APIRouter(prefix="/messages", tags=["Messages"])


async def _serialize_message(
    session: AsyncSession,
    message: Message,
    reply_count: int = 0,
) -> MessagePublic:
    """Serialize a Message ORM object into a MessagePublic schema."""
    # Get sender info
    sender = message.sender
    sender_name = sender.name if sender else "Unknown"
    sender_avatar = sender.avatar_url if sender else None

    # Get reply info
    reply_to_content = None
    reply_to_sender_name = None
    if message.reply_to and message.reply_to.sender:
        reply_to_content = message.reply_to.content[:100]  # Truncate for preview
        reply_to_sender_name = message.reply_to.sender.name

    # Get attachments
    attachments = [
        AttachmentPublic.model_validate(att)
        for att in (message.attachments or [])
    ]

    # Aggregate reactions by emoji
    reaction_map = {}
    for reaction in (message.reactions or []):
        emoji = reaction.emoji
        if emoji not in reaction_map:
            reaction_map[emoji] = {"emoji": emoji, "count": 0, "user_ids": []}
        reaction_map[emoji]["count"] += 1
        reaction_map[emoji]["user_ids"].append(reaction.user_id)

    reactions = [ReactionPublic(**v) for v in reaction_map.values()]

    return MessagePublic(
        id=message.id,
        chat_id=message.chat_id,
        chat_type=message.chat_type.value,
        sender_id=message.sender_id,
        sender_name=sender_name,
        sender_avatar=sender_avatar,
        content=message.content,
        timestamp=message.timestamp,
        edited_at=message.edited_at,
        is_pinned=message.is_pinned,
        reply_to_id=message.reply_to_id,
        reply_to_content=reply_to_content,
        reply_to_sender_name=reply_to_sender_name,
        attachments=attachments,
        reactions=reactions,
        reply_count=reply_count,
    )


async def _get_reply_counts(session: AsyncSession, message_ids: list) -> dict:
    """Get reply counts for a list of message IDs."""
    if not message_ids:
        return {}

    result = await session.execute(
        select(Message.reply_to_id, func.count(Message.id))
        .where(Message.reply_to_id.in_(message_ids))
        .group_by(Message.reply_to_id)
    )
    return {row[0]: row[1] for row in result.all()}


@router.get("", response_model=PaginatedMessages)
async def get_messages(
    chat_id: str = Query(..., description="Channel UUID or DM key (dm:user1:user2)"),
    before: Optional[str] = Query(None, description="Cursor: ISO timestamp for pagination"),
    limit: int = Query(50, ge=1, le=200, description="Number of messages to fetch"),
    search: Optional[str] = Query(None, description="Full-text search query"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Fetch paginated message history for a specific chat.
    Supports cursor-based pagination and full-text search.
    """
    # Verify user has access to this chat
    if chat_id.startswith("dm:"):
        # For DMs, verify the user is part of the DM
        parts = chat_id.split(":")
        if len(parts) == 3:
            user_ids_in_dm = [parts[1], parts[2]]
            if str(current_user.id) not in user_ids_in_dm:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You are not part of this DM conversation",
                )
    else:
        # For channels, verify membership
        channel_uuid = uuid.UUID(chat_id)
        membership = await session.execute(
            select(ChannelMember).where(
                and_(
                    ChannelMember.channel_id == channel_uuid,
                    ChannelMember.user_id == current_user.id,
                )
            )
        )
        if not membership.scalar_one_or_none():
            # Check if channel is public
            channel_result = await session.execute(
                select(Channel).where(Channel.id == channel_uuid)
            )
            channel = channel_result.scalar_one_or_none()
            if not channel or channel.is_private:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have access to this channel",
                )

    # Build query
    query = select(Message).where(Message.chat_id == chat_id)

    # Apply cursor-based pagination
    if before:
        try:
            cursor_time = datetime.fromisoformat(before)
            query = query.where(Message.timestamp < cursor_time)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid cursor format. Use ISO 8601 timestamp.",
            )

    # Apply search filter
    if search:
        query = query.where(Message.content.ilike(f"%{search}%"))

    # Order by timestamp descending and limit
    query = query.order_by(desc(Message.timestamp)).limit(limit + 1)

    # Execute query
    result = await session.execute(query)
    messages = result.scalars().all()

    # Check if there are more messages
    has_more = len(messages) > limit
    if has_more:
        messages = messages[:limit]

    # Get reply counts
    message_ids = [m.id for m in messages]
    reply_counts = await _get_reply_counts(session, message_ids)

    # Serialize messages
    serialized = []
    for msg in messages:
        count = reply_counts.get(msg.id, 0)
        serialized.append(await _serialize_message(session, msg, count))

    # Reverse to chronological order
    serialized.reverse()

    next_cursor = None
    if has_more and messages:
        next_cursor = messages[-1].timestamp.isoformat()

    return PaginatedMessages(
        messages=serialized,
        has_more=has_more,
        next_cursor=next_cursor,
    )
