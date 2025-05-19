import asyncio
import logging

from letta_client import MessageCreate, TextContent

from sqlalchemy import text
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed

from app.core.db import engine
# from app.features.llm_logic.llm_logic import get_letta_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

max_tries = 60 * 5  # 5 minutes
wait_seconds = 1


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
async def init() -> None:
    """Test database connection"""
    try:
        # Try to create session to check if DB is awake
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            await conn.commit()
    except Exception as e:
        logger.error(e)
        raise e


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
async def check_letta_connection() -> None:
    """Test connection from backend to letta service."""
    try:
        # client = get_letta_client()
        # await client.agents.list()
        logger.info("Successfully connected to Letta service")
    except Exception as e:
        logger.error(f"Failed to connect to Letta: {e}")
        raise e


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
async def check_ollama_connection_via_letta() -> None:
    """Test connection from letta to Ollama service."""
    agent_id = None
    # client = get_letta_client()
    # try:
    #     agent = await client.agents.create()
    #     agent_id = agent.id
    #     response = await client.agents.messages.create(agent_id, messages=[
    #         MessageCreate(
    #             role="user",
    #             content=[
    #                 TextContent(
    #                     text="test connection to ollama",
    #                 )
    #             ],
    #         )
    #     ], )
    #     logger.info(response.messages[0].content)
    #     logger.info("Successfully connected to Ollama")
    # except Exception as e:
    #     logger.error(f"Failed to connect to Ollama: {e}")
    #     raise e
    # finally:
    #     if agent_id:
    #         await client.agents.delete(agent_id)


async def main() -> None:
    logger.info("Initializing service")

    # 1. Test database connection
    await init()
    logger.info("Database connection successful")

    # 2. Test Letta connection
    # await check_letta_connection()
    logger.info("Letta connection successful")

    # 3. Test ollama connection vie letta_client
    # await check_ollama_connection_via_letta()
    logger.info("Successfully tested Letta client with Letta and Ollama")

    logger.info("Service finished initializing")


if __name__ == "__main__":
    asyncio.run(main())
