# Real-time Chat Application - FastAPI Backend

A comprehensive real-time chat application backend built with **FastAPI**, **PostgreSQL**, **WebSockets**, and **Redis**.

## 🏗️ Architecture

```
backend/
├── main.py              # FastAPI application entry point
├── config.py            # Application configuration (pydantic-settings)
├── database.py          # Async database connection & session management
├── models.py            # SQLModel database models (ORM)
├── schemas.py           # Pydantic request/response schemas
├── auth.py              # JWT authentication utilities
├── storage.py           # File storage service (S3/GCS/Local)
├── websocket.py         # WebSocket gateway & connection manager
├── pubsub.py            # Redis Pub/Sub for multi-worker support
├── init_db.py           # Database initialization script
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
└── routers/
    ├── __init__.py
    ├── auth.py          # Authentication endpoints
    ├── messages.py      # Message history & search
    ├── channels.py      # Channel CRUD & admin actions
    ├── users.py         # User discovery
    └── upload.py        # File upload endpoints
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 14+
- Redis 7+ (optional, for multi-worker deployment)

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your database credentials and settings
```

### 3. Initialize Database

```bash
python init_db.py
```

### 4. Run the Server

```bash
# Development
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production (multiple workers)
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 5. Access the API

- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health
- **WebSocket**: ws://localhost:8000/ws?token=<JWT_TOKEN>

---

## 📡 API Endpoints

### Authentication (`/api/auth`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Create a new user |
| POST | `/api/auth/token` | Login & get JWT token |
| GET | `/api/auth/me` | Get current user profile |
| PUT | `/api/auth/profile` | Update profile |

### Messages (`/api/messages`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/messages?chatId=X&before=Y&search=Z` | Paginated message history with search |

### Channels (`/api/channels`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/channels?search=X` | List channels (public + joined) |
| POST | `/api/channels` | Create a new channel |
| POST | `/api/channels/:id/join` | Join a channel |
| DELETE | `/api/channels/:id/leave` | Leave a channel |
| POST | `/api/channels/:id/members/:userId` | Add member (admin) |
| DELETE | `/api/channels/:id/members/:userId` | Remove member (admin) |
| POST | `/api/channels/:id/members/:userId/promote` | Promote to admin |
| POST | `/api/channels/:id/members/:userId/demote` | Demote from admin |
| PUT | `/api/channels/:id/settings` | Update channel settings |

### Users (`/api/users`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/users?search=X` | Discover users |
| GET | `/api/users/:id` | Get user profile |

### Uploads (`/api/upload`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/upload/image` | Upload image (multipart) |
| POST | `/api/upload/file` | Upload file (multipart) |

---

## 🔌 WebSocket Protocol

### Connection

```
ws://localhost:8000/ws?token=<JWT_TOKEN>
```

### Initial Payload (Server → Client)

On connection, the server sends an `init` event:

```json
{
  "type": "init",
  "payload": {
    "users": [...],
    "channels": [...],
    "messages": [...],
    "pinnedIds": [...]
  }
}
```

### Client → Server Events

| Event | Payload | Description |
|-------|---------|-------------|
| `message:send` | `{chat_id, content, attachments?, reply_to_id?}` | Send a message |
| `message:edit` | `{message_id, content}` | Edit a message |
| `message:delete` | `{message_id}` | Delete a message |
| `message:react` | `{message_id, emoji}` | Toggle reaction |
| `message:pin` | `{message_id}` | Toggle pin |
| `channel:create` | `{name, description?, is_private?, topic?}` | Create channel |
| `channel:join` | `{channel_id, invite_code?}` | Join channel |
| `channel:leave` | `{channel_id}` | Leave channel |
| `channel:addMember` | `{channel_id, user_id}` | Add member (admin) |
| `channel:removeMember` | `{channel_id, user_id}` | Remove member (admin) |
| `channel:promoteAdmin` | `{channel_id, user_id}` | Promote to admin |
| `channel:demoteAdmin` | `{channel_id, user_id}` | Demote from admin |
| `channel:updateSettings` | `{channel_id, topic?, description?, only_admins_can_post?}` | Update settings |
| `typing:start` | `{chat_id}` | Start typing indicator |
| `typing:stop` | `{chat_id}` | Stop typing indicator |
| `status:update` | `{status}` | Update presence (online/busy/away) |

### Server → Client Events

| Event | Description |
|-------|-------------|
| `message:new` | New message in a chat |
| `message:updated` | Message was edited |
| `message:deleted` | Message was deleted |
| `message:reaction` | Reaction added/removed |
| `message:pinned` | Message pin toggled |
| `channel:created` | New channel created |
| `channel:updated` | Channel settings/membership changed |
| `user:joined` | User joined a channel |
| `user:left` | User left a channel |
| `user:updated` | User status/profile changed |
| `typing:update` | Typing indicators changed |
| `channel:error` | Permission/validation error |

---

## 🔒 Security Features

1. **JWT Authentication** - Bearer token auth with configurable expiry
2. **Password Hashing** - bcrypt via passlib
3. **Group Membership Isolation** - Users only receive broadcasts for channels they're in
4. **Admin-Only Posting** - Channels can restrict posting to admins only
5. **Admin-Gated Actions** - Member management requires admin privileges
6. **Invite Codes** - Private channels require valid invite codes to join
7. **CORS Configuration** - Configurable allowed origins

---

## 💾 Database Schema

### Users
- UUID primary key, email unique, password hashed with bcrypt
- Status enum: online, busy, away, offline
- Supports bots via `is_bot` flag

### Channels
- UUID primary key, optional invite codes for private channels
- `only_admins_can_post` flag for announcement-style channels
- Created-by references the creator user

### Channel Members
- Composite primary key (channel_id, user_id)
- `is_admin` flag for role management

### Messages
- `chat_id` supports both channel UUIDs and DM keys (`dm:user1:user2`)
- Self-referential `reply_to_id` for threaded replies
- Indexed on chat_id, sender_id, and timestamp

### Attachments
- Linked to messages via foreign key
- Supports image and file types

### Reactions
- Unique per (message, user, emoji)
- Aggregated for display

---

## 🐳 Docker Deployment

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  api:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/chatapp
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis

  db:
    image: postgres:16
    environment:
      POSTGRES_DB: chatapp
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    volumes:
      - pgdata:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine

volumes:
  pgdata:
```

---

## 📝 Notes

- **DM Chat IDs**: Direct messages use the format `dm:{user1_uuid}:{user2_uuid}` where UUIDs are sorted alphabetically for consistency.
- **Cursor Pagination**: Messages use timestamp-based cursor pagination via the `before` query parameter.
- **Presence Lifecycle**: When a WebSocket disconnects, the user's status is set to `offline` after a configurable delay (default 30 seconds) unless they reconnect.
- **Multi-Worker**: Redis Pub/Sub enables real-time events across multiple Uvicorn workers.
