from fastapi import APIRouter, Request
from ..utils.line_utils import send_line_message

router = APIRouter()

@router.post("/webhook/line")
async def line_webhook(request: Request):
    body = await request.json()
    print("LINE Webhook Event:", body)
    # TODO: เขียน logic ตอบกลับหรือบันทึก event ตามต้องการ
    return {"status": "ok"}