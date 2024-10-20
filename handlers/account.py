import tornado

from .base import BaseHandler
from utils import validate

class AccountHandler(BaseHandler):
    @validate({
        "name": {"type": "string", "min": 1, "max": 64},
        "email": {"type": "string", "min": 3, "max": 320},
        "password": {"type": "string", "min": 8, "max": 72},
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
        "current_password": {"type": "string", "min": 8, "max": 72, "dependencies": ["email", "password"]},
        "name": {"type": "string", "min": 1, "max": 64},
        "email": {"type": "string", "min": 1, "min": 3, "max": 320, "dependencies": ["code"]},
        "password": {"type": "string", "min": 8, "max": 72},
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
            "id": current_user.id,
            "name": current_user.name,
            "email": current_User.email
        })
