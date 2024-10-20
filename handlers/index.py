from .base import BaseHandler

class IndexHandler(BaseHandler):
    async def get(self):
        self.write({
            "email": True,
            "version": "0.1.0",
            "description": "Accounts and synchronization API."
        })
