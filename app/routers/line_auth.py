from fastapi import APIRouter, HTTPException, Request, Depends
from sqlalchemy.orm import Session
from ..utils.line_utils import verify_line_id_token
from ..database import get_db
from ..models.models import User
import jwt
from datetime import datetime, timedelta

router = APIRouter()

SECRET_KEY = "your_secret_key_here"  # เปลี่ยนเป็นคีย์จริงของคุณ
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 วัน

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
        "sub": str(user.id),
        "name": user.name,
        "exp": expire
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

@router.post("/auth/line")
async def line_login(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    id_token = data.get("id_token")
    if not id_token:
        raise HTTPException(status_code=400, detail="Missing id_token")

    user_info = verify_line_id_token(id_token)
    if not user_info:
        raise HTTPException(status_code=401, detail="Invalid LINE token")

    line_user_id = user_info["sub"]
    user = get_or_create_user(db, line_user_id, user_info)
    access_token = create_jwt_token(user)

    return {"access_token": access_token, "token_type": "bearer"}