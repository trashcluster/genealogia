# Genealogia - AI-Powered Family Tree Management

A comprehensive family tree web application with AI-powered data ingestion, face recognition, and knowledge base capabilities built on Firebase.

## 🚀 Features

### Core Functionality
- **Firebase Gemini AI Integration**: Advanced AI processing with Google's Gemini models
- **Interactive Web Interface**: Modern React frontend with real-time updates
- **Face Recognition**: Automatic face detection, clustering, and person identification
- **Knowledge Base**: Document storage with semantic search and event extraction
- **Family Tree Visualization**: Interactive genealogical relationships and timeline views
- **Modern UI**: Responsive design with Tailwind CSS and Heroicons

### Data Ingestion Methods
- **Text Input**: Direct text entry with AI processing
- **Voice Messages**: Audio-to-text conversion and analysis
- **Document Upload**: PDF, images, text files with OCR and content extraction
- **Photo Analysis**: Face detection and person identification

### AI-Powered Features
- **Smart Data Extraction**: Automatic person, relationship, and event identification
- **Interactive Questioning**: AI asks clarifying questions to improve data quality
- **Multi-Modal Processing**: Text, voice, and document analysis
- **Event Correlation**: Cross-reference events across documents and media

## 🏗️ Architecture

### Firebase Serverless Design
- **Firebase Hosting**: React web application (Port 3000)
- **Cloud Functions**: Serverless backend for AI processing and API endpoints
- **Cloud Firestore**: NoSQL database for genealogical data
- **Firebase Storage**: File storage for documents, photos, and media
- **Firebase Authentication**: User management and security

### Database Structure
- **Firestore Collections**: User-isolated data with proper indexing
- **Document Schema**: Optimized for genealogical relationships
- **Security Rules**: User-based data isolation and access control

## 🛠️ Installation

### Prerequisites
- Firebase account (create at https://firebase.google.com)
- Node.js 18+ (for local development)
- Firebase CLI (`npm install -g firebase-tools`)

### Quick Start

1. **Clone the repository**:
   ```bash
   git clone https://github.com/trashcluster/genealogia.git
   cd genealogia
   ```

2. **Initialize Firebase**:
   ```bash
   firebase login
   firebase init
   ```

3. **Configure environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your Firebase configuration
   ```

4. **Install dependencies**:
   ```bash
   cd functions && npm install
   cd ../frontend-firebase && npm install
   ```

5. **Deploy to Firebase**:
   ```bash
   firebase deploy
   ```

6. **Access the application**:
   - Frontend: https://your-project.firebaseapp.com
   - Functions: https://your-region-your-project.cloudfunctions.net

## 📱 Usage

### Web Interface
1. **Dashboard**: Overview of statistics and recent activity
2. **Individuals**: Add, edit, and manage family members
3. **Family Tree**: Visual representation of relationships
4. **Timeline**: Chronological view of family events
5. **Knowledge Base**: Upload and search documents
6. **Face Recognition**: Manage photo collections and face clusters
7. **Ingestion**: Process text, voice, and document data
8. **Settings**: Configure AI preferences and user profile

### Features
- **Natural Language Processing**: Enter family information in natural language
- **Voice Input**: Record voice messages for data entry
- **Document Processing**: Upload PDFs and images for automatic extraction
- **Photo Tagging**: Automatic face detection and person identification
- **Interactive Q&A**: AI-guided data collection process

## 🔧 Development

### Local Development Setup

1. **Start Firebase Emulators**:
   ```bash
   firebase emulators:start
   ```

2. **Run Frontend Locally**:
   ```bash
   cd frontend-firebase
   npm start
   ```

3. **Test Functions**:
   ```bash
   cd functions
   npm run shell
   ```

### Project Structure
```
genealogia/
├── functions/                 # Cloud Functions
│   ├── src/
│   │   ├── index.ts          # Main functions
│   │   ├── auth.ts           # Authentication
│   │   ├── individuals.ts    # Individual management
│   │   ├── ingestion.ts      # AI processing
│   │   └── ...
│   └── package.json
├── frontend-firebase/         # React frontend
│   ├── src/
│   │   ├── firebase.ts       # Firebase config
│   │   ├── components/       # React components
│   │   └── pages/           # Page components
│   └── package.json
├── firebase.json             # Firebase configuration
├── firestore.rules           # Database security rules
├── storage.rules             # File security rules
└── README.md                 # This file
```

## 🔒 Security

### Data Protection
- **Firebase Authentication**: Secure user authentication
- **Firestore Security Rules**: User data isolation
- **Storage Security Rules**: File access control
- **Input Validation**: Comprehensive data sanitization

### Best Practices
- Use strong passwords
- Enable two-factor authentication
- Regularly review security rules
- Monitor Firebase console for suspicious activity

## 📊 Monitoring

### Firebase Console
- **Functions**: Monitor execution and performance
- **Firestore**: Database usage and queries
- **Storage**: File storage and bandwidth
- **Authentication**: User activity and security

### Logging
- **Function Logs**: Detailed execution logs
- **Error Tracking**: Automatic error reporting
- **Performance Metrics**: Response times and usage

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

### Development Guidelines
- Use TypeScript for type safety
- Follow Firebase security best practices
- Write comprehensive tests
- Update documentation

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the Firebase documentation
- Review the troubleshooting section

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
