# Genealogia - Enhanced Genealogy Web Application

A comprehensive family tree web application with AI-powered data ingestion, face recognition, and knowledge base capabilities.

## 🚀 Features

### Core Functionality
- **Multi-AI Backend Support**: OpenAI GPT-4, Anthropic Claude, and local Ollama models
- **Interactive Telegram Bot**: Voice, text, document, and photo ingestion with conversational AI
- **Face Recognition**: Automatic face detection, clustering, and person identification
- **Knowledge Base**: Document storage with semantic search and event extraction
- **Family Tree Visualization**: Interactive genealogical relationships and timeline views
- **Modern UI**: Responsive React frontend with Tailwind CSS and Heroicons

### Data Ingestion Methods
- **Text Input**: Direct text entry with AI processing
- **Voice Messages**: Audio-to-text conversion and analysis
- **Document Upload**: PDF, images, text files with OCR and content extraction
- **Photo Analysis**: Face detection and person identification
- **Telegram Integration**: Complete bot interface for mobile data entry

### AI-Powered Features
- **Smart Data Extraction**: Automatic person, relationship, and event identification
- **Interactive Questioning**: AI asks clarifying questions to improve data quality
- **Multi-Provider Support**: Fallback between AI providers for reliability
- **Event Correlation**: Cross-reference events across documents and media

## 🏗️ Architecture

### Microservices Design
- **Backend API** (Port 8000): Core genealogical data management
- **Ingestion Service** (Port 8001): AI-powered data processing
- **Telegram Bot** (Port 8002): Interactive chat interface
- **Knowledge Base** (Port 8003): Document storage and search
- **Face Recognition** (Port 8004): Image analysis and clustering
- **Frontend** (Port 3000): React web application

### Database
- **PostgreSQL** with pgvector extension for vector similarity
- **GEDCOM-based schema** with extensions for AI features
- **Vector embeddings** for semantic search and face recognition

## 🛠️ Installation

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.9+ (for local development)

### Quick Start
1. **Clone the repository**:
   ```bash
   git clone https://github.com/trashcluster/genealogia.git
   cd genealogia
   ```

2. **Configure environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and preferences
   ```

3. **Start all services**:
   ```bash
   docker-compose up -d
   ```

4. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Environment Variables
Required variables in `.env`:
```bash
# Database
POSTGRES_PASSWORD=your_secure_password

# AI Providers (at least one required)
OPENAI_API_KEY=sk-your-openai-key
CLAUDE_API_KEY=sk-ant-your-claude-key
OLLAMA_URL=http://localhost:11434

# Telegram Bot (optional)
TELEGRAM_BOT_TOKEN=your-telegram-bot-token

# Application
SECRET_KEY=your-secret-key
BACKEND_API_KEY=sk-your-backend-api-key
```

## 📱 Usage

### Web Interface
1. **Dashboard**: Overview of statistics and recent activity
2. **Individuals**: Add, edit, and manage family members
3. **Family Tree**: Visual representation of relationships
4. **Timeline**: Chronological view of family events
5. **Knowledge Base**: Upload and search documents
6. **Face Recognition**: Manage photo collections and face clusters
7. **Ingestion**: Process text, voice, and document data
8. **Settings**: Configure AI providers and preferences

### Telegram Bot
Commands:
- `/start` - Begin interactive session
- `/help` - Show available commands
- `/status` - Check conversation status
- `/reset` - Clear conversation history

Features:
- **Text Messages**: Natural language data entry
- **Voice Messages**: Audio processing with transcription
- **Photos**: Face detection and person tagging
- **Documents**: File upload and content extraction
- **Interactive Q&A**: AI asks clarifying questions

## 🔧 Development

### Local Development Setup
1. **Backend Services**:
   ```bash
   cd packages/backend
   pip install -r requirements.txt
   uvicorn src.main:app --reload --port 8000
   ```

2. **Frontend**:
   ```bash
   cd packages/frontend
   npm install
   npm start
   ```

3. **Telegram Bot**:
   ```bash
   cd packages/telegram-bot
   pip install -r requirements.txt
   python src/main.py
   ```

### Project Structure
```
genealogia/
├── packages/
│   ├── backend/           # Core API service
│   ├── ingestion-service/ # AI data processing
│   ├── telegram-bot/      # Chat interface
│   ├── knowledge-base/    # Document management
│   ├── face-recognition/  # Image analysis
│   └── frontend/         # React web app
├── database/
│   └── schema.sql        # Database schema
├── docker-compose.yml      # Service orchestration
└── .env.example         # Environment template
```

## 🔒 Security

### Data Protection
- **API Key Encryption**: Secure storage of provider credentials
- **JWT Authentication**: Token-based API access
- **Input Validation**: Comprehensive data sanitization
- **Privacy Controls**: User-controlled data sharing options

### Best Practices
- Use strong, unique passwords
- Regularly rotate API keys
- Enable HTTPS in production
- Review privacy settings

## 📊 Monitoring

### Health Checks
All services include health endpoints:
- `/health` - Service status
- `/metrics` - Performance metrics
- `/docs` - API documentation

### Logging
- Structured JSON logging
- Error tracking and alerting
- Performance monitoring
- Audit trails for data changes

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

### Development Guidelines
- Follow PEP 8 for Python code
- Use TypeScript for React components
- Write comprehensive tests
- Update documentation

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the FAQ section

## 🗺️ Roadmap

### Upcoming Features
- [ ] Mobile application (React Native)
- [ ] Advanced family tree visualizations
- [ ] GEDCOM import/export improvements
- [ ] Collaborative family trees
- [ ] DNA integration
- [ ] Multi-language support

### Technical Improvements
- [ ] Enhanced AI model fine-tuning
- [ ] Real-time collaboration
- [ ] Advanced search capabilities
- [ ] Performance optimizations
- [ ] Extended file format support

---

**Genealogia** - Building family connections through intelligent technology.

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
