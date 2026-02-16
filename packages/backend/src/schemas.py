from sqlalchemy import Column, String, UUID, Boolean, DateTime, Date, Text, Integer, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
import uuid
from src.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(255), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    api_key = Column(String(255), unique=True, nullable=False, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    individuals = relationship("Individual", back_populates="user", cascade="all, delete-orphan")
    family_groups = relationship("FamilyGroup", back_populates="user", cascade="all, delete-orphan")
    events = relationship("Event", back_populates="user", cascade="all, delete-orphan")
    ingestion_logs = relationship("IngestionLog", back_populates="user", cascade="all, delete-orphan")

class Individual(Base):
    __tablename__ = "individuals"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    gedcom_id = Column(String(255), nullable=False)
    given_names = Column(Text)
    surname = Column(String(255), index=True)
    sex = Column(String(1))  # M, F, U
    birth_date = Column(Date, index=True)
    birth_place = Column(Text)
    death_date = Column(Date)
    death_place = Column(Text)
    note = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="individuals")
    events = relationship("Event", back_populates="individual", cascade="all, delete-orphan")

class FamilyGroup(Base):
    __tablename__ = "family_groups"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    gedcom_id = Column(String(255), nullable=False)
    husband_id = Column(UUID(as_uuid=True), ForeignKey("individuals.id"))
    wife_id = Column(UUID(as_uuid=True), ForeignKey("individuals.id"))
    marriage_date = Column(Date)
    marriage_place = Column(Text)
    divorce_date = Column(Date)
    note = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="family_groups")
    events = relationship("Event", back_populates="family_group", cascade="all, delete-orphan")

class Event(Base):
    __tablename__ = "events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    individual_id = Column(UUID(as_uuid=True), ForeignKey("individuals.id"), index=True)
    family_group_id = Column(UUID(as_uuid=True), ForeignKey("family_groups.id"), index=True)
    event_type = Column(String(50), index=True)
    event_date = Column(Date)
    event_place = Column(Text)
    description = Column(Text)
    note = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="events")
    individual = relationship("Individual", back_populates="events")
    family_group = relationship("FamilyGroup", back_populates="events")

class IngestionLog(Base):
    __tablename__ = "ingestion_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    source_type = Column(String(50))  # TELEGRAM, CARDDAV, FILE, etc.
    source_id = Column(String(255))
    content_type = Column(String(50))  # TEXT, VOICE, IMAGE, PDF
    status = Column(String(50), index=True)  # PENDING, PROCESSING, SUCCESS, ERROR
    error_message = Column(Text)
    extracted_data = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="ingestion_logs")
