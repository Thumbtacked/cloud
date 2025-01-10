from __future__ import annotations

from .base import BaseHandler
from server.utils import validate

class AccountHandler(BaseHandler):
    @validate({
        "name": {"type": "string", "minlength": 1, "maxlength": 64},
        "email": {"type": "string", "minlength": 3, "maxlength": 320},
        "password": {"type": "string", "minlength": 8, "maxlength": 72},
        "code": {"type": "integer", "min": 10**8, "max": 10**9-1}
    })
    async def post(self):
        name = self.body["name"]
        email = self.body["email"]
        password = self.body["password"]
        code = self.body["code"]

        if self.application.registration_codes.get(email) != code:
            return self.send_error(400, message="Email and registration code do not match.")

        user_id, max_token_age = self.application.token.current_id()
        await self.application.database.create_user(user_id, name, email, password, max_token_age)
        self.application.registration_codes.pop(email)

        self.write({
            "id": user_id,
            "name": name,
            "email": email
        })

    @validate({
        "current_password": {"type": "string", "minlength": 8, "maxlength": 72},
        "name": {"type": "string", "minlength": 1, "maxlength": 64},
        "email": {"type": "string", "minlength": 3, "max": 320, "dependencies": ["current_password", "code"]},
        "password": {"type": "string", "minlength": 8, "maxlength": 72, "dependencies": ["current_password"]},
        "code": {"type": "integer", "min": 10**8, "max": 10**9-1}
    }, require_all=False, require_authentication=True)
    async def patch(self):
        current_password = self.body.get("current_password")
        name = self.body.get("name")
        email = self.body.get("email")
        password = self.body.get("password")
        code = self.body.get("code")

        if password and not (await self.current_user.check_password(current_password)):
            return self.send_error(400, message="Current password is invalid.")

        if email and self.application.registration_codes.get(email) != code:
            return self.send_error(400, message="Email and registration code do not match.")

        await self.current_user.update(name=name, email=email, password=password)

        self.write({
            "id": self.current_user.id,
            "name": self.current_user.name,
            "email": self.current_user.email
        })
