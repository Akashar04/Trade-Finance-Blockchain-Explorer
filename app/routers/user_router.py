from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import schemas, models, auth, deps

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.post("/", response_model=schemas.UserResponse)
def create_user_admin(user: schemas.UserCreate, 
                      db: Session = Depends(deps.get_db), 
                      current_user: models.User = Depends(deps.get_current_user)):
    
    # Only Admin can create users via this endpoint
    if current_user.role != models.UserRole.admin:
        raise HTTPException(status_code=403, detail="Only admin can create users here")

    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = auth.hash_password(user.password) # Use hash_password from auth (same as signup)
    
    db_user = models.User(
        name=user.name,
        email=user.email,
        password=hashed_password,
        org_name=user.org_name,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/all", response_model=List[schemas.UserResponse])
def read_all_users(db: Session = Depends(deps.get_db), 
                   current_user: models.User = Depends(deps.get_current_user)):
    
    if current_user.role != models.UserRole.admin:
        raise HTTPException(status_code=403, detail="Only admin can list users")
        
    users = db.query(models.User).all()
    return users

@router.get("/me", response_model=schemas.UserResponse) # Ensure Response Model
def read_users_me(current_user: models.User = Depends(deps.get_current_user)):
    return current_user
