import asyncio
import asyncpg
import logging
import tornado
import yaml

import handlers
import utils

try:
    import uvloop
except ImportError:
    uvloop = None

logger = logging.getLogger(__name__)
logging.basicConfig(
    encoding="utf-8",
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
    level=logging.DEBUG,
    handlers=[
        logging.FileHandler("thumbtacked.log"),
        logging.StreamHandler()
    ]
)

class Application(tornado.web.Application):
    def __init__(self, config, *, connection):
        super().__init__([
            (r"/", handlers.IndexHandler),
            (r"/account", handlers.AccountHandler),
            (r"/registration", handlers.RegistrationHandler),
            (r"/login", handlers.LoginHandler)
        ])

        self.log = logger
        self.config = config
        self.database = utils.DatabaseWrapper(connection, tornado.ioloop.IOLoop.current())
        self.email = utils.EmailDeliveryService(**config["email"])
        self.token = utils.TokenGenerator(config["secret"])
        self.registration_codes = utils.ExpiringDictionary(max_age=15*60)

async def main():
    logger.info("Loading configuration file...")

    with open("config.yaml") as f:
        config = yaml.safe_load(f)

    logger.info("Initializing PostgreSQL connection...")

    pool = await asyncpg.create_pool(config["database_uri"])

    with open("schema.sql") as f:
        await pool.execute(f.read())

    logger.info("Starting the server on port %s", config.get("port", 8888))

    app = Application(config, connection=pool)
    app.listen(config.get("port", 8888))
    await asyncio.Event().wait()

if __name__ == "__main__":
    if uvloop:
        uvloop.run(main())
    else:
        asyncio.run(main())
