from fastapi import APIRouter, HTTPException, Request, Depends
from sqlalchemy.orm import Session
from ..utils.line_utils import verify_line_id_token
from ..database import get_db
from ..models.models import User
from ..core.config import settings
from ..schemas.schemas import LineLoginRequest, TokenResponse
import jwt
from datetime import datetime, timedelta

router = APIRouter()

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

def get_or_create_user(db: Session, line_user_id: str, user_info: dict):
    user = db.query(User).filter(User.line_user_id == line_user_id).first()
    if user:
        return user
    # สร้าง username ชั่วคราวจาก line_user_id หรือ user_info
    username = user_info.get("username") or f"user_{line_user_id[-6:]}"
    new_user = User(
        line_user_id=line_user_id,
        username=username,
        name=user_info.get("name"),
        email=user_info.get("email"),
        # กำหนดค่าอื่น ๆ ตามต้องการ
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def create_jwt_token(user: User):
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(user.user_id),
        "name": user.name,
        "exp": expire
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

@router.post(
    "/auth/line",
    response_model=TokenResponse,
    summary="Login with LINE ID token",
    description="รับ id_token จาก LINE Login แล้วตรวจสอบและสร้าง JWT token สำหรับการยืนยันตัวตน"
)
async def line_login(request_data: LineLoginRequest, db: Session = Depends(get_db)):
    """
    Endpoint สำหรับรับ id_token จาก LINE Login

    - **id_token**: Token ที่ได้จาก LINE Login SDK
    - คืนค่า JWT access token สำหรับใช้ยืนยันตัวตนใน API อื่น ๆ
    """
    id_token = request_data.id_token
    if not id_token:
        raise HTTPException(status_code=400, detail="Missing id_token")

    user_info = verify_line_id_token(id_token)
    if not user_info:
        raise HTTPException(status_code=401, detail="Invalid LINE token")

    line_user_id = user_info["sub"]
    user = get_or_create_user(db, line_user_id, user_info)
    access_token = create_jwt_token(user)

    return {"access_token": access_token, "token_type": "bearer"}