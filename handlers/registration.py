import aiosmtplib
import secrets
import tornado

from .base import BaseHandler
from utils import validate

class RegistrationHandler(BaseHandler):
    @validate({
        "email": {"type": "string", "minlength": 3, "maxlength": 320}
    })
    async def post(self):
        email = self.body["email"]

        if (await self.application.database.get_user_by_email(email)):
            return self.send_error(400, message="Email is already registered.")

        code = secrets.choice(range(10**8, 10**9-1))
        subject = f"Thumbtacked Registration Code"
        content = f"""
        Your registration code is {code}.
        
        This code will last up to 15 minutes. Do not share it with anyone.
        """

        try:
            await self.application.email.deliver(email, subject, content)
        except (aiosmtplib.SMTPRecipientsRefused, aiosmtplib.SMTPException):
            return self.send_error(400, message="Unable to deliver registration code to email.")

        self.application.log.info("Sent registration code %s to %s", code, email)
        self.application.registration_codes[email] = code
        self.set_status(204)
