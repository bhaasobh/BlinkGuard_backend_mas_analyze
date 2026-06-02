import uvicorn

from app.config import get_port, logger
from app.main import app

if __name__ == "__main__":
    port = get_port()
    logger.info("Launching uvicorn on host=0.0.0.0 port=%s", port)
    uvicorn.run(app, host="0.0.0.0", port=port)
