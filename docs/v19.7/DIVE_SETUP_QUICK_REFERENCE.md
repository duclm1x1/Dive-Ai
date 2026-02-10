# Dive Coder v19.5 - Automated Setup Quick Reference

## One-Line Setup

```bash
/home/ubuntu/dive-auto-setup.sh https://github.com/your-username/your-project
```

---

## After Setup - Quick Start

```bash
# 1. Navigate to project
cd /home/ubuntu/dive-projects/your-project

# 2. Configure environment (optional)
nano .env

# 3. Start services
chmod +x start-services.sh
./start-services.sh

# 4. Access services
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
# Frontend: http://localhost:3000
```

---

## Common Commands

### Setup

| Command | Purpose |
|---------|---------|
| `/home/ubuntu/dive-auto-setup.sh <url>` | Automatic setup from GitHub |
| `python3 /home/ubuntu/dive-setup-helper.py <dir> --full-setup` | Manual full setup |
| `python3 /home/ubuntu/dive-setup-helper.py <dir> --validate` | Validate setup |

### Services

| Command | Purpose |
|---------|---------|
| `./start-services.sh` | Start all services |
| `curl http://localhost:8000/api/health` | Check backend health |
| `curl http://localhost:8000/api/status` | Get system status |

### Configuration

| Command | Purpose |
|---------|---------|
| `nano .env` | Edit environment variables |
| `pip3 install -r backend/requirements.txt` | Install Python deps |
| `npm install` | Install Node deps |

### Docker

| Command | Purpose |
|---------|---------|
| `docker build -t app .` | Build Docker image |
| `docker run -p 8000:8000 app` | Run container |
| `docker-compose up` | Start with Docker Compose |

### Troubleshooting

| Command | Purpose |
|---------|---------|
| `lsof -i :8000` | Check port 8000 |
| `tail -f /tmp/dive-setup-*.log` | View setup logs |
| `ps aux \| grep python` | Check running processes |

---

## Project Structure

```
your-project/
├── backend/
│   ├── main.py              # FastAPI backend
│   └── requirements.txt      # Python dependencies
├── src/                      # Frontend source
├── .env                      # Environment variables
├── Dockerfile                # Docker config
├── docker-compose.yml        # Docker Compose
├── start-services.sh         # Startup script
├── DIVE_SETUP_GUIDE.md      # Full documentation
└── SETUP_REPORT.json        # Setup report
```

---

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/health` | GET | Health check |
| `/api/status` | GET | System status |
| `/api/tasks` | POST | Create task |
| `/api/info` | GET | API info |
| `/docs` | GET | API documentation |

---

## Environment Variables (Key)

```env
DIVE_CODER_API_URL=http://localhost:8000
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
NODE_ENV=development
DEBUG=true
```

---

## File Locations

| File | Location |
|------|----------|
| Setup Script | `/home/ubuntu/dive-auto-setup.sh` |
| Helper Script | `/home/ubuntu/dive-setup-helper.py` |
| Projects | `/home/ubuntu/dive-projects/` |
| Dive Coder | `/home/ubuntu/dive-coder-v19-5/` |
| Logs | `/tmp/dive-setup-*.log` |

---

## Workflow Examples

### Basic Setup

```bash
# 1. Setup
/home/ubuntu/dive-auto-setup.sh https://github.com/user/project

# 2. Start
cd /home/ubuntu/dive-projects/project
./start-services.sh

# 3. Use
curl http://localhost:8000/api/health
```

### With Configuration

```bash
# 1. Setup
/home/ubuntu/dive-auto-setup.sh https://github.com/user/project

# 2. Configure
cd /home/ubuntu/dive-projects/project
nano .env

# 3. Start
./start-services.sh

# 4. Verify
curl http://localhost:8000/api/status
```

### Docker Deployment

```bash
# 1. Setup
/home/ubuntu/dive-auto-setup.sh https://github.com/user/project

# 2. Build
cd /home/ubuntu/dive-projects/project
docker build -t myapp .

# 3. Run
docker run -p 8000:8000 myapp

# 4. Access
open http://localhost:8000/docs
```

---

## Troubleshooting Quick Fixes

| Issue | Solution |
|-------|----------|
| Port 8000 in use | `lsof -i :8000` then `kill -9 <PID>` |
| Python deps fail | `pip3 cache purge && pip3 install -r requirements.txt` |
| Node deps fail | `rm -rf node_modules && npm install` |
| Backend not starting | Check logs: `tail -f /tmp/dive-setup-*.log` |
| API not responding | Verify running: `curl http://localhost:8000/api/health` |

---

## Next Steps

1. ✅ Run setup script
2. ✅ Configure environment
3. ✅ Start services
4. ✅ Test API
5. ✅ Deploy

---

**Setup Time:** ~2-5 minutes  
**Difficulty:** Easy  
**Support:** See DIVE_AUTO_SETUP_GUIDE.md
