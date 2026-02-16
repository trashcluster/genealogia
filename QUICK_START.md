# Quick Start Guide - Portainer

Get the Genealogy App running in Portainer with zero configuration!

## 🚀 Single Command (Copy & Paste)

### Option 1: Via Portainer UI (Easiest)

1. Open your Portainer web interface
2. Navigate to **Stacks** → **Add Stack**
3. Click **Upload**
4. Select `docker-compose.portainer.yml` from this repo
5. Click **Deploy the stack**

Done! App will be running in ~2 minutes.

### Option 2: Via Docker CLI

```bash
git clone https://github.com/trashcluster/genealogia.git
cd genealogia
docker-compose -f docker-compose.portainer.yml up -d
```

## 📍 Access the App

Once deployed:

- **Frontend**: http://localhost:8090
- **Backend API**: http://localhost:8091
- **API Documentation**: http://localhost:8091/docs

## ⚙️ Configure Credentials (Important!)

The default credentials are placeholders. Update them in Portainer:

1. Go to **Stacks** → Select your stack
2. Click **Editor**
3. Update these environment variables:

```yaml
OPENAI_API_KEY: sk-your-actual-openai-key     # Required for AI
TELEGRAM_BOT_TOKEN: your-actual-telegram-token # Optional
SECRET_KEY: generate-new-secure-key-here       # Generate: openssl rand -hex 32
```

4. Click **Update the stack**

## 🔐 First Login

1. Open http://localhost:8090
2. Click "Register" to create an account
3. You'll receive an API key for programmatic access

## 📦 What's Included?

- ✅ PostgreSQL (database)
- ✅ Backend API (FastAPI)
- ✅ Ingestion Service (AI processing)
- ✅ Telegram Bot (optional)
- ✅ Frontend (React)
- ✅ All dependencies pre-installed
- ✅ Database schema pre-configured

## 🎯 Exposed Ports

By design, only:
- **8090** - Frontend (user interface)
- **8091** - Backend API (REST endpoints)

Internal services (PostgreSQL, Ingestion, Telegram) are not exposed to prevent unauthorized access.

## 🔧 Troubleshooting

**Can't access the app?**
```bash
# Check if containers are running
docker ps | grep genealogy

# Check logs
docker logs genealogy-frontend
docker logs genealogy-backend
```

**Database errors?**
```bash
# Verify database is healthy
docker logs genealogy-postgres

# Check data exists
docker exec genealogy-postgres psql -U genealogy -d genealogy_db -c "\dt"
```

## 📚 Full Documentation

See [PORTAINER.md](PORTAINER.md) for:
- Detailed deployment guide
- Network architecture
- Backup & restore procedures
- Production checklist
- Complete environment reference

## ❓ Need Help?

1. Check [PORTAINER.md](PORTAINER.md) troubleshooting section
2. Review [README.md](README.md) for general info
3. Check container logs in Portainer
4. Verify network connectivity

## 🎓 Next Steps

1. ✅ Deploy the stack
2. ✅ Update OpenAI API key
3. ✅ Create first user account
4. ✅ Start importing family data!
5. ✅ (Optional) Configure Telegram bot

Enjoy! 🎉
