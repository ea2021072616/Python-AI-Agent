"""
Sistema de logging centralizado usando loguru
Proporciona logs estructurados y fáciles de debuggear
"""
import sys
from pathlib import Path
from loguru import logger
from app.core.config import settings


def setup_logging():
    """
    Configura el sistema de logging
    - Logs en consola con colores (desarrollo)
    - Logs en archivo con rotación (producción)
    """
    
    # Remover handler por defecto
    logger.remove()
    
    # Configuración de formato
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )
    
    # Handler para consola (con colores en desarrollo)
    if settings.is_development:
        logger.add(
            sys.stdout,
            format=log_format,
            level=settings.LOG_LEVEL,
            colorize=True,
            backtrace=True,
            diagnose=True
        )
    else:
        logger.add(
            sys.stdout,
            format=log_format,
            level=settings.LOG_LEVEL,
            colorize=False
        )
    
    # Handler para archivo (con rotación)
    log_path = Path(settings.LOG_FILE)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    logger.add(
        settings.LOG_FILE,
        format=log_format,
        level=settings.LOG_LEVEL,
        rotation="500 MB",  # Rotar cuando alcance 500MB
        retention="10 days",  # Mantener logs por 10 días
        compression="zip",  # Comprimir logs antiguos
        backtrace=True,
        diagnose=True
    )
    
    logger.info(f"🚀 Logging configurado - Nivel: {settings.LOG_LEVEL}")
    logger.info(f"📁 Archivo de log: {settings.LOG_FILE}")


# Inicializar logging al importar el módulo
setup_logging()


def get_logger(name: str):
    """
    Obtiene un logger con un nombre específico
    
    Args:
        name: Nombre del módulo/componente
    
    Returns:
        Logger configurado
    """
    return logger.bind(module=name)
