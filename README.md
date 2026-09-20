# Real-time Chat Application - FastAPI Backend

A comprehensive real-time chat application backend built with FastAPI, PostgreSQL, WebSockets, and Redis.

## 🚀 Quick Start

### Prerequisites

Before running the application, ensure you have:

1. **Python 3.11+** installed
2. **PostgreSQL 14+** installed and running
3. **Redis 7+** installed and running (optional, for multi-worker support)

### Step 1: Install Dependencies

```bash
# Create a virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your database credentials
# At minimum, update DATABASE_URL with your PostgreSQL connection string
```

### Step 3: Set Up Database

```bash
# Create the PostgreSQL database
# On macOS/Linux:
createdb chatapp

# On Windows (using psql):
psql -U postgres
CREATE DATABASE chatapp;
\q

# Initialize database tables
python -c "import asyncio; from app.database import init_db; asyncio.run(init_db())"
```

### Step 4: Run the Server

```bash
# Development mode (with auto-reload)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Step 5: Access the API

- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health
- **WebSocket Endpoint**: ws://localhost:8000/ws?token=<JWT_TOKEN>

## 📁 Project Structure

```
.
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Application configuration
│   ├── database.py          # Database connection & session
│   ├── auth.py              # JWT authentication utilities
│   ├── models/              # SQLModel database models
│   │   ├── __init__.py
│   │   └── models.py
│   ├── schemas/             # Pydantic request/response schemas
│   │   ├── __init__.py
│   │   └── schemas.py
│   ├── routers/             # API endpoint routers
│   │   ├── __init__.py
│   │   ├── auth.py          # Authentication endpoints
│   │   ├── channels.py      # Channel management
│   │   ├── messages.py      # Message history
│   │   ├── users.py         # User discovery
│   │   └── upload.py        # File uploads
│   ├── services/            # Business logic & integrations
│   │   ├── __init__.py
│   │   ├── storage.py       # File storage (S3/GCS/Local)
│   │   ├── websocket.py     # WebSocket gateway
│   │   └── pubsub.py        # Redis Pub/Sub
│   └── middleware/          # Request/response middleware
│       ├── __init__.py
│       └── error_handler.py
├── requirements.txt         # Python dependencies
├── .env.example            # Environment template
├── .gitignore
└── README.md
```

## 🔌 API Endpoints

### Authentication
- `POST /api/auth/register` - Create new user
- `POST /api/auth/token` - Login & get JWT token
- `GET /api/auth/me` - Get current user profile
- `PUT /api/auth/profile` - Update profile

### Messages
- `GET /api/messages?chatId=X&before=Y&search=Z` - Paginated message history

### Channels
- `GET /api/channels` - List channels
- `POST /api/channels` - Create channel
- `POST /api/channels/{id}/join` - Join channel
- `DELETE /api/channels/{id}/leave` - Leave channel
- `POST /api/channels/{id}/members/{userId}` - Add member (admin)
- `DELETE /api/channels/{id}/members/{userId}` - Remove member (admin)
- `POST /api/channels/{id}/members/{userId}/promote` - Promote to admin
- `POST /api/channels/{id}/members/{userId}/demote` - Demote from admin
- `PUT /api/channels/{id}/settings` - Update settings

### Users
- `GET /api/users` - Discover users
- `GET /api/users/{id}` - Get user profile

### Uploads
- `POST /api/upload/image` - Upload image
- `POST /api/upload/file` - Upload file

## 🔌 WebSocket Protocol

Connect to: `ws://localhost:8000/ws?token=<JWT_TOKEN>`

### Client → Server Events
- `message:send` - Send message
- `message:edit` - Edit message
- `message:delete` - Delete message
- `message:react` - Toggle reaction
- `message:pin` - Toggle pin
- `channel:create` - Create channel
- `channel:join` - Join channel
- `channel:leave` - Leave channel
- `channel:addMember` - Add member
- `channel:removeMember` - Remove member
- `channel:promoteAdmin` - Promote to admin
- `channel:demoteAdmin` - Demote from admin
- `channel:updateSettings` - Update settings
- `typing:start` - Start typing
- `typing:stop` - Stop typing
- `status:update` - Update presence

### Server → Client Events
- `init` - Initial data payload
- `message:new` - New message
- `message:updated` - Message edited
- `message:deleted` - Message deleted
- `message:reaction` - Reaction changed
- `message:pinned` - Message pinned
- `channel:created` - Channel created
- `channel:updated` - Channel updated
- `user:joined` - User joined
- `user:left` - User left
- `user:updated` - User status changed
- `typing:update` - Typing indicators
- `channel:error` - Error message

## 🐘 Database Setup

### PostgreSQL Setup (macOS)

```bash
# Install PostgreSQL
brew install postgresql

# Start PostgreSQL
brew services start postgresql

# Create database
createdb chatapp
```

### PostgreSQL Setup (Windows)

1. Download and install from https://www.postgresql.org/download/windows/
2. Open pgAdmin or psql command line
3. Create database: `CREATE DATABASE chatapp;`

### PostgreSQL Setup (Linux)

```bash
# Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# Start PostgreSQL
sudo systemctl start postgresql

# Create database
sudo -u postgres createdb chatapp
```

## 🔄 Redis Setup (Optional)

Redis is only needed for multi-worker deployments.

### macOS
```bash
brew install redis
brew services start redis
```

### Windows
Download from: https://github.com/microsoftarchive/redis/releases

### Linux
```bash
sudo apt-get install redis-server
sudo systemctl start redis
```

## 🧪 Testing the API

### Register a User
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "email": "john@example.com", "password": "secret123"}'
```

### Login
```bash
curl -X POST http://localhost:8000/api/auth/token \
  -H "Content-Type: application/json" \
  -d '{"email": "john@example.com", "password": "secret123"}'
```

### Get Profile (use token from login response)
```bash
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## 🐳 Docker Deployment (Optional)

```yaml
version: '3.8'
services:
  api:
    build: .
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

## 🔒 Security Features

- JWT Bearer token authentication
- Bcrypt password hashing
- Group membership isolation
- Admin-only posting restrictions
- Admin-gated member management
- Invite codes for private channels
- CORS configuration
- Automatic offline detection

## 📝 Notes

- DM chat IDs use format: `dm:{user1_uuid}:{user2_uuid}`
- Messages use timestamp-based cursor pagination
- User status auto-updates to offline after disconnect delay
- Redis enables cross-worker event broadcasting

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📄 License

MIT License
