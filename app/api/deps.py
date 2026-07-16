from packages.shared.config.settings import get_settings
from packages.core.logging import get_logger

def get_settings_dep():
    """Dependency for FastAPI routes."""
    return get_settings()

def get_logger_dep(name: str = "api.route"):
    """Dependency for route-level logging."""
    return get_logger(name)