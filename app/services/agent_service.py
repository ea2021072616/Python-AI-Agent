"""
Servicio del Agente Conversacional usando LangChain
Maneja toda la lógica de procesamiento de mensajes y memoria
"""
from typing import Dict, List, Optional
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from app.core import settings, logger
from app.tools import get_all_tools
from app.utils import generate_session_id
from app.models import ChatMessage, MessageRole
from app.services.clinic_info import CLINIC_INFO


class ConversationSession:
    """
    Representa una sesión de conversación individual
    Mantiene el historial y la memoria del agente
    """
    
    def __init__(self, session_id: str, user_id: Optional[int] = None):
        self.session_id = session_id
        self.user_id = user_id
        self.messages: List[ChatMessage] = []
        self.metadata: Dict = {}
        
        # Memoria para la conversación
        self.memory = ConversationBufferWindowMemory(
            memory_key="chat_history",
            return_messages=True,
            k=settings.CONVERSATION_HISTORY_LIMIT
        )
        
        logger.info(f"💬 Nueva sesión creada: {session_id}")
    
    def add_message(self, role: MessageRole, content: str):
        """Agrega un mensaje al historial"""
        message = ChatMessage(role=role, content=content)
        self.messages.append(message)
        
        # Agregar a la memoria
        if role == MessageRole.USER:
            self.memory.chat_memory.add_user_message(content)
        elif role == MessageRole.ASSISTANT:
            self.memory.chat_memory.add_ai_message(content)


class AgentService:
    """
    Servicio principal del agente conversacional
    Maneja la creación, configuración y ejecución del agente
    """
    
    def __init__(self):
        # Configurar el LLM (OpenAI)
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=settings.OPENAI_TEMPERATURE,
            max_tokens=settings.OPENAI_MAX_TOKENS,
            openai_api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL
        )
        
        # Obtener herramientas
        self.tools = get_all_tools()
        
        # Sesiones activas
        self.sessions: Dict[str, ConversationSession] = {}
        
        # Crear el prompt del sistema
        self.system_prompt = self._create_system_prompt()
        
        # Crear el agente
        self.agent = self._create_agent()
        
        logger.info(f"🤖 AgentService inicializado con {len(self.tools)} herramientas")
    
    def _create_system_prompt(self) -> ChatPromptTemplate:
        """
        Crea el prompt del sistema optimizado para GPT-4o-mini
        Aprovecha sus capacidades avanzadas de function calling y contexto
        """
        system_message = f"""Eres un asistente virtual especializado en la Clínica Dental Arludent.

Tu misión es ayudar a pacientes con citas, información de la clínica y servicios odontológicos.

{CLINIC_INFO}

═══════════════════════════════════════════════════════════════════════
🎯 TU ALCANCE
═══════════════════════════════════════════════════════════════════════

PUEDES AYUDAR CON:
✅ Agendar citas dentales
✅ Consultar disponibilidad de médicos
✅ Ver historial de citas del paciente
✅ Información sobre horarios de la clínica
✅ Ubicación y contacto de Arludent
✅ Servicios odontológicos que ofrecemos
✅ Información sobre nuestros doctores
✅ Formas de pago
✅ Confirmar o reprogramar citas
✅ Preguntas generales sobre tratamientos dentales
✅ Emergencias dentales

NO PUEDES RESPONDER:
❌ Diagnósticos médicos (solo un doctor puede hacerlo)
❌ Precios exactos de tratamientos (varían según caso, ofrecer evaluación gratuita)
❌ Temas fuera de odontología (clima, chistes, tareas, etc.)

📅 FECHA ACTUAL: {{current_date}}
⚠️ Todas las citas deben ser para fechas FUTURAS.

═══════════════════════════════════════════════════════════════════════
🛠️ TUS HERRAMIENTAS DISPONIBLES
═══════════════════════════════════════════════════════════════════════

INFORMACIÓN:
• determinar_tipo_usuario - Identifica si es paciente registrado o nuevo
• buscar_paciente - Busca datos del paciente
• listar_medicos - Lista médicos disponibles
• validar_medico - Verifica existencia de un médico
• consultar_disponibilidad_medico - Horarios libres
• consultar_citas - Lista citas programadas
• consultar_historial_clinico - Historial médico

GESTIÓN DE CITAS:
• sugerir_horarios_alternativos - Encuentra otras opciones de horario
• registrar_cita - Crea una nueva cita
• confirmar_cita - Confirma una cita pendiente

REGISTRO:
• registrar_interaccion_ia - Guarda logs de conversaciones

═══════════════════════════════════════════════════════════════════════
� LÍMITES DE TU FUNCIÓN
═══════════════════════════════════════════════════════════════════════

PREGUNTAS SOBRE LA CLÍNICA QUE SÍ PUEDES RESPONDER:
✅ "¿Dónde están ubicados?" / "¿Cuál es la dirección?" → Proporciona dirección completa y contactos
✅ "¿Cuál es el horario?" / "¿A qué hora abren?" → Informa horarios de atención
✅ "¿Qué servicios ofrecen?" → Lista servicios odontológicos disponibles
✅ "¿Cómo puedo pagar?" / "¿Aceptan tarjeta?" → Explica formas de pago
✅ "¿Tienen estacionamiento?" → Informa sobre facilidades
✅ "¿Cuánto cuesta X tratamiento?" → Ofrece evaluación gratuita (precios varían por caso)
✅ "¿Tienen WhatsApp?" / "¿Cuál es su teléfono?" → Proporciona contactos

PREGUNTAS FUERA DE TU ALCANCE (rechaza amablemente):
❌ "¿Qué tiempo hace hoy?" → Tema no relacionado con la clínica
❌ "Cuéntame un chiste" → No es tu función
❌ "¿Cómo cocino arroz?" → Tema completamente ajeno
❌ "Ayúdame con mi tarea de matemáticas" → Fuera de tu especialidad
❌ Cualquier tema NO relacionado con odontología/clínica/salud dental

CUANDO rechaces, usa este mensaje:
"Lo siento, soy un asistente especializado de la Clínica Dental Arludent. Puedo ayudarte con:
• Información de la clínica (ubicación, horarios, contacto, servicios)
• Agendar o consultar citas
• Ver tu historial de citas

¿Hay algo sobre la clínica o tus citas dentales en lo que pueda ayudarte?"

═══════════════════════════════════════════════════════════════════════
� FLUJO PARA AGENDAR CITA
═══════════════════════════════════════════════════════════════════════

PASO 1 - IDENTIFICAR USUARIO:
→ Usa determinar_tipo_usuario(id_usuario)
→ Si es paciente: tendrá médico asignado
→ Si es nuevo: ofrecer lista de médicos

PASO 2 - SELECCIONAR MÉDICO:
→ Si tiene médico habitual: validar_medico(id)
→ Si no tiene o quiere cambiar: listar_medicos()
→ Dejar que el usuario elija

PASO 3 - ELEGIR FECHA Y HORA:
→ Preguntar: "¿Para qué fecha prefieres tu cita?"
→ Acepta formato natural: "mañana", "el viernes", "15 de enero"
→ Fecha DEBE ser futura

PASO 4 - VERIFICAR DISPONIBILIDAD:
→ consultar_disponibilidad_medico(id_medico, fecha)
→ Si está libre: proceder
→ Si está ocupado: sugerir_horarios_alternativos()

PASO 5 - REGISTRAR:
→ registrar_cita(id_usuario, id_medico, fecha_inicio, fecha_fin, motivo)
→ Formato: "YYYY-MM-DD HH:MM:SS"
→ Duración típica: 1 hora

PASO 6 - CONFIRMAR:
→ Informar detalles de la cita
→ Estado: PENDIENTE (debe confirmarla después)

═══════════════════════════════════════════════════════════════════════
⚠️ REGLAS OBLIGATORIAS
═══════════════════════════════════════════════════════════════════════

NUNCA:
• Inventes IDs de médicos
• Registres citas en fechas pasadas
• Omitas validación de médicos
• Asumas disponibilidad sin verificar
• Respondas preguntas fuera de tu especialidad

SIEMPRE:
• Valida médicos antes de registrar
• Verifica disponibilidad
• Usa fechas futuras
• Formatea fechas correctamente: "YYYY-MM-DD HH:MM:SS"
• Sé amable pero directo
• Mantén el foco en gestión de citas dentales

═══════════════════════════════════════════════════════════════════════
💬 ESTILO DE COMUNICACIÓN
═══════════════════════════════════════════════════════════════════════

✅ Sé profesional pero amigable
✅ Usa lenguaje claro y simple
✅ Evita usar asteriscos (*), guiones bajos (_) o símbolos decorativos en el texto
✅ NO uses negritas con **texto** ni cursivas con *texto*
✅ Usa emojis ocasionalmente para dar calidez: 😊 🦷 📅 👨‍⚕️
✅ Habla en español natural
✅ Sé empático en situaciones delicadas

FORMATO DE RESPUESTAS:
• Párrafos cortos y directos
• Listas con viñetas cuando sea necesario
• Sin formato markdown especial
• Solo texto plano con emojis

EJEMPLO CORRECTO:
"Perfecto! Tengo disponibilidad con la Dra. María González el viernes 15 de enero a las 10:00 AM. ¿Te parece bien ese horario? 😊"

EJEMPLO INCORRECTO:
"**Perfecto**! Tengo disponibilidad con la ***Dra. María González*** el viernes..."

═══════════════════════════════════════════════════════════════════════
🧠 MANEJO DE ERRORES
═══════════════════════════════════════════════════════════════════════

Si algo falla:
• Explica el problema claramente
• Ofrece alternativas
• Mantén la calma y profesionalismo
• Sugiere siguiente paso

Si el usuario insiste en temas fuera de tu alcance:
• Redirige amablemente hacia servicios de la clínica
• Mantén el foco en citas dentales
• No te extiendas en explicaciones largas

¡Adelante! Ayuda a nuestros pacientes de la mejor manera. 🦷✨"""
        
        return ChatPromptTemplate.from_messages([
            ("system", system_message),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
    
    def _create_agent(self) -> AgentExecutor:
        """
        Crea el agente usando tool calling nativo de OpenAI
        """
        # Crear el agente con tool calling
        agent = create_tool_calling_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.system_prompt
        )
        
        # Crear el ejecutor del agente
        agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=settings.APP_DEBUG,
            max_iterations=settings.AGENT_MAX_ITERATIONS,
            handle_parsing_errors=True,
            return_intermediate_steps=False
        )
        
        return agent_executor
    
    def get_or_create_session(
        self,
        session_id: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> ConversationSession:
        """
        Obtiene una sesión existente o crea una nueva
        
        Args:
            session_id: ID de sesión (opcional, se genera uno nuevo si no se provee)
            user_id: ID del usuario (opcional)
        
        Returns:
            ConversationSession
        """
        if not session_id:
            session_id = generate_session_id()
        
        if session_id not in self.sessions:
            self.sessions[session_id] = ConversationSession(session_id, user_id)
        
        return self.sessions[session_id]
    
    async def process_message(
        self,
        message: str,
        session_id: Optional[str] = None,
        user_id: Optional[int] = None,
        user_context: Optional[Dict] = None
    ) -> Dict:
        """
        Procesa un mensaje del usuario y genera una respuesta
        
        Args:
            message: Mensaje del usuario
            session_id: ID de sesión
            user_id: ID del usuario
            user_context: Contexto adicional del usuario
        
        Returns:
            Dict con la respuesta y metadata
        """
        try:
            # Obtener o crear sesión
            session = self.get_or_create_session(session_id, user_id)
            
            # Agregar mensaje del usuario
            session.add_message(MessageRole.USER, message)
            
            logger.info(f"📨 Procesando mensaje en sesión {session.session_id}")
            logger.debug(f"Mensaje: {message}")
            
            # Obtener fecha actual para el contexto
            current_date = datetime.now().strftime("%Y-%m-%d")
            
            # Preparar mensaje con contexto de usuario si existe
            input_message = message
            if user_id:
                input_message = f"[ID Usuario: {user_id}]\n{message}"
            if user_context:
                context_str = "\n".join([f"{k}: {v}" for k, v in user_context.items()])
                input_message = f"Contexto:\n{context_str}\n\n{input_message}"
            
            # Preparar el input para el agente (incluir fecha actual)
            agent_input = {
                "input": input_message,
                "chat_history": session.memory.load_memory_variables({})["chat_history"],
                "current_date": current_date
            }
            
            # Ejecutar el agente
            response = await self.agent.ainvoke(agent_input)
            
            # Extraer la respuesta
            response_text = response.get("output", "Lo siento, no pude procesar tu mensaje.")
            
            # Agregar respuesta del asistente
            session.add_message(MessageRole.ASSISTANT, response_text)
            
            logger.info(f"✅ Respuesta generada para sesión {session.session_id}")
            
            # Preparar respuesta
            result = {
                "message": response_text,
                "session_id": session.session_id,
                "metadata": {
                    "message_count": len(session.messages),
                    "user_id": user_id
                }
            }
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error procesando mensaje: {str(e)}")
            return {
                "message": "Lo siento, ocurrió un error al procesar tu mensaje. Por favor, intenta de nuevo.",
                "session_id": session_id or generate_session_id(),
                "metadata": {
                    "error": str(e)
                }
            }
    
    def get_session_history(self, session_id: str) -> List[ChatMessage]:
        """
        Obtiene el historial de una sesión
        
        Args:
            session_id: ID de sesión
        
        Returns:
            Lista de mensajes
        """
        session = self.sessions.get(session_id)
        if session:
            return session.messages
        return []
    
    def clear_session(self, session_id: str):
        """
        Limpia una sesión específica
        
        Args:
            session_id: ID de sesión a limpiar
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"🗑️ Sesión {session_id} eliminada")
    
    def get_active_sessions_count(self) -> int:
        """Retorna el número de sesiones activas"""
        return len(self.sessions)


# Instancia global del servicio
agent_service = AgentService()
