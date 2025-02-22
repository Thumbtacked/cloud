from __future__ import annotations

import base64
import datetime
import itsdangerous


class TokenGenerator:
    __slots__  = ("_signer", "epoch", "counter")

    def __init__(self, secret: str):
        self._signer: itsdangerous.TimestampSigner = itsdangerous.TimestampSigner(secret)
        self.epoch: int = 1704067200
        self.counter: int = 1

    def current_id(self):
        now = self._signer.get_timestamp()
        self.counter += 1
        user_id = int(now - self.epoch) << 64
        user_id |= self.counter
        return str(user_id), self._signer.timestamp_to_datetime(now).replace(tzinfo=None)

    def current_time(self):
        return self._signer.timestamp_to_datetime(self._signer.get_timestamp()).replace(tzinfo=None)

    def create_token(self, user_id: str):
        encoded_user_id = base64.b64encode(user_id.encode())
        return self._signer.sign(encoded_user_id).decode()

    def validate_token(self, token: str):
        try:
            return ValidatedToken(*self._signer.unsign(token, return_timestamp=True))
        except itsdangerous.BadData:
            return None


class ValidatedToken:
    __slots__ = ("user_id", "age")

    def __init__(self, encoded_user_id: bytes, created_at: datetime.datetime):
        self.user_id: str = base64.b64decode(encoded_user_id).decode()
        self.age: datetime.datetime = created_at.replace(tzinfo=None)
