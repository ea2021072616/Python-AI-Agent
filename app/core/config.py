"""
Configuración centralizada del microservicio
Carga variables de entorno y las hace disponibles en toda la aplicación
"""
from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache


class Settings(BaseSettings):
    """
    Configuración principal de la aplicación
    Todas las variables se cargan desde .env
    """
    
    # Aplicación
    APP_NAME: str = "Arludent AI Microservice"
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8001
    
    # OpenAI / LLM
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    OPENAI_TEMPERATURE: float = 0.4
    OPENAI_MAX_TOKENS: int = 3000
    
    # Backend Laravel
    BACKEND_URL: str = "http://127.0.0.1:8000"
    BACKEND_INTERNAL_API_KEY: str
    BACKEND_TIMEOUT: int = 30
    
    # Laravel API (para webhook)
    LARAVEL_API_URL: str = "http://127.0.0.1:8000"
    INTERNAL_API_KEY: str  # Token para autenticación del webhook
    
    # Redis
    REDIS_ENABLED: bool = False
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""
    
    # Base de Datos
    DATABASE_ENABLED: bool = False
    DATABASE_URL: str = "sqlite:///./arludent_ai.db"
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"
    CORS_ALLOW_CREDENTIALS: bool = True
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 50
    RATE_LIMIT_PERIOD: int = 60
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    
    # Seguridad
    SECRET_KEY: str
    API_KEY_HEADER: str = "X-API-Key"
    
    # Configuración del Agente
    AGENT_MAX_ITERATIONS: int = 10
    AGENT_TIMEOUT: int = 60
    CONVERSATION_HISTORY_LIMIT: int = 20
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Convierte el string de orígenes CORS en lista"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    @property
    def is_production(self) -> bool:
        """Verifica si está en producción"""
        return self.APP_ENV == "production"
    
    @property
    def is_development(self) -> bool:
        """Verifica si está en desarrollo"""
        return self.APP_ENV == "development"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    Singleton para obtener la configuración
    Se carga una sola vez y se cachea
    """
    return Settings()


# Instancia global de configuración
settings = get_settings()
