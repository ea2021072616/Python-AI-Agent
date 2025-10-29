"""
Endpoints de la API REST
Define todas las rutas y controladores
"""
from fastapi import APIRouter, HTTPException, Header
from typing import Optional
from datetime import datetime
from app.models import ChatRequest, ChatResponse, HealthStatus
from app.services import agent_service
from app.utils.http_client import backend_client
from app.core import settings, logger

# Router principal
router = APIRouter()

# Importar router de seguimiento
from app.api import seguimiento

# Incluir subrouters
router.include_router(seguimiento.router, prefix="/seguimiento", tags=["Seguimiento"])


# ========================================
# Health Check
# ========================================

@router.get("/health", response_model=HealthStatus, tags=["Sistema"])
async def health_check():
    """
    Verifica el estado de salud del microservicio
    
    Returns:
        Estado del servicio y sus dependencias
    """
    logger.info("🏥 Health check solicitado")
    
    # Verificar backend
    backend_status = await backend_client.health_check()
    
    status = HealthStatus(
        status="healthy" if backend_status else "degraded",
        services={
            "backend": backend_status,
            "openai": bool(settings.OPENAI_API_KEY),
            "agent": True
        },
        details={
            "active_sessions": agent_service.get_active_sessions_count(),
            "environment": settings.APP_ENV
        }
    )
    
    return status


# ========================================
# Chat
# ========================================

@router.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(
    request: ChatRequest,
    x_user_id: Optional[str] = Header(None, description="ID del usuario autenticado")
):
    """
    Procesa un mensaje de chat y retorna la respuesta del agente
    
    Args:
        request: Datos de la solicitud de chat
        x_user_id: ID del usuario (opcional, desde header)
    
    Returns:
        Respuesta del agente con el mensaje y metadata
    """
    try:
        logger.info(f"💬 Nueva solicitud de chat - Session: {request.session_id}")
        
        # Usar user_id del header si está disponible
        user_id = None
        if x_user_id:
            try:
                user_id = int(x_user_id)
            except ValueError:
                pass
        
        # Si no viene del header, usar el del request
        if not user_id and request.user_id:
            user_id = request.user_id
        
        # Procesar el mensaje
        result = await agent_service.process_message(
            message=request.message,
            session_id=request.session_id,
            user_id=user_id,
            user_context=request.user_context
        )
        
        # Crear respuesta
        response = ChatResponse(
            message=result["message"],
            session_id=result["session_id"],
            metadata=result.get("metadata")
        )
        
        logger.info(f"✅ Respuesta enviada - Session: {response.session_id}")
        return response
        
    except Exception as e:
        logger.error(f"❌ Error en endpoint de chat: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error procesando el mensaje: {str(e)}")


# ========================================
# Sesiones
# ========================================

@router.get("/sessions/{session_id}/history", tags=["Sesiones"])
async def get_session_history(session_id: str):
    """
    Obtiene el historial de una sesión de chat
    
    Args:
        session_id: ID de la sesión
    
    Returns:
        Lista de mensajes de la sesión
    """
    try:
        history = agent_service.get_session_history(session_id)
        
        return {
            "session_id": session_id,
            "message_count": len(history),
            "messages": [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat()
                }
                for msg in history
            ]
        }
    except Exception as e:
        logger.error(f"❌ Error obteniendo historial: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/sessions/{session_id}", tags=["Sesiones"])
async def clear_session(session_id: str):
    """
    Limpia una sesión de chat específica
    
    Args:
        session_id: ID de la sesión a limpiar
    
    Returns:
        Mensaje de confirmación
    """
    try:
        agent_service.clear_session(session_id)
        return {"message": "Sesión limpiada exitosamente", "session_id": session_id}
    except Exception as e:
        logger.error(f"❌ Error limpiando sesión: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/active/count", tags=["Sesiones"])
async def get_active_sessions():
    """
    Obtiene el número de sesiones activas
    
    Returns:
        Número de sesiones activas
    """
    count = agent_service.get_active_sessions_count()
    return {
        "active_sessions": count,
        "timestamp": datetime.now().isoformat()
    }


# ========================================
# Información del Sistema
# ========================================

@router.get("/info", tags=["Sistema"])
async def get_info():
    """
    Obtiene información del microservicio
    
    Returns:
        Información general del servicio
    """
    return {
        "name": settings.APP_NAME,
        "version": "1.0.0",
        "environment": settings.APP_ENV,
        "model": settings.OPENAI_MODEL,
        "tools_count": len(agent_service.tools),
        "tools": [tool.name for tool in agent_service.tools]
    }
