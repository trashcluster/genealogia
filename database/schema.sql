-- GEDCOM-based genealogical database schema
-- Follows GEDCOM 5.7.1 standard

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

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
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_gedcom_id_per_user UNIQUE(user_id, gedcom_id)
);

CREATE INDEX idx_individuals_user_id ON individuals(user_id);
CREATE INDEX idx_individuals_surname ON individuals(surname) USING GIST(surname gist_trgm_ops);
CREATE INDEX idx_individuals_birth_date ON individuals(birth_date);

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
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_events_user_id ON events(user_id);
CREATE INDEX idx_events_individual_id ON events(individual_id);
CREATE INDEX idx_events_family_group_id ON events(family_group_id);
CREATE INDEX idx_events_event_type ON events(event_type);

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
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_media_user_id ON media(user_id);
CREATE INDEX idx_media_individual_id ON media(individual_id);

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
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_ingestion_logs_user_id ON ingestion_logs(user_id);
CREATE INDEX idx_ingestion_logs_status ON ingestion_logs(status);
CREATE INDEX idx_ingestion_logs_created_at ON ingestion_logs(created_at);

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
