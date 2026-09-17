import { useState } from 'react'

function App() {
  const [activeTab, setActiveTab] = useState<'overview' | 'endpoints' | 'websocket' | 'schema'>('overview')

  return (
    <div className="min-h-screen bg-gray-900 text-gray-100">
      {/* Header */}
      <header className="bg-gray-800 border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-green-500 rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">Chat Application Backend</h1>
              <p className="text-gray-400 text-sm">FastAPI + PostgreSQL + WebSocket + Redis</p>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <nav className="bg-gray-800 border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex gap-1">
            {(['overview', 'endpoints', 'websocket', 'schema'] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-4 py-3 text-sm font-medium capitalize transition-colors ${
                  activeTab === tab
                    ? 'text-green-400 border-b-2 border-green-400'
                    : 'text-gray-400 hover:text-gray-200'
                }`}
              >
                {tab}
              </button>
            ))}
          </div>
        </div>
      </nav>

      {/* Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        {activeTab === 'overview' && <OverviewTab />}
        {activeTab === 'endpoints' && <EndpointsTab />}
        {activeTab === 'websocket' && <WebSocketTab />}
        {activeTab === 'schema' && <SchemaTab />}
      </main>

      {/* Footer */}
      <footer className="bg-gray-800 border-t border-gray-700 py-4">
        <div className="max-w-7xl mx-auto px-4 text-center text-gray-500 text-sm">
          Python backend code located in <code className="text-green-400">backend/</code> directory • 
          Run with <code className="text-green-400">uvicorn main:app --reload</code>
        </div>
      </footer>
    </div>
  )
}

function OverviewTab() {
  return (
    <div className="space-y-8">
      <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
        <h2 className="text-xl font-bold text-white mb-4">🚀 Quick Start</h2>
        <div className="space-y-4">
          <div className="bg-gray-900 rounded-lg p-4 font-mono text-sm">
            <p className="text-gray-500"># 1. Install dependencies</p>
            <p className="text-green-400">cd backend && pip install -r requirements.txt</p>
            <br />
            <p className="text-gray-500"># 2. Configure environment</p>
            <p className="text-green-400">cp .env.example .env</p>
            <br />
            <p className="text-gray-500"># 3. Initialize database</p>
            <p className="text-green-400">python init_db.py</p>
            <br />
            <p className="text-gray-500"># 4. Run the server</p>
            <p className="text-green-400">uvicorn main:app --reload --port 8000</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <FeatureCard
          icon="⚡"
          title="FastAPI"
          description="High-performance async Python framework with automatic OpenAPI docs"
        />
        <FeatureCard
          icon="🐘"
          title="PostgreSQL"
          description="Robust relational database with SQLModel ORM for type-safe queries"
        />
        <FeatureCard
          icon="🔌"
          title="WebSockets"
          description="Real-time bidirectional communication for instant messaging"
        />
        <FeatureCard
          icon="🔐"
          title="JWT Auth"
          description="Secure token-based authentication with bcrypt password hashing"
        />
        <FeatureCard
          icon="📁"
          title="File Storage"
          description="Multi-provider support: AWS S3, Google Cloud Storage, or local"
        />
        <FeatureCard
          icon="🔄"
          title="Redis Pub/Sub"
          description="Cross-worker event broadcasting for multi-instance deployments"
        />
      </div>

      <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
        <h2 className="text-xl font-bold text-white mb-4">📂 Project Structure</h2>
        <pre className="bg-gray-900 rounded-lg p-4 text-sm text-gray-300 overflow-x-auto">
{`backend/
├── main.py              # FastAPI app entry point
├── config.py            # Pydantic settings configuration
├── database.py          # Async SQLAlchemy engine & sessions
├── models.py            # SQLModel ORM models
├── schemas.py           # Pydantic request/response schemas
├── auth.py              # JWT & password utilities
├── storage.py           # File upload service (S3/GCS/Local)
├── websocket.py         # WebSocket gateway & connection manager
├── pubsub.py            # Redis Pub/Sub for multi-worker
├── init_db.py           # Database initialization script
├── requirements.txt     # Python dependencies
├── .env.example         # Environment template
└── routers/
    ├── auth.py          # POST /register, /token, GET /me, PUT /profile
    ├── messages.py      # GET /messages (paginated + search)
    ├── channels.py      # Channel CRUD & admin actions
    ├── users.py         # User discovery & search
    └── upload.py        # POST /upload/image, /upload/file`}
        </pre>
      </div>

      <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
        <h2 className="text-xl font-bold text-white mb-4">🔒 Security Features</h2>
        <ul className="space-y-2 text-gray-300">
          <li className="flex items-start gap-2">
            <span className="text-green-400">✓</span>
            <span>JWT Bearer token authentication with configurable expiry</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-green-400">✓</span>
            <span>Bcrypt password hashing via passlib</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-green-400">✓</span>
            <span>Group membership isolation - users only see their channels</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-green-400">✓</span>
            <span>Admin-only posting restrictions per channel</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-green-400">✓</span>
            <span>Admin-gated member management (add/remove/promote/demote)</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-green-400">✓</span>
            <span>Invite code validation for private channels</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-green-400">✓</span>
            <span>CORS configuration with allowed origins</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-green-400">✓</span>
            <span>Presence lifecycle with configurable offline delay</span>
          </li>
        </ul>
      </div>
    </div>
  )
}

function EndpointsTab() {
  return (
    <div className="space-y-6">
      <EndpointGroup
        title="Authentication"
        prefix="/api/auth"
        endpoints={[
          { method: 'POST', path: '/register', desc: 'Create a new user account', body: '{ name, email, password }' },
          { method: 'POST', path: '/token', desc: 'Login and get JWT token', body: '{ email, password }' },
          { method: 'GET', path: '/me', desc: 'Get current user profile', body: 'Bearer token required' },
          { method: 'PUT', path: '/profile', desc: 'Update bio, name, status, phone, avatar', body: '{ name?, bio?, custom_status?, phone?, avatar_url?, status? }' },
        ]}
      />

      <EndpointGroup
        title="Messages"
        prefix="/api/messages"
        endpoints={[
          { method: 'GET', path: '', desc: 'Paginated message history with cursor & search', body: '?chatId=X&before=TIMESTAMP&limit=50&search=QUERY' },
        ]}
      />

      <EndpointGroup
        title="Channels"
        prefix="/api/channels"
        endpoints={[
          { method: 'GET', path: '', desc: 'List public + joined channels', body: '?search=QUERY' },
          { method: 'POST', path: '', desc: 'Create a new channel', body: '{ name, description?, is_private?, topic? }' },
          { method: 'POST', path: '/:id/join', desc: 'Join a channel (invite code for private)', body: '{ invite_code? }' },
          { method: 'DELETE', path: '/:id/leave', desc: 'Leave a channel', body: '' },
          { method: 'POST', path: '/:id/members/:userId', desc: 'Add member (admin only)', body: '' },
          { method: 'DELETE', path: '/:id/members/:userId', desc: 'Remove member (admin only)', body: '' },
          { method: 'POST', path: '/:id/members/:userId/promote', desc: 'Promote to admin', body: '' },
          { method: 'POST', path: '/:id/members/:userId/demote', desc: 'Demote from admin', body: '' },
          { method: 'PUT', path: '/:id/settings', desc: 'Update channel settings (admin)', body: '{ topic?, description?, only_admins_can_post? }' },
        ]}
      />

      <EndpointGroup
        title="Users"
        prefix="/api/users"
        endpoints={[
          { method: 'GET', path: '', desc: 'Discover users in workspace', body: '?search=QUERY' },
          { method: 'GET', path: '/:id', desc: 'Get user public profile', body: '' },
        ]}
      />

      <EndpointGroup
        title="Uploads"
        prefix="/api/upload"
        endpoints={[
          { method: 'POST', path: '/image', desc: 'Upload image (multipart/form-data)', body: 'File upload' },
          { method: 'POST', path: '/file', desc: 'Upload file (multipart/form-data)', body: 'File upload' },
        ]}
      />
    </div>
  )
}

function WebSocketTab() {
  return (
    <div className="space-y-6">
      <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
        <h2 className="text-xl font-bold text-white mb-2">🔌 WebSocket Connection</h2>
        <p className="text-gray-400 mb-4">Connect to the WebSocket gateway for real-time events.</p>
        <div className="bg-gray-900 rounded-lg p-4 font-mono text-sm">
          <p className="text-green-400">ws://localhost:8000/ws?token=&lt;JWT_TOKEN&gt;</p>
        </div>
      </div>

      <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
        <h2 className="text-xl font-bold text-white mb-4">📤 Client → Server Events</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-700">
                <th className="text-left py-2 px-3 text-gray-400">Event</th>
                <th className="text-left py-2 px-3 text-gray-400">Payload</th>
                <th className="text-left py-2 px-3 text-gray-400">Description</th>
              </tr>
            </thead>
            <tbody className="text-gray-300">
              {[
                ['message:send', '{chat_id, content, attachments?, reply_to_id?}', 'Send a new message'],
                ['message:edit', '{message_id, content}', 'Edit an existing message'],
                ['message:delete', '{message_id}', 'Delete a message'],
                ['message:react', '{message_id, emoji}', 'Toggle emoji reaction'],
                ['message:pin', '{message_id}', 'Toggle message pin'],
                ['channel:create', '{name, description?, is_private?, topic?}', 'Create a channel'],
                ['channel:join', '{channel_id, invite_code?}', 'Join a channel'],
                ['channel:leave', '{channel_id}', 'Leave a channel'],
                ['channel:addMember', '{channel_id, user_id}', 'Add member (admin)'],
                ['channel:removeMember', '{channel_id, user_id}', 'Remove member (admin)'],
                ['channel:promoteAdmin', '{channel_id, user_id}', 'Promote to admin'],
                ['channel:demoteAdmin', '{channel_id, user_id}', 'Demote from admin'],
                ['channel:updateSettings', '{channel_id, ...settings}', 'Update channel settings'],
                ['typing:start', '{chat_id}', 'Start typing indicator'],
                ['typing:stop', '{chat_id}', 'Stop typing indicator'],
                ['status:update', '{status}', 'Update presence status'],
              ].map(([event, payload, desc]) => (
                <tr key={event} className="border-b border-gray-700/50">
                  <td className="py-2 px-3 font-mono text-yellow-400 text-xs">{event}</td>
                  <td className="py-2 px-3 font-mono text-gray-400 text-xs">{payload}</td>
                  <td className="py-2 px-3">{desc}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
        <h2 className="text-xl font-bold text-white mb-4">📥 Server → Client Events</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-700">
                <th className="text-left py-2 px-3 text-gray-400">Event</th>
                <th className="text-left py-2 px-3 text-gray-400">Description</th>
              </tr>
            </thead>
            <tbody className="text-gray-300">
              {[
                ['init', 'Initial data payload (users, channels, messages, pinnedIds)'],
                ['message:new', 'New message broadcast'],
                ['message:updated', 'Message edited'],
                ['message:deleted', 'Message deleted'],
                ['message:reaction', 'Reaction added/removed'],
                ['message:pinned', 'Message pin toggled'],
                ['channel:created', 'New channel created'],
                ['channel:updated', 'Channel settings/membership changed'],
                ['user:joined', 'User joined a channel'],
                ['user:left', 'User left a channel'],
                ['user:updated', 'User status/profile changed'],
                ['typing:update', 'Typing indicators changed'],
                ['channel:error', 'Permission/validation error'],
              ].map(([event, desc]) => (
                <tr key={event} className="border-b border-gray-700/50">
                  <td className="py-2 px-3 font-mono text-blue-400 text-xs">{event}</td>
                  <td className="py-2 px-3">{desc}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

function SchemaTab() {
  return (
    <div className="space-y-6">
      <SchemaTable
        title="User"
        fields={[
          ['id', 'UUID', 'Primary Key'],
          ['name', 'String(100)', 'Required, indexed'],
          ['email', 'String(255)', 'Unique, Required, indexed'],
          ['password_hash', 'String(255)', 'Required (bcrypt)'],
          ['avatar_url', 'String(500)', 'Optional'],
          ['status', 'Enum', 'online | busy | away | offline'],
          ['custom_status', 'String(200)', 'Optional'],
          ['bio', 'Text', 'Optional'],
          ['phone', 'String(20)', 'Optional'],
          ['is_bot', 'Boolean', 'Default: false'],
          ['created_at', 'Timestamp', 'Default: now()'],
        ]}
      />

      <SchemaTable
        title="Channel"
        fields={[
          ['id', 'UUID', 'Primary Key'],
          ['name', 'String(100)', 'Required, indexed'],
          ['description', 'Text', 'Optional'],
          ['is_private', 'Boolean', 'Default: false'],
          ['topic', 'String(200)', 'Optional'],
          ['created_at', 'Timestamp', 'Default: now()'],
          ['created_by', 'UUID FK → users', 'Required, indexed'],
          ['invite_code', 'String(50)', 'Optional, Unique'],
          ['only_admins_can_post', 'Boolean', 'Default: false'],
        ]}
      />

      <SchemaTable
        title="ChannelMember"
        fields={[
          ['channel_id', 'UUID FK → channels', 'Primary Key (composite)'],
          ['user_id', 'UUID FK → users', 'Primary Key (composite)'],
          ['is_admin', 'Boolean', 'Default: false'],
          ['joined_at', 'Timestamp', 'Default: now()'],
        ]}
      />

      <SchemaTable
        title="Message"
        fields={[
          ['id', 'UUID', 'Primary Key'],
          ['chat_id', 'String(255)', 'Channel UUID or dm:u1:u2, indexed'],
          ['chat_type', 'Enum', 'channel | dm, indexed'],
          ['sender_id', 'UUID FK → users', 'Required, indexed'],
          ['content', 'Text', 'Required'],
          ['timestamp', 'Timestamp', 'Default: now(), indexed'],
          ['edited_at', 'Timestamp', 'Optional'],
          ['is_pinned', 'Boolean', 'Default: false'],
          ['reply_to_id', 'UUID FK → messages', 'Optional (self-ref)'],
        ]}
      />

      <SchemaTable
        title="Attachment"
        fields={[
          ['id', 'UUID', 'Primary Key'],
          ['message_id', 'UUID FK → messages', 'Required, indexed'],
          ['name', 'String(255)', 'Required'],
          ['type', 'Enum', 'image | file'],
          ['url', 'String(1000)', 'Required'],
          ['size_bytes', 'Integer', 'Required'],
        ]}
      />

      <SchemaTable
        title="Reaction"
        fields={[
          ['id', 'UUID', 'Primary Key'],
          ['message_id', 'UUID FK → messages', 'Required, indexed'],
          ['user_id', 'UUID FK → users', 'Required, indexed'],
          ['emoji', 'String(50)', 'Required'],
        ]}
      />
    </div>
  )
}

// ==================== COMPONENTS ====================

function FeatureCard({ icon, title, description }: { icon: string; title: string; description: string }) {
  return (
    <div className="bg-gray-800 rounded-xl p-5 border border-gray-700 hover:border-green-500/50 transition-colors">
      <div className="text-2xl mb-2">{icon}</div>
      <h3 className="font-semibold text-white mb-1">{title}</h3>
      <p className="text-gray-400 text-sm">{description}</p>
    </div>
  )
}

function EndpointGroup({ title, prefix, endpoints }: {
  title: string
  prefix: string
  endpoints: { method: string; path: string; desc: string; body: string }[]
}) {
  return (
    <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
      <h3 className="text-lg font-bold text-white mb-1">{title}</h3>
      <p className="text-gray-500 text-sm mb-4 font-mono">{prefix}</p>
      <div className="space-y-2">
        {endpoints.map((ep, i) => (
          <div key={i} className="flex items-start gap-3 py-2 border-b border-gray-700/50 last:border-0">
            <span className={`px-2 py-0.5 rounded text-xs font-bold ${
              ep.method === 'GET' ? 'bg-blue-500/20 text-blue-400' :
              ep.method === 'POST' ? 'bg-green-500/20 text-green-400' :
              ep.method === 'PUT' ? 'bg-yellow-500/20 text-yellow-400' :
              'bg-red-500/20 text-red-400'
            }`}>
              {ep.method}
            </span>
            <div className="flex-1">
              <code className="text-sm text-gray-200">{prefix}{ep.path}</code>
              <p className="text-gray-400 text-xs mt-0.5">{ep.desc}</p>
              {ep.body && <p className="text-gray-500 text-xs font-mono mt-0.5">{ep.body}</p>}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

function SchemaTable({ title, fields }: { title: string; fields: string[][] }) {
  return (
    <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
      <h3 className="text-lg font-bold text-white mb-4">{title}</h3>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-700">
              <th className="text-left py-2 px-3 text-gray-400">Field</th>
              <th className="text-left py-2 px-3 text-gray-400">Type</th>
              <th className="text-left py-2 px-3 text-gray-400">Notes</th>
            </tr>
          </thead>
          <tbody>
            {fields.map(([field, type, notes]) => (
              <tr key={field} className="border-b border-gray-700/50">
                <td className="py-2 px-3 font-mono text-green-400">{field}</td>
                <td className="py-2 px-3 font-mono text-yellow-400 text-xs">{type}</td>
                <td className="py-2 px-3 text-gray-400">{notes}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default App
