"""
Utilidades varias del microservicio
"""
import uuid
import hashlib
from datetime import datetime
from typing import Optional


def generate_session_id() -> str:
    """
    Genera un ID único para una sesión
    
    Returns:
        String UUID único
    """
    return str(uuid.uuid4())


def hash_string(text: str) -> str:
    """
    Genera un hash SHA256 de un texto
    
    Args:
        text: Texto a hashear
    
    Returns:
        Hash hexadecimal
    """
    return hashlib.sha256(text.encode()).hexdigest()


def format_datetime(dt: Optional[datetime] = None) -> str:
    """
    Formatea una fecha/hora en formato ISO
    
    Args:
        dt: Datetime a formatear (por defecto: ahora)
    
    Returns:
        String en formato ISO
    """
    if dt is None:
        dt = datetime.now()
    return dt.isoformat()


def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Trunca un texto a una longitud máxima
    
    Args:
        text: Texto a truncar
        max_length: Longitud máxima
    
    Returns:
        Texto truncado con "..." si es necesario
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def sanitize_input(text: str) -> str:
    """
    Sanitiza el input del usuario
    
    Args:
        text: Texto a sanitizar
    
    Returns:
        Texto limpio
    """
    # Remover caracteres peligrosos
    text = text.strip()
    # Remover múltiples espacios
    text = " ".join(text.split())
    return text
