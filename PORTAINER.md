# Portainer Deployment Guide

This guide explains how to deploy the Genealogy App using Portainer.

## Prerequisites

- Portainer installed and running
- Access to Portainer web console
- Docker installed on the target host

## Quick Start with Portainer

### 1. Copy the Docker Compose File

Use `docker-compose.portainer.yml` - it has:
- ✅ Hardcoded placeholder credentials (easy to edit)
- ✅ Only frontend (8090) and backend (8091) exposed to host
- ✅ Internal services (postgres, ingestion, telegram) not exposed
- ✅ Database schema pre-integrated (no mounting needed)
- ✅ Private network for inter-service communication

### 2. Import into Portainer

1. Open Portainer web UI
2. Go to **Stacks** → **Add Stack**
3. Choose **Upload** 
4. Select `docker-compose.portainer.yml`
5. Click **Deploy the stack**

Or paste the contents directly in the editor.

### 3. Configure Credentials

After deployment, update these placeholder values:

**In Stack Environment:**

| Variable | Current Value | What to Set |
|----------|---------------|-------------|
| OPENAI_API_KEY | `sk-your-openai-key-here` | Your OpenAI API key |
| TELEGRAM_BOT_TOKEN | `123456:ABC-DEF...` | Your Telegram Bot token |
| TELEGRAM_WEBHOOK_URL | `https://your-domain.com/...` | Your webhook URL |
| SECRET_KEY | `genealogy-secret-key-...` | Generate secure key: `openssl rand -hex 32` |

**To Update:**
1. Go to **Stacks** → Select your stack
2. Click **Editor** on the right
3. Edit the environment variables
4. Click **Update the stack**
5. Services will redeploy with new values

### 4. Access the Application

- **Frontend**: http://your-host:8090
- **Backend API**: http://your-host:8091
- **API Docs**: http://your-host:8091/docs

### 5. First Login

1. Register a new user at the frontend
2. Use the provided API key for programmatic access
3. Or login with credentials via web interface

## Network Architecture

```
┌─────────────────────────────────────────────────┐
│                   Host Network                  │
│  ┌─────────────────────────────────────────┐   │
│  │ External Access                         │   │
│  │ Port 8090 → Frontend                    │   │
│  │ Port 8091 → Backend API                 │   │
│  └─────────────────────────────────────────┘   │
└────────────┬──────────────────────────┬──────────┘
             │                          │
    ┌────────▼──┐              ┌───────▼────┐
    │ Frontend  │              │  Backend   │
    │  :3000    │              │   :8000    │
    └───────────┘              └──────┬─────┘
                                      │
                    ┌─────────────────┼─────────────┐
                    │                 │             │
              ┌─────▼─────┐    ┌─────▼──────┐  ┌──▼──────┐
              │ PostgreSQL │    │ Ingestion  │  │ Telegram│
              │   :5432    │    │   :8001    │  │ Bot     │
              └────────────┘    └────────────┘  └─────────┘
              
              (All services in private genealogy-net)
```

## Troubleshooting

### Cannot Access Frontend

```bash
# Check if stack is running
docker ps | grep genealogy

# Check logs
docker logs genealogy-frontend

# Verify network
docker network ls | grep genealogy
```

### Database Connection Error

```bash
# Check postgres health
docker exec genealogy-postgres pg_isready -U genealogy

# Check database exists
docker exec genealogy-postgres psql -U genealogy -d genealogy_db -c "\dt"
```

### API Key Issues

Make sure `BACKEND_API_KEY` in ingestion and telegram services matches:
```yaml
BACKEND_API_KEY: sk_genealogy_backend_key_placeholder  # Keep consistent
```

### Missing Files

All files are included in the pre-built Docker images:
- Database schema is in the postgres image
- Source code is in the backend/ingestion/telegram images
- Frontend is compiled and served via nginx

No file mounting needed!

## Backup & Restore

### Backup Database

```bash
docker exec genealogy-postgres pg_dump -U genealogy genealogy_db > backup.sql
```

### Restore Database

```bash
docker exec -i genealogy-postgres psql -U genealogy genealogy_db < backup.sql
```

## Production Checklist

- [ ] Change all placeholder credentials
- [ ] Set `DEBUG: "False"` for all services
- [ ] Configure `TELEGRAM_BOT_TOKEN` and webhook
- [ ] Set `OPENAI_API_KEY` for ingestion
- [ ] Generate strong `SECRET_KEY` (use: `openssl rand -hex 32`)
- [ ] Set up SSL/HTTPS reverse proxy
- [ ] Configure backup strategy for postgres volume
- [ ] Monitor logs regularly

## Environment Variables Reference

### Backend
- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - JWT signing key (must be secure!)
- `ALGORITHM` - JWT algorithm (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Token expiration
- `INGESTION_SERVICE_URL` - URL to ingestion service
- `DEBUG` - Enable debug mode (False for production)

### Ingestion
- `OPENAI_API_KEY` - OpenAI API key (required)
- `OPENAI_MODEL` - Model to use (default: gpt-4)
- `BACKEND_SERVICE_URL` - URL to backend service
- `BACKEND_API_KEY` - API key for backend authentication
- `DEBUG` - Enable debug mode

### Telegram Bot
- `TELEGRAM_BOT_TOKEN` - Bot token from @BotFather
- `TELEGRAM_WEBHOOK_URL` - Webhook URL for updates
- `BACKEND_SERVICE_URL` - URL to backend service
- `BACKEND_API_KEY` - API key for backend
- `INGESTION_SERVICE_URL` - URL to ingestion service
- `DEBUG` - Enable debug mode

## Support

For issues:
1. Check Portainer **Stacks** → **Logs** for error messages
2. Review **Containers** tab for service health
3. Check **Networks** to verify inter-service connectivity
4. Consult main [README.md](README.md) for general info

## Next Steps

1. ✅ Deploy the stack
2. ✅ Update placeholder credentials
3. ✅ Configure Telegram bot (optional)
4. ✅ Access frontend at http://localhost:8090
5. ✅ Register first user account
6. ✅ Start importing family data!
