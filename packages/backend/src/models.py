from pydantic import BaseModel, EmailStr
from datetime import date, datetime
from typing import Optional, List
from uuid import UUID

# User models
class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserRegister(UserBase):
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(UserBase):
    id: UUID
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserWithAPIKey(UserResponse):
    api_key: str

# Individual models
class IndividualBase(BaseModel):
    given_names: Optional[str] = None
    surname: Optional[str] = None
    sex: Optional[str] = None  # M, F, U
    birth_date: Optional[date] = None
    birth_place: Optional[str] = None
    death_date: Optional[date] = None
    death_place: Optional[str] = None
    note: Optional[str] = None

class IndividualCreate(IndividualBase):
    gedcom_id: str

class IndividualUpdate(IndividualBase):
    pass

class IndividualResponse(IndividualBase):
    id: UUID
    user_id: UUID
    gedcom_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Family group models
class FamilyGroupBase(BaseModel):
    husband_id: Optional[UUID] = None
    wife_id: Optional[UUID] = None
    marriage_date: Optional[date] = None
    marriage_place: Optional[str] = None
    divorce_date: Optional[date] = None
    note: Optional[str] = None

class FamilyGroupCreate(FamilyGroupBase):
    gedcom_id: str

class FamilyGroupResponse(FamilyGroupBase):
    id: UUID
    user_id: UUID
    gedcom_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Event models
class EventBase(BaseModel):
    event_type: str
    event_date: Optional[date] = None
    event_place: Optional[str] = None
    description: Optional[str] = None
    note: Optional[str] = None

class EventCreate(EventBase):
    individual_id: Optional[UUID] = None
    family_group_id: Optional[UUID] = None

class EventResponse(EventBase):
    id: UUID
    user_id: UUID
    individual_id: Optional[UUID] = None
    family_group_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Token models
class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

class TokenData(BaseModel):
    username: str

# Health check
class HealthResponse(BaseModel):
    status: str
    version: str
