"""
Servicio especializado de OpenAI para análisis médico
Optimizado para GPT-4o-mini con prompts estructurados
"""
from typing import Optional, Dict, Any
import json
import logging
from openai import AsyncOpenAI
from app.core.config import settings

logger = logging.getLogger(__name__)


class OpenAIService:
    """
    Servicio de OpenAI para análisis de seguimientos post-tratamiento
    """
    
    def __init__(self):
        """Inicializa el cliente de OpenAI"""
        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL if hasattr(settings, 'OPENAI_BASE_URL') else None
        )
        self.model = settings.OPENAI_MODEL if hasattr(settings, 'OPENAI_MODEL') else "gpt-4o-mini"
        logger.info(f"🤖 OpenAIService inicializado con modelo: {self.model}")
    
    async def analizar_seguimiento_post_tratamiento(
        self,
        prompt: str,
        paciente_nombre: str,
        tipo_tratamiento: str,
        temperature: float = 0.3,
        max_tokens: int = 800
    ) -> str:
        """
        Analiza respuesta de seguimiento post-tratamiento usando GPT-4o-mini
        
        Args:
            prompt: Prompt completo con datos del paciente y su respuesta
            paciente_nombre: Nombre del paciente
            tipo_tratamiento: Tipo de tratamiento realizado
            temperature: Temperatura para el modelo (0.3 = más determinístico)
            max_tokens: Máximo de tokens en la respuesta
            
        Returns:
            str: Respuesta JSON con el análisis estructurado
        """
        
        logger.info(
            f"🔍 Iniciando análisis IA - Paciente: {paciente_nombre}, "
            f"Tratamiento: {tipo_tratamiento}"
        )
        
        try:
            # Llamada a OpenAI con configuración optimizada
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un asistente médico especializado en odontología. "
                                   "Tu tarea es analizar respuestas de seguimiento post-tratamiento "
                                   "y detectar posibles complicaciones. "
                                   "Siempre respondes en formato JSON válido."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                response_format={"type": "json_object"}  # Forzar JSON válido
            )
            
            # Extraer contenido
            content = response.choices[0].message.content
            
            # Validar que sea JSON válido
            json.loads(content)  # Esto lanza excepción si no es JSON válido
            
            logger.info(
                f"✅ Análisis completado - Tokens usados: {response.usage.total_tokens}"
            )
            
            return content
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ GPT retornó JSON inválido: {str(e)}")
            # Retornar fallback estructurado
            return self._get_fallback_response(paciente_nombre)
            
        except Exception as e:
            logger.error(f"❌ Error en llamada a OpenAI: {str(e)}")
            raise
    
    def _get_fallback_response(self, paciente_nombre: str) -> str:
        """
        Respuesta de fallback cuando GPT falla
        """
        fallback = {
            "nivel_urgencia": "medio",
            "requiere_atencion": True,
            "sentimiento_general": "neutral",
            "sintomas_detectados": ["Requiere revisión manual"],
            "recomendacion": "Por favor, contacta al paciente para revisar su respuesta manualmente. El análisis automático no pudo completarse.",
            "resumen": f"Análisis automático falló para {paciente_nombre}. Requiere revisión manual.",
            "probabilidad_complicacion": 0.5,
            "necesita_cita_urgente": False
        }
        return json.dumps(fallback)
