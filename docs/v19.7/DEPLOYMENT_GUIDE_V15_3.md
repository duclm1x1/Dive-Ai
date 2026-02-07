# Dive Coder V15.3 - Deployment Guide

## Overview

Dive Coder V15.3 can be deployed in multiple environments:
- **Local Development** - Single machine
- **Docker** - Containerized deployment
- **Kubernetes** - Cloud-native deployment
- **MCP Server** - Integration with Cursor IDE, Claude Desktop

---

## 1. Local Development

### Quick Start

```bash
# Install dependencies
pip install -r requirements-v15-3.txt

# Install Dive Context
cd dive-context && pnpm install && pnpm build && cd ..

# Start services
python divecoder_v15_3.py status
```

### Run Individual Services

```bash
# Terminal 1: Monitor Server
cd monitor_server
python -m uvicorn app.main:app --reload

# Terminal 2: Dive Context
cd dive-context
node dist/index-github.js

# Terminal 3: Dive Coder CLI
python divecoder_v15_3.py process --input "Your request"
```

---

## 2. Docker Deployment

### Build Docker Image

```bash
# Create Dockerfile
cat > Dockerfile << 'DOCKERFILE'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    graphviz \
    git \
    curl \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Install pnpm
RUN npm install -g pnpm

# Copy application
COPY . .

# Install Python dependencies
RUN pip install -r requirements-v15-3.txt

# Install Dive Context
RUN cd dive-context && pnpm install && pnpm build && cd ..

# Expose ports
EXPOSE 8787 3000 3001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python divecoder_v15_3.py status || exit 1

# Default command
CMD ["python", "divecoder_v15_3.py", "status"]
DOCKERFILE

# Build image
docker build -t dive-coder-v15-3:latest .
```

### Run Docker Container

```bash
# Run with port mapping
docker run -d \
  --name dive-coder-v15-3 \
  -p 8787:8787 \
  -p 3000:3000 \
  -p 3001:3001 \
  -e OPENAI_API_KEY="sk-..." \
  -e GITHUB_TOKEN="ghp_..." \
  dive-coder-v15-3:latest

# Check logs
docker logs dive-coder-v15-3

# Access services
# Monitor: http://localhost:8787
# Dive Context: http://localhost:3000
# Frontend: http://localhost:3001
```

### Docker Compose

```bash
# Create docker-compose.yml
cat > docker-compose.yml << 'COMPOSE'
version: '3.8'

services:
  dive-coder:
    build: .
    ports:
      - "8787:8787"
      - "3000:3000"
      - "3001:3001"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - GITHUB_TOKEN=${GITHUB_TOKEN}
      - MONITOR_URL=http://localhost:8787
    volumes:
      - ./.vibe:/app/.vibe
      - ./.agent:/app/.agent
    healthcheck:
      test: ["CMD", "python", "divecoder_v15_3.py", "status"]
      interval: 30s
      timeout: 10s
      retries: 3

  monitor-server:
    build:
      context: .
      dockerfile: monitor_server/Dockerfile
    ports:
      - "8787:8787"
    depends_on:
      - dive-coder

  dive-context:
    build:
      context: ./dive-context
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - GITHUB_TOKEN=${GITHUB_TOKEN}
COMPOSE

# Run
docker-compose up -d
```

---

## 3. Kubernetes Deployment

### Create Kubernetes Manifests

```bash
# Create k8s/deployment.yaml
cat > k8s/deployment.yaml << 'YAML'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: dive-coder-v15-3
  labels:
    app: dive-coder
    version: v15.3
spec:
  replicas: 2
  selector:
    matchLabels:
      app: dive-coder
  template:
    metadata:
      labels:
        app: dive-coder
        version: v15.3
    spec:
      containers:
      - name: dive-coder
        image: dive-coder-v15-3:latest
        ports:
        - containerPort: 8787
          name: monitor
        - containerPort: 3000
          name: context
        - containerPort: 3001
          name: frontend
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: dive-coder-secrets
              key: openai-api-key
        - name: GITHUB_TOKEN
          valueFrom:
            secretKeyRef:
              name: dive-coder-secrets
              key: github-token
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
        livenessProbe:
          exec:
            command:
            - python
            - divecoder_v15_3.py
            - status
          initialDelaySeconds: 10
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health
            port: 8787
          initialDelaySeconds: 5
          periodSeconds: 10
        volumeMounts:
        - name: vibe-data
          mountPath: /app/.vibe
        - name: skills
          mountPath: /app/.agent/skills
      volumes:
      - name: vibe-data
        persistentVolumeClaim:
          claimName: dive-coder-vibe-pvc
      - name: skills
        configMap:
          name: dive-coder-skills
---
apiVersion: v1
kind: Service
metadata:
  name: dive-coder-service
spec:
  selector:
    app: dive-coder
  ports:
  - name: monitor
    port: 8787
    targetPort: 8787
  - name: context
    port: 3000
    targetPort: 3000
  - name: frontend
    port: 3001
    targetPort: 3001
  type: LoadBalancer
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: dive-coder-vibe-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
YAML

# Deploy
kubectl apply -f k8s/deployment.yaml

# Check status
kubectl get pods
kubectl logs -f deployment/dive-coder-v15-3

# Access services
kubectl port-forward service/dive-coder-service 8787:8787
```

---

## 4. MCP Server Integration

### Cursor IDE

```json
{
  "mcpServers": {
    "dive-coder-v15-3": {
      "command": "python",
      "args": ["/path/to/dive-coder-v15-3/divecoder_v15_3.py"],
      "env": {
        "OPENAI_API_KEY": "sk-...",
        "GITHUB_TOKEN": "ghp_..."
      }
    }
  }
}
```

### Claude Desktop

```bash
# Add MCP server
claude mcp add dive-coder-v15-3 -- python /path/to/dive-coder-v15-3/divecoder_v15_3.py
```

---

## 5. Production Checklist

### Pre-Deployment

- [ ] All tests passing (`pytest`)
- [ ] Environment variables configured
- [ ] Secrets managed securely
- [ ] Database backups scheduled
- [ ] Monitoring configured
- [ ] Logging configured
- [ ] Rate limiting configured

### Deployment

- [ ] Health checks enabled
- [ ] Auto-scaling configured
- [ ] Load balancer configured
- [ ] SSL/TLS certificates installed
- [ ] Firewall rules configured
- [ ] Backup and restore tested

### Post-Deployment

- [ ] Monitor logs
- [ ] Check metrics
- [ ] Verify all endpoints
- [ ] Test failover
- [ ] Document deployment
- [ ] Create runbooks

---

## 6. Monitoring & Observability

### Prometheus Metrics

```python
from prometheus_client import Counter, Histogram

request_count = Counter('dive_coder_requests_total', 'Total requests')
request_duration = Histogram('dive_coder_request_duration_seconds', 'Request duration')
```

### Logging

```python
import structlog

logger = structlog.get_logger()

logger.info("event", component="dive_engine", status="started")
```

### Health Checks

```bash
# Check status
curl http://localhost:8787/health

# Check components
curl http://localhost:8787/components

# Check metrics
curl http://localhost:8787/metrics
```

---

## 7. Scaling

### Horizontal Scaling

```bash
# Kubernetes
kubectl scale deployment dive-coder-v15-3 --replicas=5

# Docker Compose
docker-compose up -d --scale dive-coder=5
```

### Vertical Scaling

Increase resource limits in deployment manifests.

---

## 8. Troubleshooting

### Service Won't Start

```bash
# Check logs
docker logs dive-coder-v15-3

# Check environment
python divecoder_v15_3.py status

# Verify dependencies
pip list | grep -E "fastapi|langchain|networkx"
```

### High Memory Usage

```bash
# Check memory
docker stats dive-coder-v15-3

# Reduce cache size
export CACHE_TTL=1800
```

### Slow Performance

```bash
# Check metrics
curl http://localhost:8787/metrics

# Enable profiling
export PROFILE=true
```

---

## 9. Backup & Recovery

### Backup

```bash
# Backup data
docker exec dive-coder-v15-3 tar -czf /app/backup.tar.gz .vibe .agent

# Copy to host
docker cp dive-coder-v15-3:/app/backup.tar.gz ./backup.tar.gz
```

### Recovery

```bash
# Restore data
docker cp ./backup.tar.gz dive-coder-v15-3:/app/
docker exec dive-coder-v15-3 tar -xzf /app/backup.tar.gz
```

---

**Dive Coder V15.3 - Ready for Production! 🚀**
