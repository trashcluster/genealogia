# GitHub Actions CI/CD Setup

## Overview

This project uses GitHub Actions to automatically build Docker images and push them to GitHub Container Registry (GHCR). The `docker-compose.yml` is configured to **pull pre-built images** rather than building them locally.

## Workflows

### 1. **docker-build.yml** - Build and Push Images

**Triggers:**
- Push to `main` or `develop` branches
- Push of any git tag (`v*`)
- Pull requests to `main` or `develop`

**Features:**
- Builds all 4 services in parallel (backend, ingestion-service, telegram-bot, frontend)
- Pushes to GitHub Container Registry (GHCR)
- Automatic image tagging based on git branch/tag
- Caches build layers for faster builds
- Only pushes on push events (not on PRs)

**Image Tags:**
- Branch: `ghcr.io/user/repo-service:branch-name`
- Tag: `ghcr.io/user/repo-service:v1.2.3`
- Commit SHA: `ghcr.io/user/repo-service:branch-abc123def`
- Latest: `ghcr.io/user/repo-service:latest` (on main/master branch)

**Example Images:**
```
ghcr.io/username/genealogia-backend:latest
ghcr.io/username/genealogia-ingestion-service:v1.0.0
ghcr.io/username/genealogia-telegram-bot:develop-abc123def
ghcr.io/username/genealogia-frontend:main
```

### 2. **security-scan.yml** - Vulnerability Scanning

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`
- Daily at 2 AM UTC

**Features:**
- Scans each Docker image with Trivy for vulnerabilities
- Uploads results to GitHub Security tab
- Failure does not block deployments (informational)

### 3. **docker-compose.prod.yml** - Production Compose File

Generated during release, containing image references pointing to GHCR instead of local builds.

## Setup Instructions

### Prerequisites

1. GitHub repository with Actions enabled (default)
2. Package write permissions in GitHub (automatic for your own repos)

### No Additional Setup Needed

The workflow uses `GITHUB_TOKEN` automatically provided by GitHub Actions. No additional secrets configuration required!

## Usage

### For Development

```bash
# Set your environment variables
cp .env.example .env

# Pull pre-built images from GHCR
docker-compose pull

# Start services
docker-compose up -d
```

### For Production (Using Pre-built Images)

```bash
# Set your environment variables
export REGISTRY=ghcr.io
export IMAGE_NAME=your-username/genealogia
export VERSION=v1.2.3

cp .env.example .env
docker-compose up -d
```

### Building Locally (Development Only)

```bash
# Use docker-compose with build context
docker-compose -f docker-compose.build.yml up
```

## Image Naming

The workflow creates images with this pattern:

```
REGISTRY / IMAGE_NAME - SERVICE : VERSION
     ↓          ↓          ↓         ↓
ghcr.io / username/genealogia-backend : v1.0.0
```

## Pushing a Release

1. Create a git tag:
```bash
git tag v1.0.0
git push origin v1.0.0
```

2. GitHub Actions will:
   - Build and push images with version tag
   - Generate `docker-compose.prod.yml`
   - Create a GitHub Release with the file

3. Download the release and use it:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Environment Variables

### Registry Configuration
```env
# Container registry settings
REGISTRY=ghcr.io                    # Container registry
IMAGE_NAME=username/genealogia      # Repository name
VERSION=v1.0.0                      # Image version/tag
```

### Service Configuration
```env
# Database
POSTGRES_PASSWORD=secure-password

# API Keys
SECRET_KEY=your-secret-jwt-key
BACKEND_API_KEY=sk_your-api-key
OPENAI_API_KEY=sk-...              # Required
OPENAI_MODEL=gpt-4

# Telegram (Optional)
TELEGRAM_BOT_TOKEN=your-token
TELEGRAM_WEBHOOK_URL=https://...

# Frontend
REACT_APP_API_URL=http://localhost:8000

# Debugging
DEBUG=False
```

## Docker Compose Files

### docker-compose.yml (Default)
- Uses image references from environment variables
- Supports pulling pre-built images
- No build context
- Perfect for production

### docker-compose.build.yml (Development, If Needed)
For local development with building:
```bash
docker-compose -f docker-compose.build.yml build
docker-compose -f docker-compose.build.yml up
```

## Troubleshooting

### Images Not Found

```bash
# Login to GHCR
docker login ghcr.io

# Pull images manually
docker pull ghcr.io/username/genealogia-backend:latest

# Verify images exist
docker images | grep genealogia
```

### Build Failures

Check GitHub Actions tab in your repository:
1. Go to **Actions** tab
2. Find the failing workflow run
3. Click to view detailed logs

### Authentication Issues

If you get permission denied:

```bash
# Create a Personal Access Token (PAT)
# 1. Go to GitHub Settings → Developer settings → Personal access tokens
# 2. Generate new token with 'write:packages' scope
# 3. Login with PAT:
docker login ghcr.io -u USERNAME -p YOUR_PAT
```

## Monitoring

### GitHub Actions Dashboard
- View all workflow runs: **Actions** tab
- Check for failures or performance issues

### Image Registry
- View pushed images: **Packages** section in profile
- Delete old images to save storage

## Best Practices

1. **Always use version tags in production**
   ```env
   VERSION=v1.2.3
   ```

2. **Use `latest` tag only for development**
   ```env
   VERSION=latest
   ```

3. **Keep secrets secure in `.env`**
   - Never commit `.env` file
   - Use `.env.local` for local overrides

4. **Regularly scan images**
   - Security scanning runs automatically
   - Review vulnerabilities in GitHub Security tab

5. **Tag releases**
   ```bash
   git tag -a v1.0.0 -m "Release version 1.0.0"
   git push origin --tags
   ```

## Performance Tips

- Images are cached on GitHub Actions runners
- Push to GHCR is typically <1 minute
- First pull might take longer; subsequent pulls use cached layers

## Cleanup

### Remove Old Images from GHCR

```bash
# List all versions
docker search ghcr.io/username/genealogia

# Delete via web UI:
# Packages → Select package → Delete version
```

### Stop Services

```bash
docker-compose down
```

### Clean Everything (Careful!)

```bash
docker-compose down -v  # Remove volumes too
```

## Next Steps

1. ✅ Configure `.env` with your API keys
2. ✅ Push to `main` branch (triggers build)
3. ✅ Watch GitHub Actions for build completion
4. ✅ Pull images: `docker-compose pull`
5. ✅ Start services: `docker-compose up -d`

## Support

For issues:
1. Check GitHub Actions logs
2. Verify `.env` configuration
3. Test image pulls manually: `docker pull ghcr.io/...`
4. Check GHCR package visibility (should be public or private with access)
