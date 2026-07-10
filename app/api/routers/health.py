from fastapi import APIRouter, Depends
from packages.shared.config.settings import Settings
from app.api.deps import get_settings_dep
from packages.core.logging import get_logger

router = APIRouter()

@router.get("/")
def health(settings: Settings = Depends(get_settings_dep)):
    logger = get_logger("api.health")
    logger.info("Health check requested")
    
    return {
        "status": "ok",
        "app": settings.app_name,
        "env": settings.app_env.name,
        "debug": settings.app_debug,
    }