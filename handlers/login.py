import time

from .base import BaseHandler
from utils import validate

class LoginHandler(BaseHandler):
    @validate({
        "email": {"type": "string"},
        "password": {"type": "string"}
    })
    async def post(self):
        email = self.body["email"]
        password = self.body["password"]

        user = await self.application.database.get_user_by_email(email)
  
        if not user or not (await user.check_password(password)):
            return self.set_status(400, message="Email or password is invalid.")

        self.set_token(self.application.token.create_token(user.id))
        self.set_status(204)

    @validate({
        "refresh": {"type": "boolean"},
        "all": {"type": "boolean"}
    }, require_all=False, require_authentication=True)
    async def delete(self):
        if self.body.get("all"):
            await self.current_user.update(max_token_age=self.application.token.current_time())

        if self.body.get("refresh"):
            self.set_token(self.application.token.create_token(user.id))
        else:
            self.unset_token()

        self.set_status(204)
