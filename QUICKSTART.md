# Guía de Inicio Rápido

## ⚡ Configuración Rápida (5 minutos)

### 1. Activar entorno virtual e instalar dependencias

```powershell
# Activar entorno virtual
.\venv\Scripts\Activate.ps1

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configurar variables de entorno

Edita el archivo `.env` y agrega tu OpenAI API Key:

```env
OPENAI_API_KEY=sk-proj-TU-KEY-AQUI
```

### 3. Iniciar el microservicio

```powershell
python main.py
```

¡Listo! El servicio estará disponible en: **http://localhost:8001**

---

## 🧪 Probar el Microservicio

### Opción 1: Swagger UI (Recomendado)

1. Abre tu navegador en: **http://localhost:8001/docs**
2. Expande el endpoint **POST /api/v1/chat**
3. Click en **"Try it out"**
4. Usa este JSON de ejemplo:

```json
{
  "message": "Hola, ¿qué puedes hacer?",
  "session_id": null,
  "user_id": 1
}
```

5. Click en **Execute**

### Opción 2: cURL

```powershell
curl -X POST "http://localhost:8001/api/v1/chat" `
  -H "Content-Type: application/json" `
  -d '{\"message\": \"Hola, ¿qué puedes hacer?\", \"user_id\": 1}'
```

### Opción 3: PowerShell

```powershell
$body = @{
    message = "Hola, ¿qué puedes hacer?"
    user_id = 1
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8001/api/v1/chat" `
  -Method Post `
  -Body $body `
  -ContentType "application/json"
```

---

## 📋 Checklist de Verificación

- [ ] Entorno virtual activado
- [ ] Dependencias instaladas
- [ ] OpenAI API Key configurada en `.env`
- [ ] Backend Laravel ejecutándose en puerto 8000
- [ ] Microservicio ejecutándose en puerto 8001
- [ ] Health check exitoso: `curl http://localhost:8001/api/v1/health`

---

## ⚠️ Problemas Comunes

### Error: "Import 'pydantic' could not be resolved"

**Solución:**
```powershell
pip install -r requirements.txt
```

### Error: "OPENAI_API_KEY not set"

**Solución:** Agrega tu API Key en el archivo `.env`

### Error: "Connection refused to backend"

**Solución:** Asegúrate que el backend Laravel esté ejecutándose en puerto 8000

---

## 🎯 Próximos Pasos

1. ✅ Microservicio funcionando
2. 🔧 Agregar endpoints internos en Backend Laravel
3. 🎨 Integrar componente de chat en Frontend Vue.js
4. 🚀 ¡Listo para usar!

---

Para más detalles, consulta el [README.md](README.md) completo.
