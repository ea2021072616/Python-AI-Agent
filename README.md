# 🤖 Arludent AI Microservice

Microservicio de Agente Conversacional con Inteligencia Artificial para el sistema de gestión odontológica Arludent.

Este microservicio utiliza **LangChain** y **OpenAI** para proporcionar un asistente virtual inteligente que puede interactuar con el backend Laravel para consultar información de pacientes, citas, historiales clínicos y más.

---

## 📋 Tabla de Contenidos

- [Características](#características)
- [Arquitectura](#arquitectura)
- [Tecnologías](#tecnologías)
- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Configuración](#configuración)
- [Uso](#uso)
- [API Reference](#api-reference)
- [Herramientas del Agente](#herramientas-del-agente)
- [Integración con Backend](#integración-con-backend)
- [Integración con Frontend](#integración-con-frontend)
- [Despliegue](#despliegue)
- [Testing](#testing)

---

## ✨ Características

### 🤖 Agente Conversacional Inteligente
- ✅ Procesamiento de lenguaje natural con OpenAI GPT
- ✅ Memoria de conversación persistente por sesión
- ✅ Contexto de usuario para respuestas personalizadas
- ✅ Manejo de múltiples sesiones simultáneas

### 🛠️ Herramientas (Tools)
- 🔍 Búsqueda de pacientes por DNI, ID o nombre
- 📅 Consulta de citas médicas
- 📋 Acceso a historiales clínicos
- 🗓️ Consulta de disponibilidad de médicos
- 👨‍⚕️ Listado de médicos y especialidades

### 🔌 Integración
- 🔗 Comunicación directa con Backend Laravel
- 🌐 API REST para integración con Frontend Vue.js
- 🔐 Autenticación mediante API Key interna

### 🚀 Escalabilidad
- ⚡ Asíncrono (async/await)
- 📦 Arquitectura modular
- 🔧 Configuración por variables de entorno
- 📊 Logging estructurado

---

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (Vue.js)                        │
│                                                               │
│  - Chat Component                                             │
│  - User Interface                                             │
└────────────────────────────┬────────────────────────────────┘
                             │ HTTP REST
                             │
┌────────────────────────────▼────────────────────────────────┐
│              Arludent AI Microservice (Python)               │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │           API Layer (FastAPI)                        │    │
│  │  - /chat                                             │    │
│  │  - /health                                           │    │
│  │  - /sessions                                         │    │
│  └─────────────────────────┬───────────────────────────┘    │
│                             │                                 │
│  ┌─────────────────────────▼───────────────────────────┐    │
│  │        Agent Service (LangChain)                     │    │
│  │  - Conversation Memory                               │    │
│  │  - Agent Executor                                    │    │
│  │  - System Prompt                                     │    │
│  └─────────────────────────┬───────────────────────────┘    │
│                             │                                 │
│  ┌─────────────────────────▼───────────────────────────┐    │
│  │          Tools (LangChain Tools)                     │    │
│  │  - BuscarPacienteTool                               │    │
│  │  - ConsultarCitasTool                               │    │
│  │  - ConsultarHistorialTool                           │    │
│  │  - ConsultarDisponibilidadTool                      │    │
│  │  - ListarMedicosTool                                │    │
│  └─────────────────────────┬───────────────────────────┘    │
│                             │                                 │
│  ┌─────────────────────────▼───────────────────────────┐    │
│  │       Backend Client (HTTP Client)                   │    │
│  │  - Async HTTP Requests                               │    │
│  │  - Internal API Key Auth                             │    │
│  └─────────────────────────┬───────────────────────────┘    │
└────────────────────────────┼────────────────────────────────┘
                             │ HTTP (Internal)
                             │
┌────────────────────────────▼────────────────────────────────┐
│              Backend Laravel (PHP)                           │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │      Internal API Endpoints (Sin JWT)                │    │
│  │  - GET  /api/internal/pacientes/:id                 │    │
│  │  - GET  /api/internal/citas/:id                     │    │
│  │  - GET  /api/internal/historiales/:id               │    │
│  │  - GET  /api/internal/medicos                       │    │
│  └─────────────────────────┬───────────────────────────┘    │
│                             │                                 │
│  ┌─────────────────────────▼───────────────────────────┐    │
│  │            Database (MySQL)                          │    │
│  │  - pacientes                                         │    │
│  │  - citas                                             │    │
│  │  - historiales_clinico                              │    │
│  │  - medicos                                           │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘

       ┌───────────────────────────────────────┐
       │    OpenAI API (External)               │
       │    - GPT-4o-mini                       │
       └───────────────────────────────────────┘
```

### Flujo de Datos

1. **Usuario → Frontend:** El usuario escribe un mensaje en el chat
2. **Frontend → Microservicio:** POST /api/v1/chat con el mensaje
3. **Microservicio → LangChain:** El agente procesa el mensaje
4. **LangChain → OpenAI:** Consulta al LLM para entender la intención
5. **OpenAI → LangChain:** Respuesta con la acción a tomar
6. **LangChain → Tools:** Ejecuta las herramientas necesarias
7. **Tools → Backend Laravel:** Consulta datos mediante endpoints internos
8. **Backend → Database:** Consulta a la base de datos
9. **Database → Backend → Tools:** Retorna los datos
10. **Tools → LangChain → Microservicio:** Formatea la respuesta
11. **Microservicio → Frontend:** Retorna la respuesta al usuario

---

## 🛠️ Tecnologías

| Categoría | Tecnología | Versión |
|-----------|-----------|---------|
| **Framework** | FastAPI | 0.115.0 |
| **Servidor** | Uvicorn | 0.32.0 |
| **IA/LLM** | LangChain | 0.3.7 |
| **IA/LLM** | OpenAI | 1.54.4 |
| **HTTP Client** | HTTPX | 0.27.2 |
| **Validación** | Pydantic | 2.9.2 |
| **Logging** | Loguru | 0.7.2 |
| **Config** | Python-dotenv | 1.0.1 |

---

## 📦 Requisitos

- **Python:** >= 3.11
- **Pip:** >= 23.0
- **OpenAI API Key:** Necesaria para usar GPT
- **Backend Laravel:** Debe estar ejecutándose

---

## 🚀 Instalación

### 1. Clonar el repositorio

```powershell
# Ya está en tu proyecto
cd "c:\Users\erick\Downloads\ARLUDENT PROYECTO\Arludent\arludent-ai-microservice"
```

### 2. Crear entorno virtual

```powershell
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
.\venv\Scripts\Activate.ps1
```

### 3. Instalar dependencias

```powershell
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

```powershell
# Copiar el archivo de ejemplo
copy .env.example .env

# Editar .env con tus valores
notepad .env
```

**⚠️ IMPORTANTE:** Debes agregar tu **OPENAI_API_KEY** en el archivo `.env`

---

## ⚙️ Configuración

### Variables de Entorno Principales

```env
# OpenAI (REQUERIDO)
OPENAI_API_KEY=sk-proj-YOUR-KEY-HERE
OPENAI_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0.7

# Backend Laravel (REQUERIDO)
BACKEND_URL=http://127.0.0.1:8000
BACKEND_INTERNAL_API_KEY=arludent-internal-secret-2024

# Aplicación
APP_HOST=0.0.0.0
APP_PORT=8001
APP_ENV=development

# CORS (Frontend URL)
CORS_ORIGINS=http://localhost:5173
```

### Obtener OpenAI API Key

1. Ve a [platform.openai.com](https://platform.openai.com/)
2. Inicia sesión o crea una cuenta
3. Ve a **API Keys** en el menú
4. Click en **Create new secret key**
5. Copia la key y pégala en `.env`

---

## 🎮 Uso

### Iniciar el Microservicio

```powershell
# Asegúrate de estar en el entorno virtual
.\venv\Scripts\Activate.ps1

# Iniciar el servidor
python main.py
```

El servidor estará disponible en: **http://localhost:8001**

### Documentación Interactiva

- **Swagger UI:** http://localhost:8001/docs
- **ReDoc:** http://localhost:8001/redoc

### Health Check

```powershell
# Verificar que el servicio esté funcionando
curl http://localhost:8001/api/v1/health
```

---

## 📡 API Reference

### POST /api/v1/chat

Procesa un mensaje de chat y retorna la respuesta del agente.

**Request:**
```json
{
  "message": "¿Cuántas citas tengo programadas?",
  "session_id": "opcional-session-id",
  "user_id": 123,
  "user_context": {
    "nombre": "Juan Pérez",
    "rol": "paciente"
  }
}
```

**Response:**
```json
{
  "message": "Tienes 2 citas programadas para esta semana...",
  "session_id": "generated-session-id",
  "timestamp": "2024-01-15T10:30:00",
  "metadata": {
    "message_count": 5,
    "user_id": 123
  }
}
```

### GET /api/v1/health

Verifica el estado del servicio.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00",
  "version": "1.0.0",
  "services": {
    "backend": true,
    "openai": true,
    "agent": true
  },
  "details": {
    "active_sessions": 5,
    "environment": "development"
  }
}
```

### GET /api/v1/sessions/{session_id}/history

Obtiene el historial de una sesión.

**Response:**
```json
{
  "session_id": "abc-123",
  "message_count": 10,
  "messages": [
    {
      "role": "user",
      "content": "Hola",
      "timestamp": "2024-01-15T10:00:00"
    },
    {
      "role": "assistant",
      "content": "¡Hola! ¿En qué puedo ayudarte?",
      "timestamp": "2024-01-15T10:00:01"
    }
  ]
}
```

### DELETE /api/v1/sessions/{session_id}

Limpia una sesión específica.

**Response:**
```json
{
  "message": "Sesión limpiada exitosamente",
  "session_id": "abc-123"
}
```

### GET /api/v1/info

Obtiene información del microservicio.

**Response:**
```json
{
  "name": "Arludent AI Microservice",
  "version": "1.0.0",
  "environment": "development",
  "model": "gpt-4o-mini",
  "tools_count": 5,
  "tools": [
    "buscar_paciente",
    "consultar_citas",
    "consultar_historial_clinico",
    "consultar_disponibilidad_medico",
    "listar_medicos"
  ]
}
```

---

## 🔧 Herramientas del Agente

El agente cuenta con las siguientes herramientas para interactuar con el backend:

### 1. buscar_paciente
Busca información de un paciente por DNI, ID o nombre.

**Ejemplo de uso:**
- "Busca al paciente con DNI 12345678"
- "¿Quién es el paciente 5?"
- "Busca a Juan Pérez"

### 2. consultar_citas
Consulta las citas médicas programadas de un paciente o médico.

**Ejemplo de uso:**
- "¿Cuáles son mis citas?"
- "Muéstrame las citas del paciente 5"
- "¿Qué citas tiene el doctor Gómez?"

### 3. consultar_historial_clinico
Obtiene el historial clínico de un paciente.

**Ejemplo de uso:**
- "Muéstrame el historial clínico del paciente 5"
- "¿Qué diagnósticos tiene?"

### 4. consultar_disponibilidad_medico
Verifica la disponibilidad de un médico en una fecha.

**Ejemplo de uso:**
- "¿Está disponible el doctor Gómez mañana?"
- "¿Qué horarios tiene libre el médico 2 el 2024-01-20?"

### 5. listar_medicos
Lista todos los médicos disponibles, opcionalmente por especialidad.

**Ejemplo de uso:**
- "¿Qué médicos hay disponibles?"
- "Muéstrame los ortodoncistas"

---

## 🔗 Integración con Backend

### Endpoints Internos Requeridos en Laravel

El microservicio necesita que el backend Laravel exponga estos endpoints **internos** (sin autenticación JWT):

```php
// routes/internal.php
Route::middleware(['internal.api.key'])->prefix('internal')->group(function () {
    
    // Pacientes
    Route::get('/pacientes/{id}', [InternalController::class, 'getPaciente']);
    Route::get('/pacientes', [InternalController::class, 'getPacientes']);
    Route::get('/pacientes/dni/{dni}', [InternalController::class, 'getPacientePorDni']);
    
    // Citas
    Route::get('/citas/{id}', [InternalController::class, 'getCita']);
    Route::get('/pacientes/{id}/citas', [InternalController::class, 'getCitasPaciente']);
    Route::get('/medicos/{id}/citas', [InternalController::class, 'getCitasMedico']);
    
    // Historial
    Route::get('/pacientes/{id}/historial', [InternalController::class, 'getHistorial']);
    Route::get('/pacientes/{id}/historial-resumen', [InternalController::class, 'getHistorialResumen']);
    
    // Médicos
    Route::get('/medicos/{id}', [InternalController::class, 'getMedico']);
    Route::get('/medicos', [InternalController::class, 'getMedicos']);
    Route::get('/medicos/{id}/disponibilidad', [InternalController::class, 'getDisponibilidad']);
    
    // Health Check
    Route::get('/health', function () {
        return response()->json(['status' => 'ok']);
    });
});
```

### Middleware de Autenticación Interna

```php
// app/Http/Middleware/InternalApiKey.php
namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;

class InternalApiKey
{
    public function handle(Request $request, Closure $next)
    {
        $apiKey = $request->header('X-Internal-API-Key');
        
        if ($apiKey !== env('INTERNAL_API_KEY')) {
            return response()->json(['error' => 'Unauthorized'], 401);
        }
        
        return $next($request);
    }
}
```

---

## 🎨 Integración con Frontend

### Servicio de Chat en Vue.js

```typescript
// src/api/chatService.ts
import axios from 'axios';

const API_URL = import.meta.env.VITE_AI_MICROSERVICE_URL || 'http://localhost:8001/api/v1';

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export interface ChatRequest {
  message: string;
  session_id?: string;
  user_id?: number;
  user_context?: Record<string, any>;
}

export interface ChatResponse {
  message: string;
  session_id: string;
  timestamp: string;
  metadata?: Record<string, any>;
}

class ChatService {
  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    const response = await axios.post(`${API_URL}/chat`, request);
    return response.data;
  }

  async getSessionHistory(sessionId: string) {
    const response = await axios.get(`${API_URL}/sessions/${sessionId}/history`);
    return response.data;
  }

  async clearSession(sessionId: string) {
    await axios.delete(`${API_URL}/sessions/${sessionId}`);
  }

  async checkHealth() {
    const response = await axios.get(`${API_URL}/health`);
    return response.data;
  }
}

export const chatService = new ChatService();
```

### Componente de Chat en Vue.js

```vue
<template>
  <div class="chat-container">
    <div class="messages">
      <div v-for="(msg, idx) in messages" :key="idx" :class="`message ${msg.role}`">
        {{ msg.content }}
      </div>
    </div>
    <div class="input-area">
      <input v-model="inputMessage" @keyup.enter="sendMessage" placeholder="Escribe tu mensaje..." />
      <button @click="sendMessage">Enviar</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { chatService } from '@/api/chatService';
import { useAuthStore } from '@/stores/authStore';

const authStore = useAuthStore();
const messages = ref<any[]>([]);
const inputMessage = ref('');
const sessionId = ref<string | null>(null);

async function sendMessage() {
  if (!inputMessage.value.trim()) return;

  // Agregar mensaje del usuario
  messages.value.push({
    role: 'user',
    content: inputMessage.value
  });

  const userMessage = inputMessage.value;
  inputMessage.value = '';

  try {
    const response = await chatService.sendMessage({
      message: userMessage,
      session_id: sessionId.value || undefined,
      user_id: authStore.user?.id_usuario,
      user_context: {
        nombre: authStore.user?.username,
        rol: authStore.user?.roles[0]
      }
    });

    // Guardar session ID
    sessionId.value = response.session_id;

    // Agregar respuesta del asistente
    messages.value.push({
      role: 'assistant',
      content: response.message
    });
  } catch (error) {
    console.error('Error sending message:', error);
  }
}
</script>
```

---

## 🚀 Despliegue

### Usando Docker

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8001

CMD ["python", "main.py"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  arludent-ai:
    build: .
    ports:
      - "8001:8001"
    env_file:
      - .env
    restart: unless-stopped
    depends_on:
      - backend
```

### En Servidor (Ubuntu)

```bash
# Instalar Python 3.11
sudo apt update
sudo apt install python3.11 python3.11-venv

# Clonar proyecto
git clone <repo>
cd arludent-ai-microservice

# Crear entorno virtual
python3.11 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar .env
nano .env

# Ejecutar con systemd
sudo nano /etc/systemd/system/arludent-ai.service
```

**arludent-ai.service:**
```ini
[Unit]
Description=Arludent AI Microservice
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/arludent-ai-microservice
Environment="PATH=/var/www/arludent-ai-microservice/venv/bin"
ExecStart=/var/www/arludent-ai-microservice/venv/bin/python main.py

[Install]
WantedBy=multi-user.target
```

```bash
# Habilitar y ejecutar
sudo systemctl enable arludent-ai
sudo systemctl start arludent-ai
sudo systemctl status arludent-ai
```

---

## 🧪 Testing

```powershell
# Instalar dependencias de testing
pip install pytest pytest-asyncio pytest-cov

# Ejecutar tests
pytest

# Con cobertura
pytest --cov=app --cov-report=html
```

---

## 📝 Notas Importantes

1. **Seguridad:** El `BACKEND_INTERNAL_API_KEY` debe ser secreto y compartido solo entre el microservicio y el backend
2. **Rate Limiting:** Considera implementar rate limiting en producción
3. **Monitoreo:** Usa logs para monitorear el comportamiento del agente
4. **Costos:** OpenAI cobra por tokens usados, monitorea tu uso
5. **Escalabilidad:** Para múltiples instancias, considera usar Redis para sesiones compartidas

---

## 📄 Licencia

Proyecto privado - Todos los derechos reservados © Arludent 2024

---

## 👥 Soporte

Para preguntas o soporte:
- **Email:** soporte@arludent.com
- **Documentación:** http://localhost:8001/docs

---

**¡Gracias por usar Arludent AI Microservice! 🦷🤖**
