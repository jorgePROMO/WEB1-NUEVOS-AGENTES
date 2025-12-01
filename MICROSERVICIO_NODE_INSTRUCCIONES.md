# 🚀 Microservicio Node.js - Instrucciones de Implementación

**Fecha:** 1 Diciembre 2025  
**Solución final:** Microservicio Node.js con OpenAI Agents SDK

---

## ✅ LO QUE SE HA IMPLEMENTADO

He creado la estructura completa del microservicio Node.js en `/app/edn360-workflow-service/`:

```
/app/edn360-workflow-service/
├── package.json                     ✅ Dependencias configuradas
├── tsconfig.json                    ✅ TypeScript configurado
├── .env.example                     ✅ Ejemplo de configuración
├── src/
│   ├── server.ts                    ✅ Servidor Express
│   └── edn360_workflow.ts           ⏳ AQUÍ DEBES PEGAR TU CÓDIGO
```

---

## 📋 LO QUE JORGE DEBE HACER

### 1. Pegar el código del SDK de Agentes

Jorge, necesitas copiar todo el código que te genera Agent Builder en la pestaña "SDK de agentes" y pegarlo en:

```
/app/edn360-workflow-service/src/edn360_workflow.ts
```

**IMPORTANTE:** El código debe incluir:
- Todos los agentes (E1, E2, E3, E4, E5, E6, E7, E7.5)
- Los schemas de Zod
- El Runner configurado con tu workflow_id
- La función `runWorkflow`

**CRÍTICO:** Asegúrate de que `runWorkflow` devuelva el resultado:

```typescript
export const runWorkflow = async (workflow: WorkflowInput) => {
  return await withTrace("EDN360 – Entreno v1", async () => {
    // ... todo el código de los agentes ...
    
    const e75TrainingPlanEnricherResult = {
      output_text: JSON.stringify(e75TrainingPlanEnricherResultTemp.finalOutput),
      output_parsed: e75TrainingPlanEnricherResultTemp.finalOutput
    };

    // 👇 AÑADIR ESTE RETURN SI NO ESTÁ
    return e75TrainingPlanEnricherResult.output_parsed;
  });
}
```

### 2. Crear el archivo .env

```bash
cd /app/edn360-workflow-service
cp .env.example .env
```

Editar `.env`:
```bash
EDN360_WORKFLOW_PORT=4000
OPENAI_API_KEY=tu_api_key_de_openai_aqui
```

### 3. Instalar dependencias y compilar

```bash
cd /app/edn360-workflow-service
yarn install
yarn build
```

### 4. Iniciar el microservicio

```bash
yarn start
```

O para desarrollo con hot-reload:
```bash
yarn dev
```

---

## 🔧 BACKEND PYTHON ACTUALIZADO

El backend ya está configurado para usar el microservicio:

**Archivo:** `/app/backend/services/training_workflow_service.py`

**Cambios:**
- ✅ Eliminado todo el código de ChatKit
- ✅ Ahora hace un simple POST al microservicio
- ✅ Mantiene la misma validación de `client_training_program_enriched`

**Variable de entorno:**
```bash
EDN360_WORKFLOW_SERVICE_URL="http://localhost:4000/api/edn360/run-training-workflow"
```

---

## 🎯 FLUJO COMPLETO

```
Usuario → Click "Generar plan (EDN360)"
  ↓
Frontend → POST /api/training-plan
  ↓
Backend Python construye EDN360Input
  ↓
Backend Python → POST http://localhost:4000/api/edn360/run-training-workflow
  ↓
Microservicio Node.js recibe EDN360Input
  ↓
Microservicio ejecuta runWorkflow() con Agents SDK
  ↓
Workflow ejecuta agentes E1-E7.5
  ↓
Workflow devuelve { client_training_program_enriched: {...} }
  ↓
Microservicio devuelve JSON al Backend Python
  ↓
Backend valida y guarda en edn360_snapshots + training_plans_v2
  ↓
Backend devuelve plan al Frontend
  ↓
Frontend renderiza plan completo
```

---

## 📊 VENTAJAS DE ESTA SOLUCIÓN

1. **Usa el SDK oficial** de OpenAI Agents (no hackeos con ChatKit)
2. **Endpoints soportados** (no más 404)
3. **Contrato claro** entre servicios
4. **Fácil de debuggear** (logs en ambos servicios)
5. **Escalable** (el microservicio puede correr en contenedor separado)

---

## 🧪 CÓMO PROBAR

### 1. Verificar que el microservicio está corriendo:

```bash
curl http://localhost:4000/health
```

Debería devolver:
```json
{"status":"ok","service":"edn360-workflow-service"}
```

### 2. Probar el endpoint directamente:

```bash
curl -X POST http://localhost:4000/api/edn360/run-training-workflow \
  -H "Content-Type: application/json" \
  -d '{
    "user_profile": {...},
    "questionnaires": [...],
    "context": {...}
  }'
```

### 3. Probar desde el admin panel:

1. Refresca el panel admin (Ctrl+R)
2. Abre Jorge2
3. Tab "Entrenamiento"
4. Click "Generar plan (EDN360)"
5. Espera 1-2 minutos

---

## 📋 INPUT/OUTPUT (SIN CAMBIOS)

### INPUT que recibe el microservicio:
```json
{
  "user_profile": {
    "user_id": "1764168881795908",
    "name": "Jorge2",
    ...
  },
  "questionnaires": [
    {
      "submission_id": "...",
      "answers": {...}
    }
  ],
  "context": {
    "request_type": "training_plan_generation",
    ...
  }
}
```

### OUTPUT que debe devolver el microservicio:
```json
{
  "client_training_program_enriched": {
    "title": "...",
    "summary": "...",
    "sessions": [...]
  }
}
```

---

## ⚠️ POSIBLES ERRORES

### Error: Cannot find module '@openai/agents'
**Solución:** 
```bash
cd /app/edn360-workflow-service
yarn install
```

### Error: runWorkflow is not implemented
**Causa:** Aún no has pegado el código de Agent Builder en `edn360_workflow.ts`  
**Solución:** Pega el código completo del SDK de agentes

### Error: Connection refused
**Causa:** El microservicio no está corriendo  
**Solución:** 
```bash
cd /app/edn360-workflow-service
yarn start
```

### Error: OPENAI_API_KEY not found
**Causa:** El .env no está configurado  
**Solución:** Crear `.env` con tu API key

---

## 🔍 DEBUG

### Logs del microservicio:
```bash
cd /app/edn360-workflow-service
yarn start
# Los logs aparecerán en la consola
```

### Logs del backend Python:
```bash
tail -f /var/log/supervisor/backend.err.log | grep -i "workflow\|microservicio"
```

---

## 📝 RESUMEN PARA JORGE

1. **Pega el código de Agent Builder** en `/app/edn360-workflow-service/src/edn360_workflow.ts`
2. **Añade el return** al final de `runWorkflow` si no está
3. **Configura el .env** con tu API key
4. **Instala y arranca**: `yarn install && yarn build && yarn start`
5. **Prueba** desde el admin panel

Con esto debería funcionar correctamente sin 404 de ChatKit. 🚀
