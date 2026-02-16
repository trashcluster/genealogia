# Genealogy App - AI-Powered Family Tree Management

A comprehensive genealogy data management system with AI-powered ingestion through multiple input methods.

## 🎯 Features

- **AI-Powered Data Extraction**: Use GPT-4 to understand and extract genealogical information from any text, voice, images, or PDFs
- **Multiple Input Methods**:
  - 💬 Text messages
  - 🎤 Voice messages (Telegram)
  - 📷 Images and PDFs (OCR)
  - 👥 vCard/CardDAV contacts
  - 🤖 Telegram bot integration
- **GEDCOM-Based Database**: Follows genealogical standards with proper schema for individuals, families, events, sources, and notes
- **API Key Authentication**: Secure API access for programmatic integration
- **Family Tree Visualization**: Browse and manage family relationships

## 🏗️ Architecture

```
genealogia/
├── packages/
│   ├── backend/              # FastAPI backend service
│   ├── ingestion-service/    # AI-powered data processing
│   ├── telegram-bot/         # Telegram bot interface
│   └── frontend/             # React web interface
├── database/                 # PostgreSQL schema
└── docker-compose.yml        # Container orchestration
```

### Services

1. **Backend (Port 8000)** - FastAPI REST API
   - User authentication (JWT + API keys)
   - CRUD operations for genealogical data
   - PostgreSQL database integration

2. **Ingestion Service (Port 8001)** - AI Processing
   - Text processing with GPT-4
   - Voice transcription (Whisper API)
   - OCR for images and PDFs
   - vCard/CardDAV parsing
   - Structured data extraction

3. **Telegram Bot (Port 8002)** - Chat Interface
   - Voice message processing
   - Image/PDF upload
   - Contact card sharing
   - Real-time feedback

4. **Frontend (Port 3000)** - React Dashboard
   - Family tree visualization
   - Data management interface
   - User authentication
   - Search and filtering

## 📋 Prerequisites

- Docker & Docker Compose
- OpenAI API key (for GPT-4)
- Telegram Bot token (optional, for Telegram integration)
- PostgreSQL (automatic via Docker)

## 🚀 Quick Start

### 1. Set up environment variables

```bash
cp .env.example .env
# Edit .env and add your API keys:
# - OPENAI_API_KEY
# - TELEGRAM_BOT_TOKEN (optional)
```

### 2. Start all services

```bash
docker-compose up -d
```

This starts:
- PostgreSQL (port 5432)
- Backend API (port 8000)
- Ingestion Service (port 8001)
- Telegram Bot (port 8002)
- Frontend (port 3000)

### 3. Access the application

- **Frontend**: http://localhost:3000
- **Backend API Docs**: http://localhost:8000/docs
- **Ingestion Service Docs**: http://localhost:8001/docs

## 📚 API Usage

### Register a new user

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john",
    "email": "john@example.com",
    "password": "secure_password"
  }'
```

Response includes `api_key` for future requests.

### Login

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john",
    "password": "secure_password"
  }'
```

### Create an individual

```bash
curl -X POST http://localhost:8000/api/individuals \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "gedcom_id": "I1",
    "given_names": "John",
    "surname": "Smith",
    "sex": "M",
    "birth_date": "1920-01-15",
    "birth_place": "London, England"
  }'
```

### Ingest text data

```bash
curl -X POST http://localhost:8001/api/ingest/text \
  -H "Content-Type: application/json" \
  -d '{
    "content": "My grandfather John Smith was born in 1920 in London. He married Mary Johnson in 1945.",
    "content_type": "text",
    "source_type": "telegram",
    "source_id": "telegram_123"
  }'
```

## 🤖 Using the Telegram Bot

1. Get your bot token from [@BotFather](https://t.me/BotFather)
2. Add `TELEGRAM_BOT_TOKEN` to `.env`
3. Configure webhook with your domain
4. Users can:
   - Send text descriptions of family members
   - Share voice recordings
   - Upload family documents/photos
   - Share contact cards

## 📊 Database Schema

The GEDCOM-based schema includes:

- **individuals** - Person records
- **family_groups** - Marriage/partnership records
- **children** - Parent-child relationships
- **events** - Births, deaths, marriages, etc.
- **sources** - Citation sources
- **media** - Family photos and documents
- **notes** - Genealogical notes

## 🔐 Authentication

Two authentication methods:

1. **API Key** (for service-to-service)
   - Generated automatically on registration
   - Pass as Bearer token: `Authorization: Bearer sk_...`

2. **JWT Token** (for UI)
   - Generated on login
   - 30-minute expiration (configurable)

## 🛠️ Development

### Backend

```bash
cd packages/backend
pip install -r requirements.txt
python -m uvicorn src.main:app --reload
```

### Ingestion Service

```bash
cd packages/ingestion-service
pip install -r requirements.txt
python -m uvicorn src.main:app --reload
```

### Telegram Bot

```bash
cd packages/telegram-bot
pip install -r requirements.txt
python -m uvicorn src.main:app --reload
```

### Frontend

```bash
cd packages/frontend
npm install
npm start
```

## 🔄 Ingestion Pipeline

```
User Input (Text/Voice/Image/PDF/vCard)
         ↓
   File Upload
         ↓
   Text Extraction (Transcription/OCR)
         ↓
   AI Processing (GPT-4)
         ↓
   Entity Extraction (INDIVIDUAL/FAMILY/EVENT)
         ↓
   Data Validation
         ↓
   Database Storage
```

## 📝 GEDCOM Data Structure

```
Individual
├── Personal Info (name, sex, dates, places)
├── Events (birth, death, marriage, etc.)
├── Family Relationships
├── Media (photos, documents)
├── Sources (citations)
└── Notes
```

## 🗄️ Database Queries

Example: Find all individuals with surname "Smith"

```sql
SELECT * FROM individuals 
WHERE user_id = '{user_id}' 
AND surname ILIKE '%Smith%';
```

## 🚨 Troubleshooting

### Service won't start
- Check `.env` file has all required keys
- Verify port availability (8000, 8001, 8002, 3000, 5432)
- View logs: `docker-compose logs service_name`

### Database connection error
- Ensure PostgreSQL is healthy: `docker-compose ps`
- Reset database: `docker-compose down -v` then `docker-compose up`

### API returns 401 Unauthorized
- Check your API key is correct
- Ensure Bearer token format: `Authorization: Bearer sk_...`

## 📖 Documentation

- [FastAPI Docs](http://localhost:8000/docs)
- [GEDCOM Standard](https://en.wikipedia.org/wiki/GEDCOM)
- [OpenAI API](https://platform.openai.com/docs)
- [Telegram Bot API](https://core.telegram.org/bots/api)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Push to the branch
5. Open a pull request

## 📄 License

MIT License

## 🎓 Next Steps

- [ ] Add family tree visualization
- [ ] Implement GEDCOM file import/export
- [ ] Add photo gallery with OCR
- [ ] Create timeline view
- [ ] Add relationship suggestions
- [ ] Implement data privacy controls
- [ ] Add multi-language support
- [ ] Create mobile app

## 📧 Support

For issues and questions, please create an issue on the repository.
