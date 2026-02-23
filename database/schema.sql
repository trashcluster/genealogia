-- Enhanced GEDCOM-based genealogical database schema
-- Follows GEDCOM 5.7.1 standard with extensions for AI and face recognition

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "pgvector";

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    api_key VARCHAR(255) UNIQUE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Individuals (INDI records in GEDCOM)
CREATE TABLE individuals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    gedcom_id VARCHAR(255) NOT NULL, -- XREF ID from GEDCOM
    given_names TEXT,
    surname TEXT,
    sex CHAR(1), -- 'M', 'F', or 'U' for unknown
    birth_date DATE,
    birth_place TEXT,
    death_date DATE,
    death_place TEXT,
    note TEXT,
    face_ids TEXT[], -- Array of face recognition IDs
    ai_extracted BOOLEAN DEFAULT FALSE,
    confidence_score FLOAT DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_gedcom_id_per_user UNIQUE(user_id, gedcom_id)
);

CREATE INDEX idx_individuals_user_id ON individuals(user_id);
CREATE INDEX idx_individuals_surname ON individuals(surname) USING GIST(surname gist_trgm_ops);
CREATE INDEX idx_individuals_birth_date ON individuals(birth_date);
CREATE INDEX idx_individuals_face_ids ON individuals USING GIN(face_ids);

-- Family groups (FAM records in GEDCOM)
CREATE TABLE family_groups (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    gedcom_id VARCHAR(255) NOT NULL, -- XREF ID from GEDCOM
    husband_id UUID REFERENCES individuals(id) ON DELETE SET NULL,
    wife_id UUID REFERENCES individuals(id) ON DELETE SET NULL,
    marriage_date DATE,
    marriage_place TEXT,
    divorce_date DATE,
    note TEXT,
    ai_extracted BOOLEAN DEFAULT FALSE,
    confidence_score FLOAT DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_gedcom_id_per_user UNIQUE(user_id, gedcom_id)
);

CREATE INDEX idx_family_groups_user_id ON family_groups(user_id);
CREATE INDEX idx_family_groups_husband_id ON family_groups(husband_id);
CREATE INDEX idx_family_groups_wife_id ON family_groups(wife_id);

-- Children relationships (CHIL records in GEDCOM)
CREATE TABLE children (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    family_group_id UUID NOT NULL REFERENCES family_groups(id) ON DELETE CASCADE,
    individual_id UUID NOT NULL REFERENCES individuals(id) ON DELETE CASCADE,
    birth_order INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_child_per_family UNIQUE(family_group_id, individual_id)
);

CREATE INDEX idx_children_user_id ON children(user_id);
CREATE INDEX idx_children_family_group_id ON children(family_group_id);
CREATE INDEX idx_children_individual_id ON children(individual_id);

-- Events (EVEN records in GEDCOM)
CREATE TABLE events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    individual_id UUID REFERENCES individuals(id) ON DELETE CASCADE,
    family_group_id UUID REFERENCES family_groups(id) ON DELETE CASCADE,
    event_type VARCHAR(50), -- BIRTH, BURI, CENS, DEAT, EDUC, EMPL, GRAD, MARR, etc.
    event_date DATE,
    event_place TEXT,
    description TEXT,
    note TEXT,
    ai_extracted BOOLEAN DEFAULT FALSE,
    confidence_score FLOAT DEFAULT 0.0,
    source_document_id UUID, -- Link to knowledge documents
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_events_user_id ON events(user_id);
CREATE INDEX idx_events_individual_id ON events(individual_id);
CREATE INDEX idx_events_family_group_id ON events(family_group_id);
CREATE INDEX idx_events_event_type ON events(event_type);
CREATE INDEX idx_events_source_document_id ON events(source_document_id);

-- Media files
CREATE TABLE media (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    individual_id UUID REFERENCES individuals(id) ON DELETE SET NULL,
    family_group_id UUID REFERENCES family_groups(id) ON DELETE SET NULL,
    event_id UUID REFERENCES events(id) ON DELETE SET NULL,
    file_path TEXT NOT NULL,
    file_type VARCHAR(50), -- IMAGE, PDF, DOCUMENT, etc.
    file_name VARCHAR(255),
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    face_detection_results JSONB, -- Store face detection data
    ocr_text TEXT, -- Extracted text from OCR
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_media_user_id ON media(user_id);
CREATE INDEX idx_media_individual_id ON media(individual_id);
CREATE INDEX idx_media_face_detection ON media USING GIN(face_detection_results);

-- Sources (SOUR records in GEDCOM)
CREATE TABLE sources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255),
    author VARCHAR(255),
    publication_date DATE,
    repository TEXT,
    text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sources_user_id ON sources(user_id);

-- Source citations (connects sources to individuals/events)
CREATE TABLE source_citations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    source_id UUID NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    individual_id UUID REFERENCES individuals(id) ON DELETE CASCADE,
    event_id UUID REFERENCES events(id) ON DELETE CASCADE,
    page_number VARCHAR(50),
    confidence_level INT DEFAULT 3, -- 0-5 scale
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_source_citations_user_id ON source_citations(user_id);
CREATE INDEX idx_source_citations_source_id ON source_citations(source_id);

-- Notes
CREATE TABLE notes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    individual_id UUID REFERENCES individuals(id) ON DELETE CASCADE,
    family_group_id UUID REFERENCES family_groups(id) ON DELETE CASCADE,
    event_id UUID REFERENCES events(id) ON DELETE CASCADE,
    note_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_notes_user_id ON notes(user_id);
CREATE INDEX idx_notes_individual_id ON notes(individual_id);

-- Ingestion logs
CREATE TABLE ingestion_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    source_type VARCHAR(50), -- TELEGRAM, CARDDAV, FILE, etc.
    source_id VARCHAR(255),
    content_type VARCHAR(50), -- TEXT, VOICE, IMAGE, PDF
    status VARCHAR(50), -- PENDING, PROCESSING, SUCCESS, ERROR
    error_message TEXT,
    extracted_data JSONB,
    ai_provider_used VARCHAR(50), -- openai, claude, ollama
    processing_time_ms INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_ingestion_logs_user_id ON ingestion_logs(user_id);
CREATE INDEX idx_ingestion_logs_status ON ingestion_logs(status);
CREATE INDEX idx_ingestion_logs_created_at ON ingestion_logs(created_at);
CREATE INDEX idx_ingestion_logs_ai_provider ON ingestion_logs(ai_provider_used);

-- === NEW TABLES FOR ENHANCED FEATURES ===

-- Face recognition embeddings
CREATE TABLE face_embeddings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    individual_id UUID REFERENCES individuals(id) ON DELETE SET NULL,
    person_name VARCHAR(255),
    embedding VECTOR(512), -- Face embedding vector
    model_version VARCHAR(50) DEFAULT 'facenet',
    confidence_score FLOAT DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_face_embeddings_user_id ON face_embeddings(user_id);
CREATE INDEX idx_face_embeddings_individual_id ON face_embeddings(individual_id);
CREATE INDEX idx_face_embeddings_person_name ON face_embeddings(person_name);
CREATE INDEX idx_face_embeddings_embedding ON face_embeddings USING ivfflat (embedding vector_cosine_ops);

-- Face images and metadata
CREATE TABLE face_images (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    face_embedding_id UUID NOT NULL REFERENCES face_embeddings(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    individual_id UUID REFERENCES individuals(id) ON DELETE SET NULL,
    person_name VARCHAR(255),
    image_path TEXT NOT NULL,
    image_width INT,
    image_height INT,
    face_metadata JSONB, -- Bounding box, landmarks, etc.
    quality_score FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_face_images_user_id ON face_images(user_id);
CREATE INDEX idx_face_images_individual_id ON face_images(individual_id);

-- Knowledge base documents
CREATE TABLE knowledge_documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(500),
    filename VARCHAR(255),
    document_type VARCHAR(50), -- pdf, image, text, calendar, etc.
    content TEXT,
    metadata JSONB, -- Additional document metadata
    file_size INT,
    embedding VECTOR(768), -- Document embedding for semantic search
    processed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_knowledge_documents_user_id ON knowledge_documents(user_id);
CREATE INDEX idx_knowledge_documents_type ON knowledge_documents(document_type);
CREATE INDEX idx_knowledge_documents_embedding ON knowledge_documents USING ivfflat (embedding vector_cosine_ops);

-- Extracted events from knowledge base
CREATE TABLE extracted_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    document_id UUID REFERENCES knowledge_documents(id) ON DELETE CASCADE,
    event_type VARCHAR(50),
    event_date DATE,
    event_place TEXT,
    description TEXT,
    individuals_involved JSONB, -- Array of individual references
    confidence FLOAT DEFAULT 0.0,
    source_data JSONB, -- Original extracted data
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_extracted_events_user_id ON extracted_events(user_id);
CREATE INDEX idx_extracted_events_document_id ON extracted_events(document_id);
CREATE INDEX idx_extracted_events_type ON extracted_events(event_type);

-- Document embeddings for semantic search
CREATE TABLE document_embeddings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES knowledge_documents(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    chunk_text TEXT,
    chunk_index INT,
    embedding VECTOR(768),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_document_embeddings_document_id ON document_embeddings(document_id);
CREATE INDEX idx_document_embeddings_embedding ON document_embeddings USING ivfflat (embedding vector_cosine_ops);

-- Conversation sessions for Telegram bot
CREATE TABLE conversation_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    chat_id VARCHAR(100) NOT NULL,
    session_state VARCHAR(50) DEFAULT 'idle', -- idle, questioning, confirming, etc.
    current_data JSONB,
    pending_questions TEXT[],
    answered_questions JSONB,
    session_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP
);

CREATE INDEX idx_conversation_sessions_user_id ON conversation_sessions(user_id);
CREATE INDEX idx_conversation_sessions_chat_id ON conversation_sessions(chat_id);
CREATE INDEX idx_conversation_sessions_state ON conversation_sessions(session_state);

-- AI provider configuration and usage tracking
CREATE TABLE ai_providers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    provider_name VARCHAR(50), -- openai, claude, ollama
    provider_config JSONB, -- API keys, model settings, etc.
    is_enabled BOOLEAN DEFAULT TRUE,
    priority INT DEFAULT 1, -- Provider priority for fallback
    usage_count INT DEFAULT 0,
    last_used TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_ai_providers_user_id ON ai_providers(user_id);
CREATE INDEX idx_ai_providers_name ON ai_providers(provider_name);

-- Event correlations and relationships
CREATE TABLE event_correlations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    event1_id UUID NOT NULL REFERENCES extracted_events(id) ON DELETE CASCADE,
    event2_id UUID NOT NULL REFERENCES extracted_events(id) ON DELETE CASCADE,
    correlation_type VARCHAR(50), -- temporal, spatial, causal, etc.
    correlation_score FLOAT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_event_correlations_user_id ON event_correlations(user_id);
CREATE INDEX idx_event_correlations_event1 ON event_correlations(event1_id);
CREATE INDEX idx_event_correlations_event2 ON event_correlations(event2_id);

-- Face clustering results
CREATE TABLE face_clusters (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    cluster_id INT,
    face_embedding_id UUID NOT NULL REFERENCES face_embeddings(id) ON DELETE CASCADE,
    confidence_score FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_face_clusters_user_id ON face_clusters(user_id);
CREATE INDEX idx_face_clusters_cluster_id ON face_clusters(cluster_id);

-- Processing logs for debugging and monitoring
CREATE TABLE processing_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    service_name VARCHAR(100), -- ingestion, face-recognition, knowledge-base, etc.
    operation_type VARCHAR(100), -- detect_faces, extract_text, etc.
    input_data JSONB,
    output_data JSONB,
    processing_time_ms INT,
    success BOOLEAN,
    error_message TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_processing_logs_user_id ON processing_logs(user_id);
CREATE INDEX idx_processing_logs_service ON processing_logs(service_name);
CREATE INDEX idx_processing_logs_created_at ON processing_logs(created_at);

-- Create trigger for updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_individuals_updated_at BEFORE UPDATE ON individuals
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_family_groups_updated_at BEFORE UPDATE ON family_groups
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_events_updated_at BEFORE UPDATE ON events
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sources_updated_at BEFORE UPDATE ON sources
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_notes_updated_at BEFORE UPDATE ON notes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_ingestion_logs_updated_at BEFORE UPDATE ON ingestion_logs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_face_embeddings_updated_at BEFORE UPDATE ON face_embeddings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_knowledge_documents_updated_at BEFORE UPDATE ON knowledge_documents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_ai_providers_updated_at BEFORE UPDATE ON ai_providers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_conversation_sessions_updated_at BEFORE UPDATE ON conversation_sessions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
