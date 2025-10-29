"""
Herramientas de LangChain para el agente
Cada herramienta permite al agente interactuar con el backend
"""
from langchain.tools import BaseTool
from typing import Optional, Type
from pydantic import BaseModel, Field
from app.utils.http_client import backend_client
from app.core import logger


# ========================================
# Schemas de Entrada para Tools
# ========================================

class BuscarPacienteInput(BaseModel):
    """Input para buscar paciente"""
    dni: Optional[str] = Field(None, description="DNI del paciente a buscar")
    paciente_id: Optional[int] = Field(None, description="ID del paciente a buscar")
    nombre: Optional[str] = Field(None, description="Nombre del paciente a buscar")


class ConsultarCitasInput(BaseModel):
    """Input para consultar citas"""
    paciente_id: Optional[int] = Field(None, description="ID del paciente")
    medico_id: Optional[int] = Field(None, description="ID del médico")
    estado: Optional[str] = Field(None, description="Estado de la cita (pendiente, confirmada, etc.)")


class ConsultarHistorialInput(BaseModel):
    """Input para consultar historial clínico"""
    paciente_id: int = Field(..., description="ID del paciente")


class ConsultarDisponibilidadInput(BaseModel):
    """Input para consultar disponibilidad"""
    medico_id: int = Field(..., description="ID del médico")
    fecha: str = Field(..., description="Fecha en formato YYYY-MM-DD")


class ListarMedicosInput(BaseModel):
    """Input para listar médicos"""
    especialidad: Optional[str] = Field(None, description="Especialidad a filtrar")


# ========================================
# Herramientas (Tools)
# ========================================

class BuscarPacienteTool(BaseTool):
    """
    Herramienta para buscar información de pacientes
    """
    name: str = "buscar_paciente"
    description: str = """
    Busca información de un paciente en el sistema.
    Puedes buscar por DNI, ID de paciente, o nombre.
    Retorna datos básicos del paciente como nombre, edad, alergias, etc.
    Usa esta herramienta cuando el usuario pregunte por un paciente específico.
    """
    args_schema: Type[BaseModel] = BuscarPacienteInput
    
    def _run(
        self,
        dni: Optional[str] = None,
        paciente_id: Optional[int] = None,
        nombre: Optional[str] = None
    ) -> str:
        """Ejecuta la búsqueda de paciente (síncrono)"""
        import asyncio
        return asyncio.run(self._arun(dni, paciente_id, nombre))
    
    async def _arun(
        self,
        dni: Optional[str] = None,
        paciente_id: Optional[int] = None,
        nombre: Optional[str] = None
    ) -> str:
        """Ejecuta la búsqueda de paciente (asíncrono)"""
        try:
            logger.info(f"🔍 Buscando paciente - DNI: {dni}, ID: {paciente_id}, Nombre: {nombre}")
            
            if paciente_id:
                result = await backend_client.get_paciente(paciente_id)
            elif dni:
                result = await backend_client.buscar_paciente_por_dni(dni)
            elif nombre:
                result = await backend_client.get_pacientes(limit=5, search=nombre)
            else:
                return "❌ Debes proporcionar al menos un criterio de búsqueda (DNI, ID o nombre)"
            
            if result.get("success") and result.get("data"):
                paciente = result["data"]
                
                # Si es una lista, tomar el primero
                if isinstance(paciente, list):
                    if len(paciente) == 0:
                        return "❌ No se encontró ningún paciente con ese criterio"
                    paciente = paciente[0]
                
                # Formatear respuesta
                info = f"""
✅ Paciente encontrado:
- Nombre: {paciente.get('nombres', '')} {paciente.get('apellidos', '')}
- DNI: {paciente.get('dni', 'No registrado')}
- Edad: {paciente.get('edad', 'No disponible')} años
- Teléfono: {paciente.get('telefono', 'No registrado')}
- Alergias: {paciente.get('alergias', 'Ninguna registrada')}
- Grupo sanguíneo: {paciente.get('grupo_sanguineo', 'No registrado')}
                """
                return info.strip()
            else:
                return "❌ No se encontró el paciente solicitado"
                
        except Exception as e:
            logger.error(f"Error en buscar_paciente: {str(e)}")
            return f"❌ Error al buscar paciente: {str(e)}"


class ConsultarCitasTool(BaseTool):
    """
    Herramienta para consultar citas médicas
    """
    name: str = "consultar_citas"
    description: str = """
    Consulta las citas médicas programadas.
    Puedes filtrar por paciente, médico y estado de la cita.
    Útil cuando el usuario pregunta por sus citas o las citas de un paciente.
    """
    args_schema: Type[BaseModel] = ConsultarCitasInput
    
    def _run(
        self,
        paciente_id: Optional[int] = None,
        medico_id: Optional[int] = None,
        estado: Optional[str] = None
    ) -> str:
        """Ejecuta la consulta de citas (síncrono)"""
        import asyncio
        return asyncio.run(self._arun(paciente_id, medico_id, estado))
    
    async def _arun(
        self,
        paciente_id: Optional[int] = None,
        medico_id: Optional[int] = None,
        estado: Optional[str] = None
    ) -> str:
        """Ejecuta la consulta de citas (asíncrono)"""
        try:
            logger.info(f"📅 Consultando citas - Paciente: {paciente_id}, Médico: {medico_id}, Estado: {estado}")
            
            if paciente_id:
                result = await backend_client.get_citas_paciente(paciente_id, estado)
            elif medico_id:
                result = await backend_client.get_citas_medico(medico_id)
            else:
                return "❌ Debes proporcionar al menos un ID de paciente o médico"
            
            if result.get("success") and result.get("data"):
                citas = result["data"]
                
                if not citas or len(citas) == 0:
                    return "ℹ️ No hay citas registradas con esos criterios"
                
                # Formatear respuesta
                info = f"✅ Se encontraron {len(citas)} citas:\n\n"
                for i, cita in enumerate(citas[:5], 1):  # Máximo 5 citas
                    info += f"""
{i}. Cita #{cita.get('id_cita')}
   - Fecha: {cita.get('fecha_hora_inicio', 'No disponible')}
   - Médico: Dr(a). {cita.get('medico', {}).get('nombres', '')} {cita.get('medico', {}).get('apellidos', '')}
   - Motivo: {cita.get('motivo', 'No especificado')}
   - Estado: {cita.get('estado', 'pendiente').upper()}
                    """
                
                if len(citas) > 5:
                    info += f"\n... y {len(citas) - 5} citas más"
                
                return info.strip()
            else:
                return "ℹ️ No se encontraron citas"
                
        except Exception as e:
            logger.error(f"Error en consultar_citas: {str(e)}")
            return f"❌ Error al consultar citas: {str(e)}"


class ConsultarHistorialTool(BaseTool):
    """
    Herramienta para consultar el historial clínico
    """
    name: str = "consultar_historial_clinico"
    description: str = """
    Consulta el historial clínico completo de un paciente.
    Incluye diagnósticos, tratamientos realizados, y observaciones médicas.
    Usa esta herramienta cuando necesites información médica histórica del paciente.
    """
    args_schema: Type[BaseModel] = ConsultarHistorialInput
    
    def _run(self, paciente_id: int) -> str:
        """Ejecuta la consulta de historial (síncrono)"""
        import asyncio
        return asyncio.run(self._arun(paciente_id))
    
    async def _arun(self, paciente_id: int) -> str:
        """Ejecuta la consulta de historial (asíncrono)"""
        try:
            logger.info(f"📋 Consultando historial del paciente {paciente_id}")
            
            result = await backend_client.get_historial_resumen(paciente_id)
            
            if result.get("success") and result.get("data"):
                historial = result["data"]
                
                info = f"""
✅ Resumen del Historial Clínico:
- Total de consultas: {historial.get('total_consultas', 0)}
- Última consulta: {historial.get('ultima_consulta', 'No disponible')}
- Tratamientos activos: {historial.get('tratamientos_activos', 0)}
- Alergias conocidas: {historial.get('alergias', 'Ninguna')}

Diagnósticos recientes:
{historial.get('diagnosticos_recientes', 'No hay diagnósticos recientes')}

Notas importantes:
{historial.get('notas_importantes', 'Sin notas especiales')}
                """
                return info.strip()
            else:
                return "ℹ️ No hay historial clínico registrado para este paciente"
                
        except Exception as e:
            logger.error(f"Error en consultar_historial: {str(e)}")
            return f"❌ Error al consultar historial: {str(e)}"


class ConsultarDisponibilidadTool(BaseTool):
    """
    Herramienta para consultar disponibilidad de médicos
    """
    name: str = "consultar_disponibilidad_medico"
    description: str = """
    Consulta la disponibilidad de un médico en una fecha específica.
    Muestra los horarios disponibles para agendar citas.
    Útil cuando el usuario quiere agendar una cita.
    """
    args_schema: Type[BaseModel] = ConsultarDisponibilidadInput
    
    def _run(self, medico_id: int, fecha: str) -> str:
        """Ejecuta la consulta de disponibilidad (síncrono)"""
        import asyncio
        return asyncio.run(self._arun(medico_id, fecha))
    
    async def _arun(self, medico_id: int, fecha: str) -> str:
        """Ejecuta la consulta de disponibilidad (asíncrono)"""
        try:
            logger.info(f"🗓️ Consultando disponibilidad del médico {medico_id} para {fecha}")
            
            result = await backend_client.get_disponibilidad_medico(medico_id, fecha)
            
            if result.get("success") and result.get("data"):
                disponibilidad = result["data"]
                
                horarios = disponibilidad.get("horarios_disponibles", [])
                if not horarios:
                    return f"ℹ️ No hay horarios disponibles para el {fecha}"
                
                info = f"✅ Horarios disponibles para el {fecha}:\n\n"
                for horario in horarios:
                    info += f"- {horario}\n"
                
                return info.strip()
            else:
                return f"ℹ️ No hay disponibilidad para el {fecha}"
                
        except Exception as e:
            logger.error(f"Error en consultar_disponibilidad: {str(e)}")
            return f"❌ Error al consultar disponibilidad: {str(e)}"


class ListarMedicosTool(BaseTool):
    """
    Herramienta para listar médicos disponibles
    """
    name: str = "listar_medicos"
    description: str = """
    Lista todos los médicos disponibles en el consultorio.
    Puedes filtrar por especialidad si es necesario.
    Útil cuando el usuario pregunta qué médicos hay disponibles.
    """
    args_schema: Type[BaseModel] = ListarMedicosInput
    
    def _run(self, especialidad: Optional[str] = None) -> str:
        """Ejecuta el listado de médicos (síncrono)"""
        import asyncio
        return asyncio.run(self._arun(especialidad))
    
    async def _arun(self, especialidad: Optional[str] = None) -> str:
        """Ejecuta el listado de médicos (asíncrono)"""
        try:
            logger.info(f"👨‍⚕️ Listando médicos - Especialidad: {especialidad}")
            
            result = await backend_client.get_medicos(especialidad)
            
            if result.get("success") and result.get("data"):
                medicos = result["data"]
                
                if not medicos or len(medicos) == 0:
                    return "ℹ️ No hay médicos registrados"
                
                info = f"✅ Médicos disponibles ({len(medicos)}):\n\n"
                for i, medico in enumerate(medicos, 1):
                    info += f"""
{i}. Dr(a). {medico.get('nombres', '')} {medico.get('apellidos', '')}
   - Especialidad: {medico.get('especialidad', 'General')}
   - Colegiatura: {medico.get('colegiatura', 'No disponible')}
                    """
                
                return info.strip()
            else:
                return "ℹ️ No se encontraron médicos"
                
        except Exception as e:
            logger.error(f"Error en listar_medicos: {str(e)}")
            return f"❌ Error al listar médicos: {str(e)}"


# ========================================
# HERRAMIENTAS DE AGENDAMIENTO DE CITAS
# ========================================

class DeterminarTipoUsuarioInput(BaseModel):
    """Input para determinar tipo de usuario"""
    id_usuario: int = Field(..., description="ID del usuario a verificar")


class DeterminarTipoUsuarioTool(BaseTool):
    """
    Determina si un usuario es paciente activo o usuario externo (primera vez)
    """
    name: str = "determinar_tipo_usuario"
    description: str = """
    Determina si el usuario es paciente activo con historial o usuario externo (primera vez).
    USAR AL INICIO del flujo de agendamiento para decidir:
    - Paciente activo: asignar último médico o especialista según motivo
    - Usuario externo: asignar médico de cabecera (primera cita)
    
    Retorna si es paciente activo, su último médico (si existe) y datos relevantes.
    """
    args_schema: Type[BaseModel] = DeterminarTipoUsuarioInput
    
    def _run(self, id_usuario: int) -> str:
        """Ejecuta de forma síncrona"""
        import asyncio
        return asyncio.run(self._arun(id_usuario))
    
    async def _arun(self, id_usuario: int) -> str:
        """Ejecuta de forma asíncrona"""
        try:
            logger.info(f"🔍 Determinando tipo de usuario: {id_usuario}")
            result = await backend_client.determinar_tipo_usuario(id_usuario)
            
            if result.get("success") and result.get("data"):
                data = result["data"]
                
                if data["es_paciente_activo"]:
                    msg = f"✅ Usuario es PACIENTE ACTIVO: {data['nombre_completo']}"
                    if data.get("ultimo_medico"):
                        medico = data["ultimo_medico"]
                        msg += f"\n👨‍⚕️ Último médico: Dr. {medico['nombres']} {medico['apellidos']} ({medico['especialidad']})"
                    return msg
                else:
                    return f"🆕 Usuario es EXTERNO (primera vez): {data['nombre_completo']}\n💡 Debe asignarse médico de cabecera"
            else:
                return f"❌ {result.get('message', 'Error al determinar tipo de usuario')}"
                
        except Exception as e:
            logger.error(f"Error en determinar_tipo_usuario: {str(e)}")
            return f"❌ Error: {str(e)}"


class SugerirHorariosInput(BaseModel):
    """Input para sugerir horarios"""
    id_medico: int = Field(..., description="ID del médico")
    fecha_inicio: str = Field(..., description="Fecha de inicio en formato YYYY-MM-DD")
    fecha_fin: Optional[str] = Field(None, description="Fecha fin (opcional, por defecto +7 días)")
    duracion_minutos: Optional[int] = Field(60, description="Duración de la cita en minutos")
    limite: Optional[int] = Field(3, description="Cantidad de horarios a sugerir")


class SugerirHorariosTool(BaseTool):
    """
    Sugiere horarios disponibles cuando el solicitado no está libre
    """
    name: str = "sugerir_horarios_alternativos"
    description: str = """
    Sugiere horarios ALTERNATIVOS disponibles cuando el horario solicitado NO está libre.
    Busca los próximos horarios disponibles del médico en un rango de fechas.
    
    USAR cuando:
    - El horario solicitado por el usuario está ocupado
    - El usuario pregunta "¿qué horarios hay disponibles?"
    
    Retorna lista de horarios con fecha, hora y día de la semana.
    """
    args_schema: Type[BaseModel] = SugerirHorariosInput
    
    def _run(self, **kwargs) -> str:
        """Ejecuta de forma síncrona"""
        import asyncio
        return asyncio.run(self._arun(**kwargs))
    
    async def _arun(
        self,
        id_medico: int,
        fecha_inicio: str,
        fecha_fin: Optional[str] = None,
        duracion_minutos: Optional[int] = 60,
        limite: Optional[int] = 3
    ) -> str:
        """Ejecuta de forma asíncrona"""
        try:
            logger.info(f"📅 Sugiriendo horarios - Médico: {id_medico}, Fecha inicio: {fecha_inicio}")
            result = await backend_client.sugerir_horarios(
                id_medico=id_medico,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                duracion_minutos=duracion_minutos,
                limite=limite
            )
            
            if result.get("success") and result.get("data"):
                horarios = result["data"]
                
                if len(horarios) == 0:
                    return "❌ No hay horarios disponibles en el rango de fechas especificado"
                
                msg = f"📅 Horarios disponibles encontrados ({len(horarios)}):\n\n"
                for i, h in enumerate(horarios, 1):
                    msg += f"{i}. {h['dia_semana']} {h['fecha']} a las {h['hora']}\n"
                
                msg += "\n💡 El usuario puede elegir uno de estos horarios"
                return msg
            else:
                return f"❌ {result.get('message', 'Error al sugerir horarios')}"
                
        except Exception as e:
            logger.error(f"Error en sugerir_horarios: {str(e)}")
            return f"❌ Error: {str(e)}"


class RegistrarCitaInput(BaseModel):
    """Input para registrar cita"""
    id_usuario: int = Field(..., description="ID del usuario que agenda")
    id_medico: int = Field(..., description="ID del médico")
    fecha_hora_inicio: str = Field(..., description="Fecha y hora inicio YYYY-MM-DD HH:MM:SS")
    fecha_hora_fin: str = Field(..., description="Fecha y hora fin YYYY-MM-DD HH:MM:SS")
    motivo: Optional[str] = Field(None, description="Motivo de la consulta")
    tipo_cita: Optional[str] = Field(None, description="Tipo: primera_vez, seguimiento, especialidad")
    notas: Optional[str] = Field(None, description="Notas adicionales")


class RegistrarCitaTool(BaseTool):
    """
    Registra una nueva cita médica en el sistema
    """
    name: str = "registrar_cita"
    description: str = """
    Registra una NUEVA CITA médica con estado 'pendiente'.
    
    ⚠️ IMPORTANTE: 
    - Usar SOLO DESPUÉS de verificar disponibilidad del médico
    - La cita queda en estado PENDIENTE (no confirmada)
    
    Parámetros necesarios:
    - id_usuario: ID del usuario que agenda
    - id_medico: ID del médico asignado
    - fecha_hora_inicio: Inicio en formato "YYYY-MM-DD HH:MM:SS"
    - fecha_hora_fin: Fin en formato "YYYY-MM-DD HH:MM:SS"
    - motivo: Motivo de la consulta (opcional)
    
    Retorna confirmación con ID de cita generado.
    """
    args_schema: Type[BaseModel] = RegistrarCitaInput
    
    def _run(self, **kwargs) -> str:
        """Ejecuta de forma síncrona"""
        import asyncio
        return asyncio.run(self._arun(**kwargs))
    
    async def _arun(
        self,
        id_usuario: int,
        id_medico: int,
        fecha_hora_inicio: str,
        fecha_hora_fin: str,
        motivo: Optional[str] = None,
        tipo_cita: Optional[str] = None,
        notas: Optional[str] = None
    ) -> str:
        """Ejecuta de forma asíncrona"""
        try:
            logger.info(f"📝 Registrando cita - Usuario: {id_usuario}, Médico: {id_medico}, Fecha: {fecha_hora_inicio}")
            result = await backend_client.registrar_cita(
                id_usuario=id_usuario,
                id_medico=id_medico,
                fecha_hora_inicio=fecha_hora_inicio,
                fecha_hora_fin=fecha_hora_fin,
                motivo=motivo,
                tipo_cita=tipo_cita,
                notas=notas
            )
            
            if result.get("success") and result.get("data"):
                data = result["data"]
                return f"""✅ Cita registrada exitosamente:

📋 ID Cita: {data['id_cita']}
📅 Fecha/Hora: {data['fecha_hora_inicio']}
⏳ Estado: {data['estado'].upper()} (pendiente de confirmación)
📝 Motivo: {data['motivo']}

💡 La cita está en estado PENDIENTE. El usuario debe confirmarla más adelante."""
            else:
                return f"❌ {result.get('message', 'Error al registrar cita')}"
                
        except Exception as e:
            logger.error(f"Error en registrar_cita: {str(e)}")
            return f"❌ Error: {str(e)}"


class ConfirmarCitaInput(BaseModel):
    """Input para confirmar cita"""
    id_cita: int = Field(..., description="ID de la cita a confirmar")


class ConfirmarCitaTool(BaseTool):
    """
    Confirma una cita existente (cambia estado a confirmada)
    """
    name: str = "confirmar_cita"
    description: str = """
    Confirma una cita que está en estado 'pendiente', cambiándola a 'confirmada'.
    
    USAR cuando:
    - El usuario dice explícitamente "confirmo mi cita"
    - El usuario pregunta "¿cómo confirmo mi cita?"
    
    ⚠️ Solo se pueden confirmar citas en estado PENDIENTE.
    
    Retorna confirmación del cambio de estado exitoso.
    """
    args_schema: Type[BaseModel] = ConfirmarCitaInput
    
    def _run(self, id_cita: int) -> str:
        """Ejecuta de forma síncrona"""
        import asyncio
        return asyncio.run(self._arun(id_cita))
    
    async def _arun(self, id_cita: int) -> str:
        """Ejecuta de forma asíncrona"""
        try:
            logger.info(f"✅ Confirmando cita: {id_cita}")
            result = await backend_client.confirmar_cita(id_cita)
            
            if result.get("success") and result.get("data"):
                data = result["data"]
                return f"""✅ Cita confirmada exitosamente:

📋 ID Cita: {data['id_cita']}
✅ Estado: {data['estado'].upper()}
📅 Fecha/Hora: {data['fecha_hora_inicio']}

🔔 Recibirás un recordatorio antes de tu cita."""
            else:
                return f"❌ {result.get('message', 'Error al confirmar cita')}"
                
        except Exception as e:
            logger.error(f"Error en confirmar_cita: {str(e)}")
            return f"❌ Error: {str(e)}"


class RegistrarInteraccionInput(BaseModel):
    """Input para registrar interacción IA"""
    id_usuario: int = Field(..., description="ID del usuario")
    tipo_intencion: Optional[str] = Field(None, description="Tipo de intención detectada")
    entrada_usuario: Optional[str] = Field(None, description="Mensaje del usuario")
    respuesta_ia: Optional[str] = Field(None, description="Respuesta del agente")
    estado_resultado: Optional[str] = Field(None, description="exitosa, fallida, requiere_revision")
    contexto: Optional[dict] = Field(None, description="Contexto adicional JSON")


class RegistrarInteraccionTool(BaseTool):
    """
    Registra interacciones para trazabilidad y análisis
    """
    name: str = "registrar_interaccion_ia"
    description: str = """
    Registra la interacción del usuario con la IA para trazabilidad.
    
    USAR para:
    - Guardar registro de intenciones importantes (agendar_cita, cancelar_cita, etc.)
    - Análisis posterior de conversaciones
    - Auditoría del sistema
    
    Es opcional, usar solo en interacciones clave.
    """
    args_schema: Type[BaseModel] = RegistrarInteraccionInput
    
    def _run(self, **kwargs) -> str:
        """Ejecuta de forma síncrona"""
        import asyncio
        return asyncio.run(self._arun(**kwargs))
    
    async def _arun(
        self,
        id_usuario: int,
        tipo_intencion: Optional[str] = None,
        entrada_usuario: Optional[str] = None,
        respuesta_ia: Optional[str] = None,
        estado_resultado: Optional[str] = None,
        contexto: Optional[dict] = None
    ) -> str:
        """Ejecuta de forma asíncrona"""
        try:
            logger.info(f"📊 Registrando interacción - Usuario: {id_usuario}, Intención: {tipo_intencion}")
            result = await backend_client.registrar_interaccion(
                id_usuario=id_usuario,
                tipo_intencion=tipo_intencion,
                entrada_usuario=entrada_usuario,
                respuesta_ia=respuesta_ia,
                estado_resultado=estado_resultado,
                contexto=contexto
            )
            
            if result.get("success"):
                return f"✅ Interacción registrada (ID: {result['data']['id_interaccion']})"
            else:
                return f"⚠️ {result.get('message', 'Error al registrar interacción')}"
                
        except Exception as e:
            logger.error(f"Error en registrar_interaccion: {str(e)}")
            return f"⚠️ Error: {str(e)}"


class ValidarMedicoInput(BaseModel):
    """Input para validar médico"""
    id_medico: int = Field(..., description="ID del médico a validar")


class ValidarMedicoTool(BaseTool):
    """
    Valida que un médico existe y está disponible
    """
    name: str = "validar_medico"
    description: str = """
    Valida que un médico existe y está disponible en el sistema.
    
    USAR cuando:
    - Necesites verificar que un ID de médico es válido antes de usarlo
    - El último médico del paciente podría no estar disponible
    - Antes de registrar una cita para confirmar que el médico existe
    
    Retorna información del médico si es válido, o error si no existe.
    """
    args_schema: Type[BaseModel] = ValidarMedicoInput
    
    def _run(self, id_medico: int) -> str:
        """Ejecuta de forma síncrona"""
        import asyncio
        return asyncio.run(self._arun(id_medico))
    
    async def _arun(self, id_medico: int) -> str:
        """Ejecuta de forma asíncrona"""
        try:
            logger.info(f"🔍 Validando médico: {id_medico}")
            result = await backend_client.get_medico(id_medico)
            
            if result.get("success") and result.get("data"):
                medico = result["data"]
                return f"""✅ Médico válido:
- ID: {medico.get('id_medico')}
- Nombre: Dr(a). {medico.get('nombres', '')} {medico.get('apellidos', '')}
- Especialidad: {medico.get('especialidad', 'General')}
- Colegiatura: {medico.get('colegiatura', 'No disponible')}

Este médico puede ser usado para agendar citas."""
            else:
                return f"❌ Médico con ID {id_medico} no existe o no está disponible. Usa listar_medicos para ver médicos válidos."
                
        except Exception as e:
            logger.error(f"Error en validar_medico: {str(e)}")
            return f"❌ Error al validar médico: {str(e)}"


# ========================================
# Lista de todas las herramientas
# ========================================

def get_all_tools():
    """
    Retorna todas las herramientas disponibles para el agente
    """
    return [
        # Herramientas de consulta
        BuscarPacienteTool(),
        ConsultarCitasTool(),
        ConsultarHistorialTool(),
        ConsultarDisponibilidadTool(),
        ListarMedicosTool(),
        ValidarMedicoTool(),
        
        # Herramientas de agendamiento
        DeterminarTipoUsuarioTool(),
        SugerirHorariosTool(),
        RegistrarCitaTool(),
        ConfirmarCitaTool(),
        RegistrarInteraccionTool(),
    ]
