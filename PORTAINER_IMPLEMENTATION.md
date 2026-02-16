# Portainer Deployment - Implementation Summary

This document summarizes the changes made to support easy Portainer deployment.

## What Changed

### 1. **New Files Created**

```
docker-compose.portainer.yml        # Main deployment file for Portainer
docker/postgres/Dockerfile          # Custom PostgreSQL with schema integrated
PORTAINER.md                        # Detailed Portainer guide
QUICK_START.md                      # Quick start for Portainer users
```

### 2. **docker-compose.portainer.yml Features**

✅ **No Environment Variable Templating**
  - All values are hardcoded placeholders
  - Users edit directly in Portainer UI

✅ **Minimal Port Exposure**
```
Port 8090 → Frontend      (exposed to host)
Port 8091 → Backend API   (exposed to host)
```
Internal services (postgres, ingestion, telegram) are NOT exposed.

✅ **Pre-integrated Database Schema**
  - Custom PostgreSQL image includes schema
  - No mounting required
  - No file dependencies

✅ **Private Docker Network**
  - All services on `genealogy-net` bridge network
  - Services communicate internally only
  - Secure by default

✅ **Hardcoded Placeholder Credentials**
```yaml
POSTGRES_PASSWORD: genealogy123!
SECRET_KEY: genealogy-secret-key-change-this-in-production
OPENAI_API_KEY: sk-your-openai-key-here
TELEGRAM_BOT_TOKEN: 123456:ABC-DEF...
```

### 3. **Custom PostgreSQL Docker Image**

**File**: `docker/postgres/Dockerfile`

```dockerfile
FROM postgres:15-alpine
COPY database/schema.sql /docker-entrypoint-initdb.d/01-schema.sql
```

- Schema is integrated into the image
- No volume mounting needed
- Pre-built and pushed to GHCR
- Image: `ghcr.io/trashcluster/genealogia-postgres:latest`

### 4. **GitHub Actions Updates**

The docker-build workflow now builds 5 services:
1. ✅ backend
2. ✅ ingestion-service
3. ✅ telegram-bot
4. ✅ frontend
5. ✅ postgres (new!)

**Configuration**:
- Postgres uses root context (`.`) with custom Dockerfile path
- Others use packages directory context
- All pushed to GHCR for pull-only deployment

## Deployment Flow

### Developer/Admin
```
1. Push code to GitHub
2. GitHub Actions builds all 5 images
3. Images pushed to GHCR
4. Tags: latest, branch name, version, commit SHA
```

### Portainer User
```
1. Open Portainer → Stacks → Add Stack
2. Upload docker-compose.portainer.yml
3. Click Deploy
4. Update placeholder credentials
5. Access at http://localhost:8090
6. Done!
```

## Security Notes

### Default (Safe)
- Only frontend and backend exposed
- PostgreSQL locked to internal network
- Telegram bot not exposed
- Ingestion service not exposed

### Placeholder Credentials
Users MUST update before production:

| Credential | Default | Action |
|-----------|---------|--------|
| POSTGRES_PASSWORD | genealogy123! | Change in compose file |
| SECRET_KEY | genealogy-secret-key... | Generate: `openssl rand -hex 32` |
| OPENAI_API_KEY | sk-your-openai-key-here | Add real key |
| TELEGRAM_BOT_TOKEN | 123456:ABC-DEF... | Add real token (optional) |

## Port Mapping Reference

```
Container → Host

Frontend (3000) → 8090
Backend (8000) → 8091
PostgreSQL (5432) → NOT EXPOSED
Ingestion (8001) → NOT EXPOSED
Telegram (8002) → NOT EXPOSED
```

## Network Architecture

```
┌──────────────────────────────────────────┐
│             Host Network                 │
│  Port 8090 (Frontend)  │  Port 8091 (API)
│  ─────────────────────────────────────   │
└────────────┬──────────────────────┬──────┘
             │                      │
    ┌────────▼──────┐      ┌───────▼────┐
    │   Frontend    │      │   Backend  │
    │   Container   │      │ Container  │
    └───────────────┘      └──────┬─────┘
             │                    │
             └────────┬───────────┘
                      │
            ┌─────────▼──────────┐
            │ genealogy-net      │
            │ (Private Network)  │
            └────────┬───────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
    ┌───▼──┐ ┌──────▼───┐ ┌──────▼──┐
    │ DB   │ │ Ingestion│ │ Telegram│
    │ :5432│ │  :8001   │ │  :8002  │
    └──────┘ └──────────┘ └─────────┘
   (NOT EXPOSED)
```

## Updating Credentials in Portainer

### Step 1: Access Stack Editor
```
Stacks → genealogy → Editor (tab on right)
```

### Step 2: Find and Update
```yaml
# Change:
OPENAI_API_KEY: sk-your-openai-key-here

# To:
OPENAI_API_KEY: sk-proj-real-api-key-here...
```

### Step 3: Deploy
```
Click "Update the stack"
→ Services redeploy with new values
```

## Pre-built Images

All images are available on GHCR:

```
ghcr.io/trashcluster/genealogia-backend:latest
ghcr.io/trashcluster/genealogia-ingestion-service:latest
ghcr.io/trashcluster/genealogia-telegram-bot:latest
ghcr.io/trashcluster/genealogia-frontend:latest
ghcr.io/trashcluster/genealogia-postgres:latest
```

**Note**: Postgres image is custom-built, not official postgres image.

## File Dependencies Eliminated

❌ BEFORE (Portainer-unfriendly)
```
- Needs database/schema.sql on host
- Needs packages/*/src files on host
- Needs environment .env file
- Complex mounting
```

✅ AFTER (Portainer-native)
```
- Everything in pre-built images
- Just the docker-compose file needed
- Pure pull deployment
- No local files needed
```

## Troubleshooting Commands

```bash
# View running containers
docker ps | grep genealogy

# Check logs
docker logs genealogy-frontend
docker logs genealogy-backend
docker logs genealogy-postgres

# Test database
docker exec genealogy-postgres psql -U genealogy -c "\dt"

# Check network
docker network inspect genealogy_genealogy-net

# Check resource usage
docker stats genealogy-*
```

## Production Deployment

For production, add to the compose file:

```yaml
# Add restart policy
restart_policy:
  condition: on-failure
  delay: 5s
  max_attempts: 3

# Add resource limits
deploy:
  resources:
    limits:
      cpus: '1'
      memory: 1G
    reservations:
      cpus: '0.5'
      memory: 512M

# Add logging
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

## Next Steps

1. ✅ Users obtain `docker-compose.portainer.yml`
2. ✅ Upload to Portainer
3. ✅ Customize credentials
4. ✅ Deploy with one click
5. ✅ Access at configured ports

## References

- [QUICK_START.md](QUICK_START.md) - Fast setup guide
- [PORTAINER.md](PORTAINER.md) - Comprehensive Portainer guide
- [README.md](README.md) - General project info
- [DEPLOYMENT.md](DEPLOYMENT.md) - GitHub Actions deployment
