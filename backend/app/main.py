from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import logging
from app.database import init_db
from app.api.v1.endpoints import router

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="CiteGraph API", version="1.0.0")

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.on_event("startup")
async def startup_event():
    """
    Initialize database on startup.
    No database calls at import time - all initialization happens here.
    """
    logger.info("Starting up CiteGraph API...")
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


app.include_router(router, prefix="/api/v1", tags=["v1"])


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serve the main web interface."""
    import os
    static_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    with open(static_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

