"""
Channels API endpoints.
Handles channel listing, creation, joining, and administrative actions.
"""

import uuid
import secrets
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, delete
from sqlmodel import col

from database import get_session
from models import User, Channel, ChannelMember
from schemas import ChannelPublic, ChannelCreate, ChannelUpdateSettings, ChannelJoinRequest
from auth import get_current_user

router = APIRouter(prefix="/channels", tags=["Channels"])


@router.get("", response_model=list[ChannelPublic])
async def list_channels(
    search: Optional[str] = Query(None, description="Search channels by name"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Fetch list of channels the user is a member of, plus public channels."""
    # Get channels where user is a member
    member_query = select(ChannelMember.channel_id).where(
        ChannelMember.user_id == current_user.id
    )
    member_result = await session.execute(member_query)
    member_channel_ids = {row[0] for row in member_result.all()}

    # Get public channels + user's channels
    query = select(Channel)

    if search:
        query = query.where(Channel.name.ilike(f"%{search}%"))

    query = query.order_by(Channel.created_at.desc())
    result = await session.execute(query)
    channels = result.scalars().all()

    # Filter: show public channels + user's private channels
    filtered = []
    for ch in channels:
        if not ch.is_private or ch.id in member_channel_ids:
            filtered.append(ch)

    # Get member counts
    channels_data = []
    for channel in filtered:
        count_result = await session.execute(
            select(func.count(ChannelMember.user_id)).where(
                ChannelMember.channel_id == channel.id
            )
        )
        member_count = count_result.scalar() or 0

        channel_data = ChannelPublic(
            id=channel.id,
            name=channel.name,
            description=channel.description,
            is_private=channel.is_private,
            topic=channel.topic,
            created_at=channel.created_at,
            created_by=channel.created_by,
            invite_code=channel.invite_code if channel.id in member_channel_ids else None,
            only_admins_can_post=channel.only_admins_can_post,
            member_count=member_count,
        )
        channels_data.append(channel_data)

    return channels_data


@router.post("", response_model=ChannelPublic, status_code=status.HTTP_201_CREATED)
async def create_channel(
     ChannelCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Create a new channel. The creator becomes the admin."""
    invite_code = None
    if data.is_private:
        invite_code = secrets.token_urlsafe(12)

    channel = Channel(
        name=data.name,
        description=data.description,
        is_private=data.is_private,
        topic=data.topic,
        created_by=current_user.id,
        invite_code=invite_code,
    )
    session.add(channel)
    await session.flush()

    member = ChannelMember(
        channel_id=channel.id,
        user_id=current_user.id,
        is_admin=True,
    )
    session.add(member)
    await session.flush()
    await session.refresh(channel)

    return ChannelPublic(
        id=channel.id,
        name=channel.name,
        description=channel.description,
        is_private=channel.is_private,
        topic=channel.topic,
        created_at=channel.created_at,
        created_by=channel.created_by,
        invite_code=channel.invite_code,
        only_admins_can_post=channel.only_admins_can_post,
        member_count=1,
    )


@router.post("/{channel_id}/join", response_model=dict)
async def join_channel(
    channel_id: uuid.UUID,
     ChannelJoinRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Join a channel. Requires invite code for private channels."""
    result = await session.execute(select(Channel).where(Channel.id == channel_id))
    channel = result.scalar_one_or_none()

    if not channel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Channel not found")

    existing = await session.execute(
        select(ChannelMember).where(
            and_(ChannelMember.channel_id == channel_id, ChannelMember.user_id == current_user.id)
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Already a member")

    if channel.is_private:
        if not data.invite_code or data.invite_code != channel.invite_code:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid invite code")

    member = ChannelMember(channel_id=channel_id, user_id=current_user.id, is_admin=False)
    session.add(member)
    await session.flush()

    return {"status": "joined", "channel_id": str(channel_id)}


@router.delete("/{channel_id}/leave", response_model=dict)
async def leave_channel(
    channel_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Leave a channel. If creator leaves, oldest member is promoted to admin."""
    result = await session.execute(
        select(ChannelMember).where(
            and_(ChannelMember.channel_id == channel_id, ChannelMember.user_id == current_user.id)
        )
    )
    membership = result.scalar_one_or_none()

    if not membership:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not a member")

    channel_result = await session.execute(select(Channel).where(Channel.id == channel_id))
    channel = channel_result.scalar_one_or_none()

    await session.delete(membership)
    await session.flush()

    if channel and channel.created_by == current_user.id:
        oldest_member_result = await session.execute(
            select(ChannelMember).where(ChannelMember.channel_id == channel_id).order_by(ChannelMember.joined_at.asc()).limit(1)
        )
        oldest_member = oldest_member_result.scalar_one_or_none()
        if oldest_member:
            oldest_member.is_admin = True
            session.add(oldest_member)
            await session.flush()

    return {"status": "left", "channel_id": str(channel_id)}


@router.post("/{channel_id}/members/{user_id}", response_model=dict)
async def add_member(
    channel_id: uuid.UUID,
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Add a member to a channel. Requester must be an admin."""
    admin_check = await session.execute(
        select(ChannelMember).where(
            and_(ChannelMember.channel_id == channel_id, ChannelMember.user_id == current_user.id, ChannelMember.is_admin == True)
        )
    )
    if not admin_check.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can add members")

    user_result = await session.execute(select(User).where(User.id == user_id))
    if not user_result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    existing = await session.execute(
        select(ChannelMember).where(and_(ChannelMember.channel_id == channel_id, ChannelMember.user_id == user_id))
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User is already a member")

    member = ChannelMember(channel_id=channel_id, user_id=user_id, is_admin=False)
    session.add(member)
    await session.flush()

    return {"status": "added", "user_id": str(user_id)}


@router.delete("/{channel_id}/members/{user_id}", response_model=dict)
async def remove_member(
    channel_id: uuid.UUID,
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Remove a member from a channel. Requester must be an admin."""
    admin_check = await session.execute(
        select(ChannelMember).where(
            and_(ChannelMember.channel_id == channel_id, ChannelMember.user_id == current_user.id, ChannelMember.is_admin == True)
        )
    )
    if not admin_check.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can remove members")

    result = await session.execute(
        select(ChannelMember).where(and_(ChannelMember.channel_id == channel_id, ChannelMember.user_id == user_id))
    )
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")

    await session.delete(member)
    await session.flush()
    return {"status": "removed", "user_id": str(user_id)}


@router.post("/{channel_id}/members/{user_id}/promote", response_model=dict)
async def promote_admin(
    channel_id: uuid.UUID,
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Promote a member to admin. Requester must be an admin."""
    admin_check = await session.execute(
        select(ChannelMember).where(
            and_(ChannelMember.channel_id == channel_id, ChannelMember.user_id == current_user.id, ChannelMember.is_admin == True)
        )
    )
    if not admin_check.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can promote members")

    result = await session.execute(
        select(ChannelMember).where(and_(ChannelMember.channel_id == channel_id, ChannelMember.user_id == user_id))
    )
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")

    member.is_admin = True
    session.add(member)
    await session.flush()
    return {"status": "promoted", "user_id": str(user_id)}


@router.post("/{channel_id}/members/{user_id}/demote", response_model=dict)
async def demote_admin(
    channel_id: uuid.UUID,
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Demote an admin to regular member. Requester must be an admin."""
    admin_check = await session.execute(
        select(ChannelMember).where(
            and_(ChannelMember.channel_id == channel_id, ChannelMember.user_id == current_user.id, ChannelMember.is_admin == True)
        )
    )
    if not admin_check.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can demote members")

    result = await session.execute(
        select(ChannelMember).where(and_(ChannelMember.channel_id == channel_id, ChannelMember.user_id == user_id))
    )
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")

    member.is_admin = False
    session.add(member)
    await session.flush()
    return {"status": "demoted", "user_id": str(user_id)}


@router.put("/{channel_id}/settings", response_model=ChannelPublic)
async def update_channel_settings(
    channel_id: uuid.UUID,
     ChannelUpdateSettings,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Update channel settings. Requester must be an admin."""
    admin_check = await session.execute(
        select(ChannelMember).where(
            and_(ChannelMember.channel_id == channel_id, ChannelMember.user_id == current_user.id, ChannelMember.is_admin == True)
        )
    )
    if not admin_check.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can update channel settings")

    result = await session.execute(select(Channel).where(Channel.id == channel_id))
    channel = result.scalar_one_or_none()
    if not channel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Channel not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(channel, field, value)

    session.add(channel)
    await session.flush()
    await session.refresh(channel)

    count_result = await session.execute(
        select(func.count(ChannelMember.user_id)).where(ChannelMember.channel_id == channel_id)
    )
    member_count = count_result.scalar() or 0

    return ChannelPublic(
        id=channel.id,
        name=channel.name,
        description=channel.description,
        is_private=channel.is_private,
        topic=channel.topic,
        created_at=channel.created_at,
        created_by=channel.created_by,
        invite_code=channel.invite_code,
        only_admins_can_post=channel.only_admins_can_post,
        member_count=member_count,
    )
