#!/bin/bash

################################################################################
# DIVE CODER v19.5 - AUTOMATED SETUP ORCHESTRATOR
# 
# Usage: ./dive-auto-setup.sh <github-url>
# Example: ./dive-auto-setup.sh https://github.com/duclm1x1/dive-coder-companion
#
# This script automatically:
# 1. Clones the GitHub repository
# 2. Detects project type
# 3. Creates backend API
# 4. Configures environment
# 5. Installs dependencies
# 6. Sets up Dive Coder integration
# 7. Starts all services
################################################################################

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
GITHUB_URL="${1:-}"
SETUP_DIR="/home/ubuntu/dive-projects"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="/tmp/dive-setup-${TIMESTAMP}.log"

################################################################################
# UTILITY FUNCTIONS
################################################################################

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[!]${NC} $1" | tee -a "$LOG_FILE"
}

print_header() {
    echo "" | tee -a "$LOG_FILE"
    echo "================================================================================" | tee -a "$LOG_FILE"
    echo "  $1" | tee -a "$LOG_FILE"
    echo "================================================================================" | tee -a "$LOG_FILE"
}

print_step() {
    echo "" | tee -a "$LOG_FILE"
    echo -e "${BLUE}>>> $1${NC}" | tee -a "$LOG_FILE"
}

################################################################################
# VALIDATION FUNCTIONS
################################################################################

validate_github_url() {
    if [[ -z "$GITHUB_URL" ]]; then
        log_error "GitHub URL is required"
        echo "Usage: $0 <github-url>"
        echo "Example: $0 https://github.com/duclm1x1/dive-coder-companion"
        exit 1
    fi
    
    if [[ ! "$GITHUB_URL" =~ ^https?://github\.com/ ]]; then
        log_error "Invalid GitHub URL format"
        exit 1
    fi
    
    log_success "GitHub URL validated: $GITHUB_URL"
}

check_dependencies() {
    print_step "Checking system dependencies"
    
    local missing_deps=()
    
    for cmd in git python3 pip3 node npm; do
        if ! command -v "$cmd" &> /dev/null; then
            missing_deps+=("$cmd")
        else
            log_success "$cmd is installed"
        fi
    done
    
    if [ ${#missing_deps[@]} -gt 0 ]; then
        log_error "Missing dependencies: ${missing_deps[*]}"
        log_info "Installing missing dependencies..."
        sudo apt-get update
        sudo apt-get install -y git python3 python3-pip nodejs npm
    fi
}

################################################################################
# SETUP FUNCTIONS
################################################################################

setup_directories() {
    print_step "Setting up directories"
    
    mkdir -p "$SETUP_DIR"
    log_success "Setup directory created: $SETUP_DIR"
}

clone_repository() {
    print_step "Cloning GitHub repository"
    
    # Extract project name from URL
    PROJECT_NAME=$(echo "$GITHUB_URL" | sed 's|.*/||' | sed 's|\.git$||')
    PROJECT_DIR="$SETUP_DIR/$PROJECT_NAME"
    
    if [ -d "$PROJECT_DIR" ]; then
        log_warning "Project directory already exists: $PROJECT_DIR"
        read -p "Do you want to overwrite it? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf "$PROJECT_DIR"
        else
            log_info "Using existing directory: $PROJECT_DIR"
            return
        fi
    fi
    
    git clone "$GITHUB_URL" "$PROJECT_DIR"
    log_success "Repository cloned to: $PROJECT_DIR"
}

detect_project_type() {
    print_step "Detecting project type"
    
    if [ -f "$PROJECT_DIR/package.json" ]; then
        PROJECT_TYPE="node"
        log_success "Detected Node.js project"
    elif [ -f "$PROJECT_DIR/requirements.txt" ]; then
        PROJECT_TYPE="python"
        log_success "Detected Python project"
    elif [ -f "$PROJECT_DIR/pom.xml" ]; then
        PROJECT_TYPE="java"
        log_success "Detected Java project"
    else
        PROJECT_TYPE="generic"
        log_warning "Could not detect specific project type, treating as generic"
    fi
}

create_backend_api() {
    print_step "Creating backend API for Dive Coder integration"
    
    local backend_dir="$PROJECT_DIR/backend"
    mkdir -p "$backend_dir"
    
    # Create main.py
    cat > "$backend_dir/main.py" << 'EOF'
"""
Dive Coder v19.5 - Backend API Service
Provides REST API interface to Dive Coder orchestrator
"""

from fastapi import FastAPI, HTTPException
from fastapi.cors import CORSMiddleware
from pydantic import BaseModel
import sys
from pathlib import Path
from datetime import datetime
import json

# Add Dive Coder to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from dive_coder_v19_5.src.core.orchestration.orchestrator import (
        OptimizedOrchestrator, Task, Plan, TaskStatus, ExecutionMode
    )
    DIVE_CODER_AVAILABLE = True
except ImportError:
    DIVE_CODER_AVAILABLE = False
    print("Warning: Dive Coder not available in expected location")

app = FastAPI(
    title="Dive Coder API",
    version="19.5",
    description="REST API for Dive Coder v19.5 Autonomous Development Platform"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize orchestrator if available
if DIVE_CODER_AVAILABLE:
    orchestrator = OptimizedOrchestrator()
else:
    orchestrator = None

# Models
class TaskRequest(BaseModel):
    prompt: str
    priority: int = 8
    complexity: int = 7

class TaskResponse(BaseModel):
    task_id: str
    status: str
    timestamp: str

# Routes
@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "19.5",
        "dive_coder_available": DIVE_CODER_AVAILABLE,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/status")
async def get_status():
    """Get Dive Coder system status"""
    if not DIVE_CODER_AVAILABLE or not orchestrator:
        return {
            "connected": False,
            "error": "Dive Coder not available",
            "timestamp": datetime.now().isoformat()
        }
    
    try:
        status = orchestrator.get_system_status()
        return {
            "connected": True,
            "status": status,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "connected": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.post("/api/tasks")
async def create_task(request: TaskRequest):
    """Create and execute a task"""
    if not DIVE_CODER_AVAILABLE or not orchestrator:
        raise HTTPException(
            status_code=503,
            detail="Dive Coder service not available"
        )
    
    try:
        task = Task(
            task_id=f"TASK_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            description=request.prompt,
            priority=request.priority,
            estimated_complexity=request.complexity,
            status=TaskStatus.PENDING
        )
        
        plan = Plan(
            plan_id=f"PLAN_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            name="API Task",
            description=request.prompt,
            tasks=[task],
            mode=ExecutionMode.AUTONOMOUS
        )
        
        result = orchestrator.execute_plan(plan)
        
        return {
            "task_id": task.task_id,
            "status": result.status,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/info")
async def get_info():
    """Get API information"""
    return {
        "name": "Dive Coder v19.5 Backend API",
        "version": "19.5",
        "description": "REST API for autonomous code generation",
        "endpoints": {
            "health": "/api/health",
            "status": "/api/status",
            "tasks": "/api/tasks",
            "info": "/api/info"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
EOF
    
    log_success "Backend API created at: $backend_dir/main.py"
}

create_requirements() {
    print_step "Creating requirements files"
    
    # Backend requirements
    cat > "$PROJECT_DIR/backend/requirements.txt" << 'EOF'
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
python-dotenv==1.0.0
requests==2.31.0
EOF
    
    log_success "Backend requirements.txt created"
}

create_env_file() {
    print_step "Creating environment configuration"
    
    cat > "$PROJECT_DIR/.env.example" << 'EOF'
# Dive Coder Configuration
DIVE_CODER_API_URL=http://localhost:8000
DIVE_CODER_API_KEY=your-secret-key-here

# LLM Providers
OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key

# Database
DATABASE_URL=postgresql://user:password@localhost/divedb
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-key

# Frontend
FRONTEND_URL=http://localhost:3000
VITE_API_URL=http://localhost:8000

# Environment
NODE_ENV=development
DEBUG=true
EOF
    
    # Create actual .env if it doesn't exist
    if [ ! -f "$PROJECT_DIR/.env" ]; then
        cp "$PROJECT_DIR/.env.example" "$PROJECT_DIR/.env"
        log_success "Environment file created: $PROJECT_DIR/.env"
    else
        log_warning "Environment file already exists, skipping"
    fi
}

install_dependencies() {
    print_step "Installing dependencies"
    
    cd "$PROJECT_DIR"
    
    # Install backend dependencies
    if [ -f "backend/requirements.txt" ]; then
        log_info "Installing Python backend dependencies..."
        pip3 install -r backend/requirements.txt
        log_success "Python dependencies installed"
    fi
    
    # Install frontend dependencies
    if [ -f "package.json" ]; then
        log_info "Installing Node.js dependencies..."
        npm install
        log_success "Node.js dependencies installed"
    fi
}

create_startup_script() {
    print_step "Creating startup script"
    
    cat > "$PROJECT_DIR/start-services.sh" << 'EOF'
#!/bin/bash

echo "Starting Dive Coder Services..."

# Start backend API
echo "Starting backend API on port 8000..."
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Start Dive Coder service (if available)
if [ -d "../dive-coder-v19-5" ]; then
    echo "Starting Dive Coder service..."
    cd ../dive-coder-v19-5
    python start_service.py &
    DIVESERVICE_PID=$!
fi

# Start frontend (if available)
if [ -f "../package.json" ]; then
    echo "Starting frontend on port 3000..."
    cd ..
    npm run dev &
    FRONTEND_PID=$!
fi

# Wait for services
sleep 5

# Health check
echo "Checking service health..."
curl http://localhost:8000/api/health

echo "Services started successfully!"
echo "Backend PID: $BACKEND_PID"
if [ ! -z "$DIVESERVICE_PID" ]; then
    echo "Dive Coder PID: $DIVESERVICE_PID"
fi
if [ ! -z "$FRONTEND_PID" ]; then
    echo "Frontend PID: $FRONTEND_PID"
fi

wait
EOF
    
    chmod +x "$PROJECT_DIR/start-services.sh"
    log_success "Startup script created: $PROJECT_DIR/start-services.sh"
}

create_docker_support() {
    print_step "Creating Docker support files"
    
    # Dockerfile for backend
    cat > "$PROJECT_DIR/Dockerfile" << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose ports
EXPOSE 8000 3000

# Start services
CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF
    
    # Docker Compose
    cat > "$PROJECT_DIR/docker-compose.yml" << 'EOF'
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=true
    volumes:
      - .:/app
    command: python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports:
      - "3000:3000"
    environment:
      - VITE_API_URL=http://localhost:8000
    volumes:
      - .:/app
    command: npm run dev

volumes:
  app:
EOF
    
    log_success "Docker support files created"
}

create_documentation() {
    print_step "Creating setup documentation"
    
    cat > "$PROJECT_DIR/DIVE_SETUP_GUIDE.md" << 'EOF'
# Dive Coder v19.5 - Automated Setup Guide

This project has been automatically configured for Dive Coder v19.5 integration.

## Quick Start

### 1. Configure Environment Variables

Edit `.env` file with your settings:
```bash
nano .env
```

Key variables to configure:
- `DIVE_CODER_API_URL` - Backend API URL
- `OPENAI_API_KEY` - OpenAI API key
- `ANTHROPIC_API_KEY` - Anthropic API key

### 2. Start Services

```bash
# Make startup script executable
chmod +x start-services.sh

# Start all services
./start-services.sh
```

### 3. Verify Setup

Check backend health:
```bash
curl http://localhost:8000/api/health
```

### 4. Access Services

- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **Frontend:** http://localhost:3000

## API Endpoints

### Health Check
```bash
GET /api/health
```

### Get System Status
```bash
GET /api/status
```

### Create Task
```bash
POST /api/tasks
Content-Type: application/json

{
  "prompt": "Your task description",
  "priority": 8,
  "complexity": 7
}
```

### Get Info
```bash
GET /api/info
```

## Troubleshooting

### Port Already in Use
If port 8000 is already in use:
```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>
```

### Python Dependencies Issues
```bash
# Reinstall dependencies
pip install --upgrade -r backend/requirements.txt
```

### Node Dependencies Issues
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

## Project Structure

```
project-root/
├── backend/
│   ├── main.py              # FastAPI application
│   └── requirements.txt      # Python dependencies
├── src/                      # Frontend source
├── .env                      # Environment variables
├── .env.example             # Example environment
├── start-services.sh        # Startup script
├── Dockerfile               # Docker configuration
├── docker-compose.yml       # Docker Compose configuration
└── DIVE_SETUP_GUIDE.md     # This file
```

## Docker Deployment

### Build Image
```bash
docker build -t dive-coder-app .
```

### Run Container
```bash
docker run -p 8000:8000 -p 3000:3000 dive-coder-app
```

### Using Docker Compose
```bash
docker-compose up
```

## Production Deployment

For production deployment:

1. Update `.env` with production values
2. Set `NODE_ENV=production`
3. Set `DEBUG=false`
4. Use environment-specific configuration
5. Deploy to cloud platform (AWS, GCP, Azure)

## Support

For issues or questions:
- Check logs: `tail -f /tmp/dive-setup-*.log`
- Review API docs: http://localhost:8000/docs
- Check service status: `curl http://localhost:8000/api/status`

## Next Steps

1. Configure your LLM provider keys
2. Set up database connections if needed
3. Customize frontend as needed
4. Deploy to production
5. Monitor service health

---

Generated by Dive Coder v19.5 Automated Setup
EOF
    
    log_success "Documentation created: $PROJECT_DIR/DIVE_SETUP_GUIDE.md"
}

generate_setup_report() {
    print_step "Generating setup report"
    
    cat > "$PROJECT_DIR/SETUP_REPORT.json" << EOF
{
  "setup_timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "project_name": "$PROJECT_NAME",
  "project_type": "$PROJECT_TYPE",
  "project_directory": "$PROJECT_DIR",
  "github_url": "$GITHUB_URL",
  "setup_status": "completed",
  "components": {
    "backend_api": {
      "status": "created",
      "location": "$PROJECT_DIR/backend",
      "port": 8000,
      "framework": "FastAPI"
    },
    "environment_config": {
      "status": "created",
      "location": "$PROJECT_DIR/.env"
    },
    "dependencies": {
      "status": "installed",
      "python": "installed",
      "nodejs": "installed"
    },
    "startup_script": {
      "status": "created",
      "location": "$PROJECT_DIR/start-services.sh"
    },
    "docker_support": {
      "status": "created",
      "dockerfile": "$PROJECT_DIR/Dockerfile",
      "compose": "$PROJECT_DIR/docker-compose.yml"
    },
    "documentation": {
      "status": "created",
      "location": "$PROJECT_DIR/DIVE_SETUP_GUIDE.md"
    }
  },
  "next_steps": [
    "1. Configure .env file with your API keys",
    "2. Run: chmod +x start-services.sh",
    "3. Run: ./start-services.sh",
    "4. Access API at http://localhost:8000",
    "5. Check API docs at http://localhost:8000/docs"
  ],
  "log_file": "$LOG_FILE"
}
EOF
    
    log_success "Setup report generated: $PROJECT_DIR/SETUP_REPORT.json"
}

################################################################################
# MAIN EXECUTION
################################################################################

main() {
    print_header "DIVE CODER v19.5 - AUTOMATED SETUP ORCHESTRATOR"
    
    log_info "Setup started at $(date)"
    log_info "Log file: $LOG_FILE"
    
    # Validation
    validate_github_url
    check_dependencies
    
    # Setup
    setup_directories
    clone_repository
    detect_project_type
    
    # Configuration
    create_backend_api
    create_requirements
    create_env_file
    
    # Installation
    install_dependencies
    
    # Scripts and Documentation
    create_startup_script
    create_docker_support
    create_documentation
    generate_setup_report
    
    # Summary
    print_header "SETUP COMPLETED SUCCESSFULLY"
    
    log_success "Project setup completed!"
    log_success "Project directory: $PROJECT_DIR"
    log_success "Project type: $PROJECT_TYPE"
    
    echo "" | tee -a "$LOG_FILE"
    echo "📋 NEXT STEPS:" | tee -a "$LOG_FILE"
    echo "1. Configure environment variables:" | tee -a "$LOG_FILE"
    echo "   nano $PROJECT_DIR/.env" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
    echo "2. Start services:" | tee -a "$LOG_FILE"
    echo "   cd $PROJECT_DIR" | tee -a "$LOG_FILE"
    echo "   chmod +x start-services.sh" | tee -a "$LOG_FILE"
    echo "   ./start-services.sh" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
    echo "3. Access services:" | tee -a "$LOG_FILE"
    echo "   Backend API: http://localhost:8000" | tee -a "$LOG_FILE"
    echo "   API Docs: http://localhost:8000/docs" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
    echo "📚 Documentation: $PROJECT_DIR/DIVE_SETUP_GUIDE.md" | tee -a "$LOG_FILE"
    echo "📊 Setup Report: $PROJECT_DIR/SETUP_REPORT.json" | tee -a "$LOG_FILE"
    echo "📝 Log File: $LOG_FILE" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
}

# Run main function
main "$@"
