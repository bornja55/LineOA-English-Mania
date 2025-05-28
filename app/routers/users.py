from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.models import User, Role
from app.schemas.schemas import UserResponse
from app.routers.line_auth import get_current_user  # สมมติมีฟังก์ชันนี้สำหรับดึง user จาก token

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

def require_role(allowed_roles: List[str]):
    def role_checker(current_user=Depends(get_current_user)):
        if current_user.role is None or current_user.role.name not in allowed_roles:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        return current_user
    return role_checker

@router.get("/me", response_model=UserResponse)
def read_own_profile(current_user=Depends(get_current_user)):
    return current_user

@router.get("/", response_model=List[UserResponse])
def list_users(
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["admin", "teacher"]))
):
    users = db.query(User).all()
    return users

@router.put("/{user_id}/role", response_model=UserResponse)
def update_user_role(
    user_id: int,
    role_name: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["admin"]))
):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    role = db.query(Role).filter(Role.name == role_name).first()
    if not role:
        raise HTTPException(status_code=400, detail="Role not found")
    user.role = role
    db.commit()
    db.refresh(user)
    return user