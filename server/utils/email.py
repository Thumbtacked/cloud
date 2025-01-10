from __future__ import annotations

import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class EmailDeliveryService:
    __slots__ = ("display", "username", "password", "hostname", "port")

    def __init__(self, config: dict) -> None:
        self.display: str = config["display"]
        self.username: str = config["username"]
        self.password: str = config["password"]
        self.hostname: str = config["hostname"]
        self.port: int = config.get("port", 587)

    async def deliver(self, address: str, subject: str, content: str) -> None:
        message = MIMEMultipart()
        message["From"] = self.display
        message["To"] = address
        message["Subject"] = subject
        message.attach(MIMEText(content, "html"))

        async with aiosmtplib.SMTP(hostname=self.hostname, port=self.port) as smtp:
            await smtp.login(self.username, self.password)
            await smtp.send_message(message)
