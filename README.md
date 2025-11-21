# Bot Management Dashboard

A modern, production-ready web dashboard for managing Telegram userbots, Telegram bots, and Discord bots from a single, beautiful interface.

![Dashboard Preview](https://via.placeholder.com/800x400?text=Bot+Management+Dashboard)

## ✨ Features

- **Multi-Platform Support**: Manage Telegram userbots, Telegram bots, and Discord bots
- **Real-Time Monitoring**: Live log streaming via WebSocket, real-time system statistics
- **Process Management**: Start, stop, restart bots with one click
- **Resource Tracking**: Monitor CPU, RAM usage per bot and system-wide
- **Auto-Restart**: Automatic bot restart on crashes with configurable backoff
- **Beautiful UI**: Dark theme with glassmorphism effects, built with Next.js 14 and Tailwind CSS
- **Responsive Design**: Works perfectly on mobile, tablet, and desktop
- **RESTful API**: Comprehensive API with OpenAPI documentation
- **Docker Ready**: Full Docker and Docker Compose support for easy deployment
- **Production Ready**: Security best practices, proper error handling, logging

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern, fast web framework for Python
- **SQLAlchemy** - SQL toolkit and ORM
- **SQLite/PostgreSQL** - Database (SQLite for dev, PostgreSQL for production)
- **WebSockets** - Real-time communication
- **Uvicorn** - ASGI server
- **JWT** - Authentication
- **Psutil** - System and process monitoring

### Frontend
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type safety
- **Tailwind CSS** - Utility-first CSS framework
- **shadcn/ui** - High-quality React components
- **TanStack Query** - Data fetching and caching
- **Axios** - HTTP client
- **Recharts** - Charts and graphs
- **Sonner** - Toast notifications

### Infrastructure
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration
- **Nginx** - Reverse proxy and load balancer

## 📋 Prerequisites

- **Python 3.11+** for backend development
- **Node.js 20+** for frontend development
- **Docker & Docker Compose** (optional, for containerized deployment)
- **Git** for version control

## 🚀 Quick Start with Docker

The fastest way to get started:

```bash
# Clone the repository
git clone <repository-url>
cd bot-dashboard

# Copy environment file
cp backend/.env.example backend/.env

# Generate a secure secret key
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
# Add the generated key to backend/.env as SECRET_KEY

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

Access the dashboard at **http://localhost:3000**

API documentation available at **http://localhost:8000/docs**

## 💻 Local Development Setup

### Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Initialize database
python -c "from app.database import init_db; init_db()"

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at http://localhost:8000

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Copy environment file
cp .env.local.example .env.local

# Start development server
npm run dev
```

Frontend will be available at http://localhost:3000

### Installing Bot Dependencies

```bash
cd bots/examples

# Install bot dependencies
pip install -r requirements.txt
```

## 📱 Adding Your First Bot

### Via Web Interface

1. Open the dashboard at http://localhost:3000
2. Click "Add Bot" button
3. Fill in bot details:
   - **Name**: A unique name for your bot
   - **Type**: Select bot type (Telegram Userbot, Telegram Bot, or Discord Bot)
   - **Configuration**: Enter bot credentials (tokens, API keys, etc.)
   - **Auto-restart**: Enable/disable automatic restart on crash
4. Click "Create"
5. Start the bot using the "Start" button on the bot card

### Via API

```bash
curl -X POST http://localhost:8000/api/v1/bots \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Telegram Bot",
    "type": "telegram_bot",
    "config": {
      "token": "YOUR_BOT_TOKEN_HERE"
    },
    "auto_restart": true
  }'
```

## 🤖 Bot Configuration Examples

### Telegram Bot

```json
{
  "name": "My Telegram Bot",
  "type": "telegram_bot",
  "config": {
    "token": "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
  },
  "auto_restart": true
}
```

### Telegram Userbot

```json
{
  "name": "My Telegram Userbot",
  "type": "telegram_userbot",
  "config": {
    "api_id": "12345678",
    "api_hash": "0123456789abcdef0123456789abcdef",
    "phone": "+1234567890",
    "session_name": "my_session"
  },
  "auto_restart": true
}
```

### Discord Bot

```json
{
  "name": "My Discord Bot",
  "type": "discord_bot",
  "config": {
    "token": "YOUR_DISCORD_BOT_TOKEN",
    "prefix": "!"
  },
  "auto_restart": true
}
```

## 🔧 Configuration

### Environment Variables

#### Backend (.env)

```bash
# Database
DATABASE_URL=sqlite:///./data/bot_dashboard.db

# Security
SECRET_KEY=your-secret-key-here-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Logging
LOG_LEVEL=INFO
MAX_LOG_SIZE_MB=10

# Bot Management
AUTO_RESTART_BOTS=true
STATS_COLLECTION_INTERVAL=5
BOT_PROCESS_CHECK_INTERVAL=5
BOT_RESTART_BACKOFF_SECONDS=10
```

#### Frontend (.env.local)

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

## 📖 API Documentation

### Authentication

```bash
# Register
POST /api/v1/auth/register
{
  "username": "admin",
  "email": "admin@example.com",
  "password": "secure_password"
}

# Login
POST /api/v1/auth/login
{
  "username": "admin",
  "password": "secure_password"
}
```

### Bot Management

```bash
# List all bots
GET /api/v1/bots?page=1&page_size=20

# Get bot details
GET /api/v1/bots/{bot_id}

# Create bot
POST /api/v1/bots

# Update bot
PUT /api/v1/bots/{bot_id}

# Delete bot
DELETE /api/v1/bots/{bot_id}

# Start bot
POST /api/v1/bots/{bot_id}/start

# Stop bot
POST /api/v1/bots/{bot_id}/stop

# Restart bot
POST /api/v1/bots/{bot_id}/restart

# Get bot status
GET /api/v1/bots/{bot_id}/status

# Get bot logs
GET /api/v1/bots/{bot_id}/logs?page=1
```

### Statistics

```bash
# System stats
GET /api/v1/stats/system

# Bot stats
GET /api/v1/stats/bots/{bot_id}

# All bots stats
GET /api/v1/stats/bots
```

### WebSocket Endpoints

```bash
# Real-time logs
WS /ws/logs/{bot_id}

# Real-time stats
WS /ws/stats
```

Full API documentation: http://localhost:8000/docs

## 🐳 Production Deployment

### Using Docker Compose

```bash
# Copy production compose file
cp docker-compose.prod.yml docker-compose.yml

# Set environment variables
export SECRET_KEY="your-production-secret-key"
export CORS_ORIGINS="https://yourdomain.com"
export API_URL="https://yourdomain.com"

# Start services
docker-compose up -d

# View logs
docker-compose logs -f
```

### Manual Deployment

1. **Backend**:
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
   ```

2. **Frontend**:
   ```bash
   cd frontend
   npm install
   npm run build
   npm start
   ```

3. **Nginx**: Configure nginx as reverse proxy (see nginx/nginx.conf)

## 🔒 Security Considerations

- **Change default SECRET_KEY** in production
- **Use HTTPS** in production (configure SSL certificates in nginx)
- **Enable rate limiting** (configured in nginx)
- **Implement authentication** for production use
- **Secure WebSocket connections** (use wss:// in production)
- **Keep dependencies updated** regularly
- **Use environment variables** for all secrets
- **Enable firewall** on production servers
- **Regular backups** of database

## 📊 Monitoring

The dashboard provides real-time monitoring:

- **System Metrics**: CPU, RAM, disk, network usage
- **Bot Status**: Running, stopped, crashed states
- **Process Info**: PIDs, uptime, resource usage per bot
- **Live Logs**: Real-time log streaming via WebSocket
- **Statistics**: Aggregated metrics across all bots

## 🛠️ Development

### Using Makefile

```bash
# View available commands
make help

# Start development environment
make dev

# Install dependencies
make install

# Run tests
make test

# Format code
make format

# Lint code
make lint
```

## 📝 Troubleshooting

### Bot won't start

- Check bot credentials in configuration
- Verify bot dependencies are installed
- Check logs for error messages
- Ensure API tokens are valid

### WebSocket connection fails

- Verify CORS settings
- Check firewall rules
- Ensure WebSocket URL is correct
- Check nginx configuration

### Database errors

- Ensure database file permissions
- Check DATABASE_URL environment variable
- Run database migrations
- Verify disk space

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/)
- [Next.js](https://nextjs.org/)
- [shadcn/ui](https://ui.shadcn.com/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Telethon](https://docs.telethon.dev/)
- [python-telegram-bot](https://python-telegram-bot.org/)
- [discord.py](https://discordpy.readthedocs.io/)

---

**Made with ❤️ for bot developers**
