"""
Cliente HTTP para comunicación con el Backend Laravel
Maneja todas las solicitudes HTTP de forma centralizada
"""
import httpx
from typing import Optional, Dict, Any
from app.core import settings, logger


class BackendClient:
    """
    Cliente para comunicarse con el backend Laravel
    
    Este cliente se usa para llamar a los endpoints internos del backend
    que NO requieren autenticación JWT (comunicación interna segura)
    """
    
    def __init__(self):
        self.base_url = settings.BACKEND_URL
        self.timeout = settings.BACKEND_TIMEOUT
        self.api_key = settings.BACKEND_INTERNAL_API_KEY
        self.headers = {
            "X-Internal-API-Key": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        logger.info(f"🔌 BackendClient inicializado - URL: {self.base_url}")
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Realiza una solicitud HTTP al backend
        
        Args:
            method: Método HTTP (GET, POST, PUT, DELETE)
            endpoint: Endpoint relativo (ej: /api/internal/pacientes)
            data: Datos para el body (POST/PUT)
            params: Parámetros de query string
        
        Returns:
            Dict con la respuesta JSON
        
        Raises:
            Exception: Si hay error en la comunicación
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                logger.debug(f"📡 {method} {url}")
                
                response = await client.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    json=data,
                    params=params
                )
                
                response.raise_for_status()
                result = response.json()
                
                logger.debug(f"✅ Response: {response.status_code}")
                return result
                
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ HTTP Error {e.response.status_code}: {e.response.text}")
            raise Exception(f"Error del backend: {e.response.status_code}")
        except httpx.RequestError as e:
            logger.error(f"❌ Request Error: {str(e)}")
            raise Exception(f"Error de conexión con el backend: {str(e)}")
        except Exception as e:
            logger.error(f"❌ Unexpected Error: {str(e)}")
            raise
    
    # ========================================
    # Endpoints de Pacientes
    # ========================================
    
    async def get_paciente(self, paciente_id: int) -> Dict[str, Any]:
        """Obtiene información de un paciente por ID"""
        return await self._make_request("GET", f"/api/internal/pacientes/{paciente_id}")
    
    async def get_pacientes(
        self,
        limit: int = 10,
        search: Optional[str] = None
    ) -> Dict[str, Any]:
        """Lista pacientes con filtros opcionales"""
        params = {"limit": limit}
        if search:
            params["search"] = search
        return await self._make_request("GET", "/api/internal/pacientes", params=params)
    
    async def buscar_paciente_por_dni(self, dni: str) -> Dict[str, Any]:
        """Busca un paciente por DNI"""
        return await self._make_request("GET", f"/api/internal/pacientes/dni/{dni}")
    
    # ========================================
    # Endpoints de Citas
    # ========================================
    
    async def get_cita(self, cita_id: int) -> Dict[str, Any]:
        """Obtiene información de una cita por ID"""
        return await self._make_request("GET", f"/api/internal/citas/{cita_id}")
    
    async def get_citas_paciente(
        self,
        paciente_id: int,
        estado: Optional[str] = None
    ) -> Dict[str, Any]:
        """Obtiene las citas de un paciente"""
        params = {}
        if estado:
            params["estado"] = estado
        return await self._make_request(
            "GET",
            f"/api/internal/pacientes/{paciente_id}/citas",
            params=params
        )
    
    async def get_citas_medico(
        self,
        medico_id: int,
        fecha: Optional[str] = None
    ) -> Dict[str, Any]:
        """Obtiene las citas de un médico"""
        params = {}
        if fecha:
            params["fecha"] = fecha
        return await self._make_request(
            "GET",
            f"/api/internal/medicos/{medico_id}/citas",
            params=params
        )
    
    async def get_disponibilidad_medico(
        self,
        medico_id: int,
        fecha: str
    ) -> Dict[str, Any]:
        """Obtiene la disponibilidad de un médico en una fecha"""
        return await self._make_request(
            "GET",
            f"/api/internal/medicos/{medico_id}/disponibilidad",
            params={"fecha": fecha}
        )
    
    # ========================================
    # Endpoints de Historial Clínico
    # ========================================
    
    async def get_historial_paciente(self, paciente_id: int) -> Dict[str, Any]:
        """Obtiene el historial clínico de un paciente"""
        return await self._make_request(
            "GET",
            f"/api/internal/pacientes/{paciente_id}/historial"
        )
    
    async def get_historial_resumen(self, paciente_id: int) -> Dict[str, Any]:
        """Obtiene un resumen del historial clínico"""
        return await self._make_request(
            "GET",
            f"/api/internal/pacientes/{paciente_id}/historial-resumen"
        )
    
    # ========================================
    # Endpoints de Médicos
    # ========================================
    
    async def get_medico(self, medico_id: int) -> Dict[str, Any]:
        """Obtiene información de un médico por ID"""
        return await self._make_request("GET", f"/api/internal/medicos/{medico_id}")
    
    async def get_medicos(
        self,
        especialidad: Optional[str] = None
    ) -> Dict[str, Any]:
        """Lista médicos con filtros opcionales"""
        params = {}
        if especialidad:
            params["especialidad"] = especialidad
        return await self._make_request("GET", "/api/internal/medicos", params=params)
    
    # ========================================
    # Endpoints de Tratamientos
    # ========================================
    
    async def get_tratamientos_paciente(self, paciente_id: int) -> Dict[str, Any]:
        """Obtiene los tratamientos de un paciente"""
        return await self._make_request(
            "GET",
            f"/api/internal/pacientes/{paciente_id}/tratamientos"
        )
    
    # ========================================
    # Agendamiento de Citas
    # ========================================
    
    async def determinar_tipo_usuario(self, id_usuario: int) -> Dict[str, Any]:
        """Determina si un usuario es paciente activo o externo"""
        return await self._make_request(
            "GET",
            f"/api/internal/agendamiento/tipo-usuario/{id_usuario}"
        )
    
    async def sugerir_horarios(
        self,
        id_medico: int,
        fecha_inicio: str,
        fecha_fin: Optional[str] = None,
        duracion_minutos: Optional[int] = 60,
        limite: Optional[int] = 3
    ) -> Dict[str, Any]:
        """Sugiere horarios disponibles para un médico"""
        return await self._make_request(
            "POST",
            "/api/internal/agendamiento/sugerir-horarios",
            data={
                "id_medico": id_medico,
                "fecha_inicio": fecha_inicio,
                "fecha_fin": fecha_fin,
                "duracion_minutos": duracion_minutos,
                "limite": limite
            }
        )
    
    async def registrar_cita(
        self,
        id_usuario: int,
        id_medico: int,
        fecha_hora_inicio: str,
        fecha_hora_fin: str,
        motivo: Optional[str] = None,
        tipo_cita: Optional[str] = None,
        notas: Optional[str] = None
    ) -> Dict[str, Any]:
        """Registra una nueva cita médica"""
        return await self._make_request(
            "POST",
            "/api/internal/agendamiento/registrar-cita",
            data={
                "id_usuario": id_usuario,
                "id_medico": id_medico,
                "fecha_hora_inicio": fecha_hora_inicio,
                "fecha_hora_fin": fecha_hora_fin,
                "motivo": motivo,
                "tipo_cita": tipo_cita,
                "notas": notas
            }
        )
    
    async def confirmar_cita(self, id_cita: int) -> Dict[str, Any]:
        """Confirma una cita existente (cambia estado a confirmada)"""
        return await self._make_request(
            "PATCH",
            f"/api/internal/agendamiento/confirmar-cita/{id_cita}"
        )
    
    async def registrar_interaccion(
        self,
        id_usuario: int,
        tipo_intencion: Optional[str] = None,
        entrada_usuario: Optional[str] = None,
        respuesta_ia: Optional[str] = None,
        estado_resultado: Optional[str] = None,
        contexto: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Registra una interacción del usuario con la IA"""
        return await self._make_request(
            "POST",
            "/api/internal/interacciones",
            data={
                "id_usuario": id_usuario,
                "tipo_intencion": tipo_intencion,
                "entrada_usuario": entrada_usuario,
                "respuesta_ia": respuesta_ia,
                "estado_resultado": estado_resultado,
                "contexto": contexto
            }
        )
    
    # ========================================
    # Health Check
    # ========================================
    
    async def health_check(self) -> bool:
        """Verifica si el backend está disponible"""
        try:
            await self._make_request("GET", "/api/internal/health")
            return True
        except Exception:
            return False


# Instancia global del cliente
backend_client = BackendClient()
