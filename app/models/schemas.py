"""
Modelos de datos del microservicio usando Pydantic
Definen la estructura de datos que se intercambian
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ========================================
# Enums
# ========================================

class MessageRole(str, Enum):
    """Roles de mensajes en el chat"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class CitaEstado(str, Enum):
    """Estados de una cita"""
    PENDIENTE = "pendiente"
    CONFIRMADA = "confirmada"
    COMPLETADA = "completada"
    CANCELADA = "cancelada"
    REPROGRAMADA = "reprogramada"


# ========================================
# Modelos de Chat
# ========================================

class ChatMessage(BaseModel):
    """Mensaje individual en una conversación"""
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Optional[Dict[str, Any]] = None


class ChatRequest(BaseModel):
    """Request para el endpoint de chat"""
    message: str = Field(..., min_length=1, max_length=1000, description="Mensaje del usuario")
    session_id: Optional[str] = Field(None, description="ID de sesión para mantener contexto")
    user_id: Optional[int] = Field(None, description="ID del usuario autenticado (opcional)")
    user_context: Optional[Dict[str, Any]] = Field(None, description="Contexto adicional del usuario")
    
    @field_validator('message')
    @classmethod
    def validate_message(cls, v: str) -> str:
        """Valida que el mensaje no esté vacío"""
        if not v.strip():
            raise ValueError("El mensaje no puede estar vacío")
        return v.strip()


class ChatResponse(BaseModel):
    """Response del endpoint de chat"""
    message: str
    session_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Optional[Dict[str, Any]] = None
    suggested_actions: Optional[List[str]] = None


# ========================================
# Modelos de Backend (Laravel)
# ========================================

class PacienteInfo(BaseModel):
    """Información básica de un paciente"""
    id_paciente: int
    nombres: str
    apellidos: str
    dni: Optional[str] = None
    fecha_nacimiento: Optional[str] = None
    sexo: Optional[str] = None
    telefono: Optional[str] = None
    correo: Optional[str] = None
    alergias: Optional[str] = None
    grupo_sanguineo: Optional[str] = None


class MedicoInfo(BaseModel):
    """Información básica de un médico"""
    id_medico: int
    nombres: str
    apellidos: str
    especialidad: Optional[str] = None
    colegiatura: Optional[str] = None
    telefono: Optional[str] = None


class CitaInfo(BaseModel):
    """Información de una cita"""
    id_cita: int
    fecha_hora_inicio: str
    fecha_hora_fin: str
    motivo: str
    estado: CitaEstado
    paciente: Optional[PacienteInfo] = None
    medico: Optional[MedicoInfo] = None
    notas: Optional[str] = None


class HistorialClinicoInfo(BaseModel):
    """Información de historial clínico"""
    id_historial: int
    id_paciente: int
    fecha_atencion: str
    diagnostico: Optional[str] = None
    tratamiento_realizado: Optional[str] = None
    observaciones: Optional[str] = None
    medico: Optional[MedicoInfo] = None


# ========================================
# Modelos de Respuesta de Herramientas
# ========================================

class ToolResponse(BaseModel):
    """Respuesta genérica de una herramienta"""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    message: Optional[str] = None


# ========================================
# Modelos de Sesión
# ========================================

class SessionInfo(BaseModel):
    """Información de una sesión de chat"""
    session_id: str
    user_id: Optional[int] = None
    created_at: datetime
    last_activity: datetime
    message_count: int = 0
    metadata: Optional[Dict[str, Any]] = None


# ========================================
# Modelos de Health Check
# ========================================

class HealthStatus(BaseModel):
    """Estado de salud del servicio"""
    status: str
    timestamp: datetime = Field(default_factory=datetime.now)
    version: str = "1.0.0"
    services: Dict[str, bool] = Field(default_factory=dict)
    details: Optional[Dict[str, Any]] = None
