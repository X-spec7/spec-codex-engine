import structlog
from typing import Optional, Mapping, Any

def get_logger(name: str, context: Optional[Mapping[str, Any]] = None) -> structlog.BoundLogger:
    """
    Return a structured logger for a given module.
    """
    
    logger = structlog.get_logger(name)
    if context:
        logger = logger.bind(**context)
        
    return logger