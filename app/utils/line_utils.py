import requests
from app.core.config import settings

def verify_line_id_token(id_token):
    url = "https://api.line.me/oauth2/v2.1/verify"
    data = {
        "id_token": id_token,
        "client_id": settings.LINE_LOGIN_CHANNEL_ID
    }
    resp = requests.post(url, data=data)
    if resp.status_code == 200:
        return resp.json()
    return None

def send_line_message(line_user_id, message):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Authorization": f"Bearer {settings.LINE_CHANNEL_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "to": line_user_id,
        "messages": [{"type": "text", "text": message}]
    }
    resp = requests.post(url, headers=headers, json=data)
    return resp.status_code, resp.text