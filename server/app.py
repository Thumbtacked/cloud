from __future__ import annotations

import tornado
from typing import TYPE_CHECKING, Mapping

from . import utils
from . import handlers

if TYPE_CHECKING:
    import asyncpg


class Application(tornado.web.Application):
    def __init__(self, *, config: Mapping, database: asyncpg.Pool):
        super().__init__([
            (r"/", handlers.IndexHandler),
            (r"/account", handlers.AccountHandler),
            (r"/registration", handlers.RegistrationHandler),
            (r"/login", handlers.LoginHandler)
        ])

        self.config: Mapping = config
        self.database: utils.DatabaseWrapper = utils.DatabaseWrapper(database)
        self.email: utils.EmailDeliveryService = utils.EmailDeliveryService(config["email"])
        self.token: utils.TokenGenerator = utils.TokenGenerator(config["secret"])
        self.registration_codes: utils.ExpiringDictionary = utils.ExpiringDictionary(max_age=15*60)
