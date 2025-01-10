from __future__ import annotations

import tornado
from typing import TYPE_CHECKING

from server.utils import MISSING

if TYPE_CHECKING:
    from app import Application


class BaseHandler(tornado.web.RequestHandler):
    application: Application

    def initialize(self):
        self.body: dict = MISSING

    async def prepare(self):
        token = self.get_cookie("token")
        if not token:
            return

        validated = self.application.token.validate_token(token)
        if not validated:
            return self.unset_token()

        user = await self.application.database.get_user(validated.user_id)
        if not user or user.max_token_age > validated.age:
            return self.unset_token()

        self.current_user = user

    def write_error(self, status_code: int, *, message: str = "Experienced an unknown error.", **_):
        self.set_status(status_code)
        self.finish({"message": message})

    def options(self):
        self.set_status(204)

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "*")
        self.set_header("Access-Control-Allow-Methods", "*")
        self.set_header("Content-Type", "application/json")

    def set_token(self, token: str):
        self.set_cookie("token", token, httponly=True)

    def unset_token(self):
        self.clear_cookie("token")
