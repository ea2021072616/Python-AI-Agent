"""
Módulo de inicialización de la aplicación FastAPI
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core import settings, logger
from app.api.endpoints import router


def create_app() -> FastAPI:
    """
    Crea y configura la aplicación FastAPI
    
    Returns:
        Aplicación FastAPI configurada
    """
    
    # Crear aplicación
    app = FastAPI(
        title=settings.APP_NAME,
        description="Microservicio de Agente Conversacional con IA para Arludent",
        version="1.0.0",
        debug=settings.APP_DEBUG,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json"
    )
    
    # Configurar CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Incluir rutas
    app.include_router(router, prefix="/api/v1")
    
    # Eventos de inicio y cierre
    @app.on_event("startup")
    async def startup_event():
        logger.info("=" * 50)
        logger.info(f"🚀 {settings.APP_NAME} iniciando...")
        logger.info(f"📍 Entorno: {settings.APP_ENV}")
        logger.info(f"🤖 Modelo: {settings.OPENAI_MODEL}")
        logger.info(f"🔧 Herramientas: {len(app.state.tools) if hasattr(app.state, 'tools') else 'N/A'}")
        logger.info("=" * 50)
    
    @app.on_event("shutdown")
    async def shutdown_event():
        logger.info("👋 Cerrando microservicio...")
    
    return app
