from fastapi import APIRouter, HTTPException, Request, Depends
from sqlalchemy.orm import Session
from ..utils.line_utils import verify_line_id_token
from ..database import get_db
from ..models.models import User
from ..schemas.line import LineUserInfo
from ..schemas.auth import LineLoginRequest, TokenResponse
import jwt
from datetime import datetime, timedelta

router = APIRouter()

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

def get_or_create_user(db: Session, line_user_id: str, user_info: dict):
    user = db.query(User).filter(User.line_user_id == line_user_id).first()
    if not user:
        user = User(
            line_user_id=line_user_id,
            name=user_info.get("name"),
            email=user_info.get("email"),
            username=user_info.get("email")  # อาจใช้ email เป็น username ชั่วคราว
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        # ถ้าเจอ user แล้ว ให้อัปเดตข้อมูล (ถ้าต้องการ)
        user.name = user_info.get("name")
        user.email = user_info.get("email")
        db.commit()
        db.refresh(user)
    return user

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