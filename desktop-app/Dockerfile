# Dive AI V29.4 Desktop App
# Multi-stage Docker build

FROM python:3.11-slim AS backend

WORKDIR /app/backend

# Install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ .

# Expose port
EXPOSE 1879

# Run backend
CMD ["python", "gateway_server.py"]


# Frontend build stage
FROM node:20-alpine AS frontend-build

WORKDIR /app

# Install dependencies
COPY package.json package-lock.json* ./
RUN npm ci

# Copy source
COPY . .

# Build
RUN npm run build


# Production stage
FROM nginx:alpine AS production

# Copy built frontend
COPY --from=frontend-build /app/dist/renderer /usr/share/nginx/html

# Copy nginx config
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
