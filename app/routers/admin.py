from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import User, Role
from app.schemas.schemas import UserResponse, UserBase
from app.routers.auth import admin_required

router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)

@router.get("/users", response_model=list[UserResponse])
def list_users(db: Session = Depends(get_db), admin=Depends(admin_required(["admin"]))):
    users = db.query(User).all()
    return users

@router.put("/users/{user_id}/role")
def update_user_role(user_id: int, role_id: int, db: Session = Depends(get_db), admin=Depends(admin_required(["admin"]))):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    role = db.query(Role).filter(Role.role_id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    user.role_id = role_id
    db.commit()
    return {"message": "User role updated successfully"}