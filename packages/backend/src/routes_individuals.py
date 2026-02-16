from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from src.database import get_db
from src.schemas import User, Individual
from src.models import IndividualCreate, IndividualUpdate, IndividualResponse
from src.auth import get_current_user

router = APIRouter(prefix="/api/individuals", tags=["individuals"])

@router.post("", response_model=IndividualResponse)
def create_individual(
    individual_data: IndividualCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new individual"""
    
    # Check if GEDCOM ID already exists for this user
    existing = db.query(Individual).filter(
        Individual.user_id == current_user.id,
        Individual.gedcom_id == individual_data.gedcom_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Individual with this GEDCOM ID already exists"
        )
    
    new_individual = Individual(
        user_id=current_user.id,
        **individual_data.dict()
    )
    
    db.add(new_individual)
    db.commit()
    db.refresh(new_individual)
    
    return new_individual

@router.get("", response_model=List[IndividualResponse])
def list_individuals(
    surname: str = Query(None),
    given_names: str = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all individuals for current user"""
    
    query = db.query(Individual).filter(Individual.user_id == current_user.id)
    
    if surname:
        query = query.filter(Individual.surname.ilike(f"%{surname}%"))
    
    if given_names:
        query = query.filter(Individual.given_names.ilike(f"%{given_names}%"))
    
    individuals = query.offset(skip).limit(limit).all()
    return individuals

@router.get("/{individual_id}", response_model=IndividualResponse)
def get_individual(
    individual_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific individual"""
    
    individual = db.query(Individual).filter(
        Individual.id == individual_id,
        Individual.user_id == current_user.id
    ).first()
    
    if not individual:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Individual not found")
    
    return individual

@router.put("/{individual_id}", response_model=IndividualResponse)
def update_individual(
    individual_id: UUID,
    individual_data: IndividualUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an individual"""
    
    individual = db.query(Individual).filter(
        Individual.id == individual_id,
        Individual.user_id == current_user.id
    ).first()
    
    if not individual:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Individual not found")
    
    update_data = individual_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(individual, field, value)
    
    db.commit()
    db.refresh(individual)
    
    return individual

@router.delete("/{individual_id}")
def delete_individual(
    individual_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an individual"""
    
    individual = db.query(Individual).filter(
        Individual.id == individual_id,
        Individual.user_id == current_user.id
    ).first()
    
    if not individual:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Individual not found")
    
    db.delete(individual)
    db.commit()
    
    return {"message": "Individual deleted successfully"}
