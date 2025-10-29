"""
Módulo de inicialización del core
"""
from app.core.config import settings, get_settings
from app.core.logger import logger, get_logger

__all__ = ["settings", "get_settings", "logger", "get_logger"]
