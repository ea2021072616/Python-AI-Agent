"""
Punto de entrada principal del microservicio
"""
import uvicorn
from app import create_app
from app.core import settings

# Crear la aplicación
app = create_app()

if __name__ == "__main__":
    # Ejecutar el servidor
    uvicorn.run(
        "main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.is_development,
        log_level=settings.LOG_LEVEL.lower()
    )
