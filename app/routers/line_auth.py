from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from ..utils.line_utils import verify_line_id_token
from ..database import get_db
from ..models.models import User, RefreshToken, Role  # import Role model
from ..core.config import settings
from ..schemas.schemas import LineLoginRequest, TokenResponse, RefreshTokenRequest, RefreshTokenResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from datetime import datetime, timedelta

router = APIRouter(
    prefix="/auth/line",
    tags=["line_auth"]
)

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = 30

bearer_scheme = HTTPBearer()

def get_or_create_user(db: Session, line_user_id: str, user_info: dict):
    user = db.query(User).filter(User.line_user_id == line_user_id).first()
    if user:
        return user
    username = user_info.get("username") or f"user_{line_user_id[-6:]}"
    # ดึง role_id ของ student จากตาราง role
    student_role = db.query(Role).filter(Role.role_name == "student").first()
    if not student_role:
        raise HTTPException(status_code=500, detail="Role 'student' not found")
    new_user = User(
        line_user_id=line_user_id,
        username=username,
        password_hash="",
        name=user_info.get("name"),
        email=user_info.get("email"),
        role_id=student_role.role_id
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def create_access_token(user: User, db: Session):
    role = db.query(Role).filter(Role.role_id == user.role_id).first()
    role_name = user.role.role_name if user.role else "student"
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(user.user_id),
        "role": role_name,
        "exp": expire
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

def create_refresh_token(user: User):
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": str(user.user_id),
        "exp": expire
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

def store_refresh_token(db: Session, user: User, refresh_token: str):
    db.query(RefreshToken).filter(RefreshToken.user_id == user.user_id).delete()
    db_refresh_token = RefreshToken(
        user_id=user.user_id,
        token=refresh_token,
        created_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )
    db.add(db_refresh_token)
    db.commit()
    db.refresh(db_refresh_token)
    return db_refresh_token

@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login with LINE ID token",
    description="รับ id_token จาก LINE Login แล้วตรวจสอบและสร้าง JWT token สำหรับการยืนยันตัวตน"
)
async def line_login(request_data: LineLoginRequest, db: Session = Depends(get_db)):
    id_token = request_data.id_token
    if not id_token:
        raise HTTPException(status_code=400, detail="Missing id_token")

    user_info = verify_line_id_token(id_token)
    if not user_info:
        raise HTTPException(status_code=401, detail="Invalid LINE token")

    line_user_id = user_info["sub"]
    user = get_or_create_user(db, line_user_id, user_info)
    access_token = create_access_token(user, db)
    refresh_token = create_refresh_token(user)
    store_refresh_token(db, user, refresh_token)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post(
    "/refresh",
    response_model=RefreshTokenResponse,
    summary="Refresh access token",
    description="รับ refresh token เพื่อขอ access token ใหม่"
)
async def refresh_access_token(request_data: RefreshTokenRequest, db: Session = Depends(get_db)):
    refresh_token = request_data.refresh_token
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    db_refresh_token = db.query(RefreshToken).filter(
        RefreshToken.user_id == int(user_id),
        RefreshToken.token == refresh_token,
        RefreshToken.expires_at > datetime.utcnow()
    ).first()

    if not db_refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")

    user = db.query(User).filter(User.user_id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    new_access_token = create_access_token(user, db)
    return {"access_token": new_access_token, "token_type": "bearer"}

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme), db: Session = Depends(get_db)):
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        role: str = payload.get("role")
        if user_id is None or role is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.user_id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    return {"user": user, "role": role}