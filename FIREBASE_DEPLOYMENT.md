# 🔥 Firebase Deployment Guide

This guide provides step-by-step instructions for deploying Genealogia on Firebase's serverless platform.

## 🏗️ Firebase Architecture Overview

Genealogia has been completely restructured for Firebase's serverless architecture:

### **Core Firebase Services Used**
- **Firebase Authentication**: User management and authentication
- **Cloud Firestore**: NoSQL database for genealogical data
- **Firebase Storage**: File storage for documents, photos, and media
- **Cloud Functions**: Serverless backend for AI processing and API endpoints
- **Firebase Hosting**: Static web hosting for the React frontend

### **Key Changes from Docker Version**
- ❌ **Removed**: PostgreSQL, Redis, Docker containers
- ✅ **Added**: Firestore collections, Firebase Auth, Cloud Functions
- 🔄 **Migrated**: All backend logic to serverless functions
- 🔄 **Migrated**: File storage to Firebase Storage
- 🔄 **Migrated**: Database schema to Firestore collections

## 📋 Prerequisites

1. **Firebase Account**: Create account at https://firebase.google.com
2. **Node.js 18+**: For local development
3. **Firebase CLI**: Install with `npm install -g firebase-tools`
4. **AI Provider API Keys**: At least one of OpenAI, Claude, or Ollama

## 🚀 Quick Deployment

### Step 1: Initialize Firebase Project

```bash
# Install Firebase CLI
npm install -g firebase-tools

# Login to Firebase
firebase login

# Initialize project in genealogia directory
cd genealogia
firebase init

# Choose:
# - Hosting: Configure and deploy Firebase Hosting sites
# - Functions: Configure and deploy Cloud Functions
# - Firestore: Deploy rules and indexes
# - Storage: Deploy security rules
```

### Step 2: Configure Environment Variables

Create `.env.local` in the frontend directory:

```bash
# Firebase Configuration (get from Firebase Console)
REACT_APP_FIREBASE_API_KEY=your-api-key
REACT_APP_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
REACT_APP_FIREBASE_PROJECT_ID=your-project-id
REACT_APP_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
REACT_APP_FIREBASE_MESSAGING_SENDER_ID=123456789
REACT_APP_FIREBASE_APP_ID=1:123456789:web:abcdef

# AI Provider Keys (at least one required)
REACT_APP_OPENAI_API_KEY=sk-your-openai-key
REACT_APP_CLAUDE_API_KEY=sk-ant-your-claude-key
REACT_APP_OLLAMA_URL=https://your-ollama-instance.com
```

Configure Cloud Functions environment variables:

```bash
# Set in Firebase Console → Functions → Configuration
OPENAI_API_KEY=sk-your-openai-key
CLAUDE_API_KEY=sk-ant-your-claude-key
OLLAMA_URL=https://your-ollama-instance.com
```

### Step 3: Deploy Functions

```bash
# Navigate to functions directory
cd functions

# Install dependencies
npm install

# Deploy functions
firebase deploy --only functions
```

### Step 4: Deploy Frontend

```bash
# Navigate to frontend directory
cd frontend-firebase

# Install dependencies
npm install

# Build and deploy
npm run deploy
```

### Step 5: Configure Firestore Rules and Indexes

```bash
# Deploy Firestore rules and indexes
firebase deploy --only firestore
```

## 📁 Project Structure

```
genealogia/
├── firebase.json                 # Firebase configuration
├── firestore.rules              # Firestore security rules
├── firestore.indexes.json       # Firestore indexes
├── storage.rules                # Firebase Storage rules
├── functions/                   # Cloud Functions
│   ├── package.json
│   ├── tsconfig.json
│   └── src/
│       ├── index.ts             # Main functions file
│       ├── auth.ts              # Authentication functions
│       ├── individuals.ts       # Individual management
│       ├── ingestion.ts         # AI data processing
│       └── ...                  # Other function modules
└── frontend-firebase/           # React frontend
    ├── package.json
    ├── public/
    └── src/
        ├── firebase.ts          # Firebase configuration
        └── ...                  # React components
```

## 🔧 Configuration Details

### Firestore Collections Structure

```
users/{userId}
├── individuals/{individualId}
├── families/{familyId}
├── events/{eventId}
├── media/{mediaId}
├── knowledge/{documentId}
├── faces/{faceId}
├── ingestion/{logId}
└── conversations/{conversationId}
```

### Cloud Functions

| Function | Purpose | Trigger |
|----------|---------|---------|
| `register` | User registration | Callable |
| `createIndividual` | Create person record | Callable |
| `processTextIngestion` | AI text processing | Callable |
| `processVoiceIngestion` | AI voice processing | Callable |
| `processDocumentIngestion` | AI document processing | Callable |
| `healthCheck` | Service health check | HTTP |
| `scheduledMaintenance` | Daily cleanup | Pub/Sub |

### Firebase Storage Structure

```
gs://your-project.appspot.com/
├── users/{userId}/
│   ├── profiles/
│   ├── documents/
│   ├── faces/
│   ├── media/
│   └── temp/
```

## 🔒 Security Configuration

### Authentication
- Firebase Auth with email/password
- Custom claims for role-based access
- JWT tokens for API access

### Firestore Rules
- User-based data isolation
- Read/write permissions per user
- Collection-level security

### Storage Rules
- User-specific file access
- File type restrictions
- Size limits

## 📊 Monitoring and Logging

### Firebase Console
- **Functions**: Monitor execution, errors, and performance
- **Firestore**: Database usage and performance
- **Storage**: File storage usage
- **Authentication**: User activity

### Local Development
```bash
# Start Firebase emulators
firebase emulators:start

# Run tests with emulators
npm test -- --watchAll=false
```

## 🚨 Limitations and Considerations

### Firebase Limitations
- **Functions**: 9-minute execution timeout
- **Firestore**: 1MB document size limit
- **Storage**: 5GB free tier, then $0.026/GB
- **Pricing**: Pay-as-you-go model

### AI Processing Limitations
- **OpenAI**: Rate limits and token costs
- **Claude**: Rate limits and token costs
- **Voice Processing**: Large files may timeout
- **Face Recognition**: Memory-intensive for large images

### Performance Considerations
- **Cold Starts**: Functions may have initial latency
- **Database Queries**: Optimize with proper indexes
- **File Uploads**: Use resumable uploads for large files

## 🔄 Migration from Docker Version

### Data Migration
1. **Export PostgreSQL data** to JSON format
2. **Transform data structure** to match Firestore schema
3. **Import to Firestore** using Firebase SDK
4. **Migrate files** from Docker volumes to Firebase Storage

### Feature Differences
| Feature | Docker Version | Firebase Version |
|---------|---------------|------------------|
| Database | PostgreSQL | Firestore |
| File Storage | Local volumes | Firebase Storage |
| AI Processing | Separate services | Cloud Functions |
| Authentication | JWT + API keys | Firebase Auth |
| Deployment | Docker Compose | Firebase CLI |
| Scaling | Manual scaling | Auto-scaling |

## 💰 Cost Estimation

### Firebase Pricing (Free Tier)
- **Firestore**: 1GB storage, 50k reads/day, 20k writes/day
- **Functions**: 125k invocations/month, 40k GB-seconds/month
- **Storage**: 5GB storage, 1GB/day download
- **Authentication**: 10k monthly active users

### Estimated Monthly Costs (Medium Usage)
- **Firestore**: $0.18 (10GB storage, 100k reads, 50k writes)
- **Functions**: $25 (500k invocations, 200k GB-seconds)
- **Storage**: $0.50 (20GB storage, 10GB download)
- **AI APIs**: $50-200 (depending on usage)
- **Total**: ~$75-275/month

## 🛠️ Development Workflow

### Local Development
```bash
# Start emulators
firebase emulators:start

# Run frontend locally
cd frontend-firebase
npm start

# Test functions locally
cd functions
npm run shell
```

### Deployment Pipeline
```bash
# Deploy everything
firebase deploy

# Deploy specific services
firebase deploy --only functions
firebase deploy --only hosting
firebase deploy --only firestore:rules
```

### Testing
```bash
# Run tests
npm test

# Run integration tests with emulators
firebase emulators:exec "npm test"
```

## 🆘 Troubleshooting

### Common Issues

**1. Functions Timeout**
- Increase timeout in firebase.json
- Optimize function code
- Use background functions for long tasks

**2. Firestore Permission Denied**
- Check Firestore rules
- Verify user authentication
- Check collection paths

**3. Storage Upload Failed**
- Check Storage rules
- Verify file size limits
- Check network connectivity

**4. High Costs**
- Monitor usage in Firebase Console
- Optimize database queries
- Implement caching strategies

### Debugging
```bash
# View function logs
firebase functions:log

# View emulator logs
firebase emulators:start --debug
```

## 📚 Additional Resources

- [Firebase Documentation](https://firebase.google.com/docs)
- [Cloud Functions Documentation](https://firebase.google.com/docs/functions)
- [Firestore Documentation](https://firebase.google.com/docs/firestore)
- [Firebase Pricing](https://firebase.google.com/pricing)

---

**Note**: This Firebase version provides better scalability, automatic updates, and reduced infrastructure management compared to the Docker version.
