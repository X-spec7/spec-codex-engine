from fastapi import FastAPI
from packages.shared.config.settings import get_settings
from packages.core.logging import configure_logging, get_logger
from .routers.health import router as health_router

def create_app() -> FastAPI:
    """
    Application factory: creates a FastAPI app with logging and routers.
    """
    
    # Configure logging once
    configure_logging()
    logger = get_logger("api.app")
    
    settings = get_settings()
    
    app = FastAPI(
        title=settings.app_name,
        debug=settings.app_debug,
        version=settings.version
    )
    
    app.include_router(health_router, prefix="/health", tags=["health"])
    
    logger.info("FastAPI app created", app_name=settings.app_name)
    
    return app