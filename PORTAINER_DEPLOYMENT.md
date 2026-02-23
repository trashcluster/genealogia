# 🐳 Portainer Deployment Guide

This guide provides step-by-step instructions for deploying Genealogia using Portainer.

## 📋 Prerequisites

- Portainer instance (Community or Business Edition)
- Docker environment
- At least one AI provider API key (OpenAI, Claude, or Ollama)

## 🚀 Quick Deployment

### Step 1: Prepare Environment Variables

1. Copy the Portainer environment template:
   ```bash
   cp .env.portainer .env.portainer.custom
   ```

2. Edit the file and update all **REQUIRED** variables:
   - `POSTGRES_PASSWORD`: Set a secure database password
   - `SECRET_KEY`: Generate a random JWT signing key
   - `BACKEND_API_KEY`: Set a secure backend API key
   - At least one AI provider API key (OpenAI, Claude, or Ollama)
   - `TELEGRAM_BOT_TOKEN` (if using Telegram integration)

### Step 2: Deploy in Portainer

1. **Login to Portainer**
2. **Navigate to Stacks** → **Add Stack**
3. **Stack Configuration**:
   - **Name**: `genealogia`
   - **Build method**: Web editor
4. **Paste the Docker Compose content**:
   - Copy the entire contents of `docker-compose.portainer.new.yml`
   - Paste into the web editor
5. **Configure Environment Variables**:
   - Click on the "Environment variables" tab
   - Copy all variables from your `.env.portainer.custom` file
   - Remove all comments (# lines)
   - Ensure each variable is on a separate line
6. **Deploy**:
   - Click "Deploy the stack"
   - Wait for all services to start (2-3 minutes)

### Step 3: Verify Deployment

1. **Check Stack Status**:
   - Go to Stacks → genealogia
   - Verify all containers are running (green status)
2. **Access Services**:
   - Frontend: http://your-server:8090
   - Backend API: http://your-server:8091
   - API Docs: http://your-server:8091/docs

## 🔧 Advanced Configuration

### Enable Optional Services

To enable optional services, add profiles to your deployment:

1. **In Portainer Stack Editor**:
   - Add to the bottom of the compose file:
   ```yaml
   profiles:
     - with-nginx
     - with-ollama
   ```

2. **Or use Portainer Profiles Field**:
   - In the stack configuration, add: `with-nginx,with-ollama`

**Available Profiles**:
- `with-nginx`: Enables Nginx reverse proxy (ports 80, 443)
- `with-ollama`: Enables local Ollama service (port 11434)

### Custom Ports

To change default ports, modify the port mappings in the compose file:

```yaml
# Example: Change frontend port to 3000
frontend:
  ports:
    - "3000:3000"  # Changed from "8090:3000"
```

### Persistent Storage

All data is persisted in Docker volumes:
- `postgres_data`: Database data
- `redis_data`: Cache data
- `uploads_data`: User uploads
- `documents_data`: Knowledge base documents
- `faces_data`: Face recognition data
- `telegram_data`: Bot session data

## 🔒 Security Configuration

### Production Security Checklist

- [ ] Change `POSTGRES_PASSWORD` from default
- [ ] Change `SECRET_KEY` to a random string
- [ ] Change `BACKEND_API_KEY` to a secure key
- [ ] Set up SSL certificates (if using Nginx)
- [ ] Configure firewall rules
- [ ] Enable backup for database volume
- [ ] Monitor container logs

### SSL Configuration (with Nginx)

1. **Create SSL directory**:
   ```bash
   mkdir -p nginx/ssl
   ```

2. **Add certificates**:
   - Place `cert.pem` and `key.pem` in `nginx/ssl/`
   - Or use Let's Encrypt certificates

3. **Configure Nginx** (optional):
   - Create `nginx/nginx.conf` with your SSL configuration

## 📊 Monitoring and Maintenance

### Health Checks

All services include health checks. Monitor them in Portainer:
- Go to Containers → Select container → Health tab

### Logs

View logs in Portainer:
- Go to Containers → Select container → Logs tab
- Or use stack logs: Stacks → genealogia → Logs

### Updates

To update the application:
1. **Pull new images** in Portainer
2. **Redeploy the stack**
3. **Or update image tags** in the compose file

## 🐛 Troubleshooting

### Common Issues

**1. Containers won't start**
- Check environment variables are properly set
- Verify API keys are valid
- Check port conflicts

**2. Database connection failed**
- Verify PostgreSQL container is healthy
- Check database credentials in environment variables
- Ensure database schema was applied

**3. AI services not working**
- Verify API keys are valid and active
- Check network connectivity to AI providers
- Review service logs for error messages

**4. Frontend not loading**
- Check backend service is running
- Verify API URL configuration
- Check browser console for errors

### Resetting the Stack

To completely reset:
1. **Stop the stack** in Portainer
2. **Remove volumes** (careful - this deletes data)
3. **Redeploy** with fresh configuration

### Backup and Restore

**Backup volumes**:
```bash
# Example backup commands
docker run --rm -v genealogia_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz -C /data .
```

**Restore volumes**:
```bash
docker run --rm -v genealogia_postgres_data:/data -v $(pwd):/backup alpine tar xzf /backup/postgres_backup.tar.gz -C /data
```

## 📞 Support

For deployment issues:
1. Check Portainer logs
2. Review this troubleshooting section
3. Create an issue on GitHub
4. Include stack configuration and logs

---

**Note**: This deployment configuration is optimized for production use with proper security defaults and monitoring capabilities.
