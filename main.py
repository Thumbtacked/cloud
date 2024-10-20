import asyncio
import asyncpg
import tornado
import yaml

import handlers
import utils

try:
    import uvloop
except ImportError:
    uvloop = None

class Application(tornado.web.Application):
    def __init__(self, config, *, connection):
        super().__init__([
            (r"/", handlers.IndexHandler),
            (r"/account", handlers.AccountHandler),
            (r"/registration", handlers.RegistrationHandler),
            (r"/login", handlers.LoginHandler)
        ])

        self.config = config
        self.database = utils.DatabaseWrapper(connection, tornado.ioloop.IOLoop.current())
        self.email = utils.EmailDeliveryService(**config["email"])
        self.token = utils.TokenGenerator(config["secret"])
        self.registration_codes = utils.ExpiringDictionary(max_age=15*60)

async def main():
    with open("config.yaml") as f:
        config = yaml.safe_load(f)

    pool = await asyncpg.create_pool(config["database_uri"])

    with open("schema.sql") as f:
        await pool.execute(f.read())

    app = Application(config, connection=pool)
    app.listen(config.get("port", 8888))

    await asyncio.Event().wait()

if __name__ == "__main__":
    if uvloop:
        uvloop.run(main())
    else:
        asyncio.run(main())
