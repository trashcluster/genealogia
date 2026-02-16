from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from src.database import get_db
from src.schemas import User
from src.models import UserBase, UserRegister, UserLogin, UserResponse, UserWithAPIKey, Token
from src.auth import hash_password, verify_password, create_access_token, generate_api_key, get_current_user
from config.settings import get_settings

router = APIRouter(prefix="/api/auth", tags=["auth"])
settings = get_settings()

@router.post("/register", response_model=UserWithAPIKey)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user"""
    
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.username == user_data.username) | (User.email == user_data.email)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )
    
    # Create new user
    api_key = generate_api_key()
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        api_key=api_key,
        is_active=True
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return UserWithAPIKey(
        id=new_user.id,
        username=new_user.username,
        email=new_user.email,
        is_active=new_user.is_active,
        created_at=new_user.created_at,
        api_key=new_user.api_key
    )

@router.post("/login", response_model=Token)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """Login user and return JWT token"""
    
    user = db.query(User).filter(User.username == user_data.username).first()
    
    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive"
        )
    
    access_token = create_access_token(user.username)
    expires_in = settings.access_token_expire_minutes * 60
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=expires_in
    )

@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        is_active=current_user.is_active,
        created_at=current_user.created_at
    )

@router.post("/regenerate-api-key", response_model=UserWithAPIKey)
def regenerate_api_key(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Regenerate API key for current user"""
    
    new_api_key = generate_api_key()
    current_user.api_key = new_api_key
    
    db.commit()
    db.refresh(current_user)
    
    return UserWithAPIKey(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        api_key=current_user.api_key
    )
