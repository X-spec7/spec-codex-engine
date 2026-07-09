from enum import StrEnum

class Environment(StrEnum):
    """Supported application environments."""
    
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"
    
class LogLevel(StrEnum):
    """Supported logging levels."""
    
    INFO = "INFO"
    DEBUG = "DEBUG"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"