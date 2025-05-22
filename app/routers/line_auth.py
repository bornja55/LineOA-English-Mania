from fastapi import APIRouter, HTTPException, Request
from app.line_utils import verify_line_id_token
# สมมติว่ามีฟังก์ชัน get_or_create_user และ create_jwt_token อยู่แล้ว

router = APIRouter()

@router.post("/auth/line")
async def line_login(request: Request):
    data = await request.json()
    id_token = data.get("id_token")
    if not id_token:
        raise HTTPException(status_code=400, detail="Missing id_token")
    user_info = verify_line_id_token(id_token)
    if not user_info:
        raise HTTPException(status_code=401, detail="Invalid LINE token")
    line_user_id = user_info["sub"]
    # TODO: เช็คหรือสร้าง user ใน DB ด้วย line_user_id
    # user = get_or_create_user(line_user_id)
    # access_token = create_jwt_token(user)
    # return {"access_token": access_token, "token_type": "bearer"}
    return {"line_user_id": line_user_id, "user_info": user_info}