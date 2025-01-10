from __future__ import annotations

import asyncio
import asyncpg
import logging
import yaml
from typing import NoReturn

from .app import Application

try:
    import uvloop # type: ignore
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass

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

async def main() -> NoReturn:
    logger.info("Loading configuration file...")

    with open("config.yaml") as f:
        config = yaml.safe_load(f)

    logger.info("Initializing PostgreSQL connection...")

    pool = await asyncpg.create_pool(config["database_uri"])
    with open("schema.sql") as f:
        await pool.execute(f.read())

    logger.info("Starting the server on port %s", config.get("port", 8888))

    app = Application(config=config, database=pool)
    app.listen(config.get("port", 8888))
    await asyncio.Event().wait()

asyncio.run(main())
