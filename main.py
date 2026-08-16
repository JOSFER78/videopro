import os
import sys

# Ensure workspace root is first in PYTHONPATH
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import uvicorn
from loguru import logger
from app.config import config

if __name__ == "__main__":
    logger.info(
        f"start VideoPro server, docs: http://127.0.0.1:{config.listen_port}/docs"
    )
    uvicorn.run(
        app="app.asgi:app",
        host=config.listen_host,
        port=config.listen_port,
        reload=False,
        log_level="warning",
    )
