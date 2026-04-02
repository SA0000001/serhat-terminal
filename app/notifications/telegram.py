import httpx

from app.notifications.base import NotificationService


class TelegramNotificationService(NotificationService):
    def __init__(self, bot_token: str, chat_id: str) -> None:
        self.bot_token = bot_token
        self.chat_id = chat_id

    def send(self, title: str, message: str) -> None:
        if not self.bot_token or not self.chat_id:
            return
        text = f"{title}\n\n{message}"
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        httpx.post(url, json={"chat_id": self.chat_id, "text": text}, timeout=10.0)
