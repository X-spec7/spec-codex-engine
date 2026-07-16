from packages.shared.config.settings import Settings, get_settings

def get_settings_dep() -> Settings:
    """Dependency for FastAPI routes."""
    return get_settings()
