import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.core.logging_conf import configure_logging

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    configure_logging()

    # Initialize container resources
    if hasattr(app.state, "container"):
        app.state.container.init_resources()
        logger.info("Container resources initialized")

    logger.info("Startup event completed")

    yield

    # Shutdown container resources
    if hasattr(app.state, "container"):
        app.state.container.shutdown_resources()
        logger.info("Container resources shutdown")

    logger.info("Shutdown event completed")
