# Dive Coder v19.5 - Automated Setup Guide

## Overview

The Dive Coder v19.5 Automated Setup system allows you to quickly set up any GitHub project with full Dive Coder integration. Simply provide a GitHub URL, and the system will automatically:

- Clone the repository
- Detect project type
- Create backend API
- Configure environment
- Install dependencies
- Set up Docker support
- Generate documentation

---

## Quick Start

### One-Line Setup

```bash
/home/ubuntu/dive-auto-setup.sh https://github.com/your-username/your-project
```

That's it! The setup will complete automatically.

---

## Prerequisites

The setup script requires:
- Git
- Python 3.11+
- Node.js 14+
- npm or yarn
- curl
- Basic Unix tools

All missing dependencies are automatically installed.

---

## Detailed Usage

### Step 1: Run Setup Script

```bash
/home/ubuntu/dive-auto-setup.sh <GITHUB_URL>
```

**Example:**
```bash
/home/ubuntu/dive-auto-setup.sh https://github.com/duclm1x1/dive-coder-companion
```

### Step 2: Monitor Setup Progress

The script will display progress with color-coded output:
- 🔵 `[INFO]` - Information messages
- 🟢 `[✓]` - Success messages
- 🔴 `[✗]` - Error messages
- 🟡 `[!]` - Warning messages

### Step 3: Configure Environment

After setup completes, configure your environment:

```bash
cd /home/ubuntu/dive-projects/your-project
nano .env
```

Update these key variables:
```env
DIVE_CODER_API_URL=http://localhost:8000
OPENAI_API_KEY=sk-your-key
ANTHROPIC_API_KEY=sk-ant-your-key
```

### Step 4: Start Services

```bash
cd /home/ubuntu/dive-projects/your-project
chmod +x start-services.sh
./start-services.sh
```

### Step 5: Verify Setup

Check if services are running:

```bash
# Check backend health
curl http://localhost:8000/api/health

# View API documentation
open http://localhost:8000/docs
```

---

## What Gets Created

### Directory Structure

```
/home/ubuntu/dive-projects/
└── your-project/
    ├── backend/
    │   ├── main.py              # FastAPI backend
    │   └── requirements.txt      # Python dependencies
    ├── src/                      # Your frontend source
    ├── .env                      # Environment variables
    ├── .env.example             # Example environment
    ├── .gitignore               # Git ignore rules
    ├── Dockerfile               # Docker configuration
    ├── docker-compose.yml       # Docker Compose
    ├── start-services.sh        # Startup script
    ├── DIVE_SETUP_GUIDE.md     # Setup documentation
    ├── SETUP_REPORT.json       # Setup report
    └── package.json             # Node.js dependencies
```

### Backend API

A FastAPI application is created with these endpoints:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/health` | GET | Health check |
| `/api/status` | GET | System status |
| `/api/tasks` | POST | Create task |
| `/api/info` | GET | API information |
| `/docs` | GET | API documentation |

### Environment Configuration

A `.env` file is created with these variables:

```env
# Dive Coder Configuration
DIVE_CODER_API_URL=http://localhost:8000
DIVE_CODER_API_KEY=your-secret-key

# LLM Providers
OPENAI_API_KEY=sk-your-key
ANTHROPIC_API_KEY=sk-ant-your-key

# Database
DATABASE_URL=postgresql://user:password@localhost/divedb
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-key

# Frontend
FRONTEND_URL=http://localhost:3000
VITE_API_URL=http://localhost:8000

# Environment
NODE_ENV=development
DEBUG=true
```

### Startup Script

A `start-services.sh` script is created to start all services:

```bash
./start-services.sh
```

This will start:
- Backend API (port 8000)
- Dive Coder service (if available)
- Frontend (port 3000)

### Docker Support

Docker files are created for containerization:

- `Dockerfile` - Container configuration
- `docker-compose.yml` - Multi-container setup

---

## Advanced Usage

### Using the Setup Helper

For advanced operations, use the Python helper script:

```bash
python3 /home/ubuntu/dive-setup-helper.py <project-dir> [options]
```

**Options:**

```bash
# Validate project structure
python3 /home/ubuntu/dive-setup-helper.py /path/to/project --validate

# Check port availability
python3 /home/ubuntu/dive-setup-helper.py /path/to/project --check-ports

# Install dependencies
python3 /home/ubuntu/dive-setup-helper.py /path/to/project --install-deps

# Test backend connection
python3 /home/ubuntu/dive-setup-helper.py /path/to/project --test-backend

# Run full setup
python3 /home/ubuntu/dive-setup-helper.py /path/to/project --full-setup

# Update environment variables
python3 /home/ubuntu/dive-setup-helper.py /path/to/project \
  --update-env '{"OPENAI_API_KEY":"sk-..."}'
```

### Manual Configuration

If you need to manually configure after setup:

1. **Update .env file:**
   ```bash
   nano .env
   ```

2. **Install dependencies:**
   ```bash
   pip3 install -r backend/requirements.txt
   npm install
   ```

3. **Start services:**
   ```bash
   ./start-services.sh
   ```

### Docker Deployment

**Build Docker image:**
```bash
docker build -t dive-coder-app .
```

**Run with Docker:**
```bash
docker run -p 8000:8000 -p 3000:3000 dive-coder-app
```

**Use Docker Compose:**
```bash
docker-compose up
```

---

## API Usage Examples

### Health Check

```bash
curl http://localhost:8000/api/health
```

Response:
```json
{
  "status": "healthy",
  "version": "19.5",
  "dive_coder_available": true,
  "timestamp": "2026-02-03T12:00:00"
}
```

### Get System Status

```bash
curl http://localhost:8000/api/status
```

Response:
```json
{
  "connected": true,
  "status": {
    "num_agents": 8,
    "total_capabilities": 416,
    "is_active": true
  },
  "timestamp": "2026-02-03T12:00:00"
}
```

### Create Task

```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Generate a Python function to calculate factorial",
    "priority": 8,
    "complexity": 5
  }'
```

Response:
```json
{
  "task_id": "TASK_20260203_120000",
  "status": "success",
  "timestamp": "2026-02-03T12:00:00"
}
```

---

## Troubleshooting

### Port Already in Use

If port 8000 is already in use:

```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port in start-services.sh
```

### Python Dependencies Error

```bash
# Clear pip cache
pip3 cache purge

# Reinstall dependencies
pip3 install --upgrade -r backend/requirements.txt
```

### Node Dependencies Error

```bash
# Clear npm cache
npm cache clean --force

# Remove node_modules
rm -rf node_modules package-lock.json

# Reinstall
npm install
```

### Backend Not Starting

```bash
# Check if port is available
lsof -i :8000

# Check logs
tail -f /tmp/dive-setup-*.log

# Try starting manually
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### Dive Coder Not Available

If Dive Coder is not available:

1. Ensure Dive Coder v19.5 is installed at `/home/ubuntu/dive-coder-v19-5`
2. Check if service is running: `ps aux | grep dive`
3. Check logs: `tail -f /tmp/dive-coder-v19.5.log`

---

## File Locations

| File | Location |
|------|----------|
| Setup Script | `/home/ubuntu/dive-auto-setup.sh` |
| Helper Script | `/home/ubuntu/dive-setup-helper.py` |
| Projects Directory | `/home/ubuntu/dive-projects/` |
| Setup Logs | `/tmp/dive-setup-*.log` |
| Dive Coder | `/home/ubuntu/dive-coder-v19-5/` |

---

## Setup Report

After setup completes, a `SETUP_REPORT.json` file is generated containing:

```json
{
  "setup_timestamp": "2026-02-03T12:00:00Z",
  "project_name": "your-project",
  "project_type": "node",
  "project_directory": "/home/ubuntu/dive-projects/your-project",
  "github_url": "https://github.com/your-username/your-project",
  "setup_status": "completed",
  "components": {
    "backend_api": {
      "status": "created",
      "location": "/home/ubuntu/dive-projects/your-project/backend",
      "port": 8000
    },
    "environment_config": {
      "status": "created",
      "location": "/home/ubuntu/dive-projects/your-project/.env"
    },
    "dependencies": {
      "status": "installed",
      "python": "installed",
      "nodejs": "installed"
    }
  },
  "next_steps": [
    "1. Configure .env file with your API keys",
    "2. Run: chmod +x start-services.sh",
    "3. Run: ./start-services.sh",
    "4. Access API at http://localhost:8000"
  ]
}
```

---

## Environment Variables Reference

### Dive Coder Configuration

| Variable | Description | Example |
|----------|-------------|---------|
| `DIVE_CODER_API_URL` | Backend API URL | `http://localhost:8000` |
| `DIVE_CODER_API_KEY` | API authentication key | `your-secret-key` |

### LLM Providers

| Variable | Description | Example |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | `sk-...` |
| `ANTHROPIC_API_KEY` | Anthropic API key | `sk-ant-...` |

### Database

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection | `postgresql://user:pass@localhost/db` |
| `SUPABASE_URL` | Supabase project URL | `https://project.supabase.co` |
| `SUPABASE_KEY` | Supabase API key | `your-key` |

### Frontend

| Variable | Description | Example |
|----------|-------------|---------|
| `FRONTEND_URL` | Frontend URL | `http://localhost:3000` |
| `VITE_API_URL` | Vite API URL | `http://localhost:8000` |

### Environment

| Variable | Description | Example |
|----------|-------------|---------|
| `NODE_ENV` | Node environment | `development` or `production` |
| `DEBUG` | Debug mode | `true` or `false` |

---

## Common Workflows

### Setup and Start

```bash
# 1. Run setup
/home/ubuntu/dive-auto-setup.sh https://github.com/your-username/your-project

# 2. Configure environment
cd /home/ubuntu/dive-projects/your-project
nano .env

# 3. Start services
chmod +x start-services.sh
./start-services.sh

# 4. Access services
open http://localhost:8000/docs
```

### Docker Deployment

```bash
# 1. Run setup
/home/ubuntu/dive-auto-setup.sh https://github.com/your-username/your-project

# 2. Build Docker image
cd /home/ubuntu/dive-projects/your-project
docker build -t my-app .

# 3. Run container
docker run -p 8000:8000 -p 3000:3000 my-app

# 4. Access services
open http://localhost:8000/docs
```

### Production Deployment

```bash
# 1. Run setup
/home/ubuntu/dive-auto-setup.sh https://github.com/your-username/your-project

# 2. Update environment for production
cd /home/ubuntu/dive-projects/your-project
nano .env
# Set NODE_ENV=production, DEBUG=false, etc.

# 3. Deploy to cloud
# (AWS, GCP, Azure, Heroku, etc.)

# 4. Monitor services
curl https://your-production-domain.com/api/health
```

---

## Support

For issues or questions:

1. **Check logs:**
   ```bash
   tail -f /tmp/dive-setup-*.log
   ```

2. **Review documentation:**
   ```bash
   cat /home/ubuntu/dive-projects/your-project/DIVE_SETUP_GUIDE.md
   ```

3. **Check API status:**
   ```bash
   curl http://localhost:8000/api/status
   ```

4. **View setup report:**
   ```bash
   cat /home/ubuntu/dive-projects/your-project/SETUP_REPORT.json
   ```

---

## Next Steps

After successful setup:

1. **Explore the API:** Visit http://localhost:8000/docs
2. **Create your first task:** Use the API to execute a task
3. **Customize the frontend:** Modify your project as needed
4. **Deploy to production:** Use Docker or cloud platform
5. **Monitor and scale:** Track performance and optimize

---

## Version Information

- **Dive Coder Version:** 19.5
- **Setup Script Version:** 1.0
- **Last Updated:** February 3, 2026

---

**Happy coding with Dive Coder v19.5!** 🚀
