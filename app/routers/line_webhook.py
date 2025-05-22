from fastapi import APIRouter, Request

router = APIRouter()

@router.post("/webhook/line")
async def line_webhook(request: Request):
    body = await request.json()
    print("LINE Webhook Event:", body)
    # TODO: เขียน logic ตอบกลับหรือบันทึก event ตามต้องการ
    return {"status": "ok"}