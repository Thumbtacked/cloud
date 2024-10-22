import aiosmtplib
import random

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class EmailDeliveryService:
    __slots__ = ("display", "username", "password", "hostname", "port")

    def __init__(self, **config):
        self.display = config["display"]
        self.username = config["username"]
        self.password = config["password"]
        self.hostname = hostname = config["hostname"]
        self.port = port = config.get("port", 587)

    async def deliver(self, address, subject, content):
        message = MIMEMultipart()
        message["From"] = self.display
        message["To"] = address
        message["Subject"] = subject
        message.attach(MIMEText(content, "html"))

        async with aiosmtplib.SMTP(hostname=self.hostname, port=self.port) as smtp:
            await smtp.login(self.username, self.password)
            await smtp.send_message(message)
