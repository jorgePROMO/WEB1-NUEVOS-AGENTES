# Sistema E.D.N.360

Sistema de generación automática de planes de entrenamiento y nutrición con 26 agentes especializados basados en IA.

## 📋 Descripción General

E.D.N.360 (Entrenamiento Deportivo + Nutrición 360°) es un sistema avanzado que utiliza 26 agentes de IA especializados para generar planes personalizados de entrenamiento y nutrición.

### Características Principales

- ✅ **26 Agentes Especializados**: Cada agente tiene una función específica
- ✅ **Arquitectura Event-Driven**: Ejecución secuencial con validaciones
- ✅ **Contratos JSON Estrictos**: Validación automática de datos
- ✅ **Reglas Transversales**: Seguridad y coherencia garantizadas
- ✅ **Versionado de Planes**: Historial de modificaciones
- ✅ **Chat IA para Modificaciones**: Ajustes inteligentes

## 🏗️ Arquitectura

```
Cliente → Formulario → Admin Panel
                           ↓
                    Orquestador E.D.N.360
                           ↓
        ┌──────────────────┴──────────────────┐
        ↓                                     ↓
Entrenamiento (E1-E9)              Nutrición (N0-N8)
        ↓                                     ↓
        └──────────────────┬──────────────────┘
                           ↓
                    Plan Completo (Draft)
                           ↓
              Admin Visualiza/Modifica/Aprueba
                           ↓
              Envío (Email/WhatsApp/Docs)
```

## 📊 Agentes del Sistema

### Bloque 1: Entrenamiento Inicial (E1-E9)

1. **E1 - Analista del Atleta**: Limpia y estructura datos del cuestionario
2. **E2 - Evaluador de Capacidad y Riesgo**: Calcula SEG, split, RIR objetivo
3. **E3 - Analista de Historial**: Determina IA, tipo adaptador, estrategia
4. **E4 - Arquitecto del Programa**: Diseña mesociclo de 4 semanas
5. **E5 - Ingeniero de Microciclos**: Crea sesiones detalladas
6. **E6 - Técnico Clínico**: Adapta para lesiones, añade correctivos
7. **E7 - Analista de Carga**: Calcula CIT e IRG
8. **E8 - Auditor Técnico**: QA completo del plan
9. **E9 - Bridge Nutrición**: Traduce carga a mapa energético

### Bloque 2: Nutrición Inicial (N0-N8)

0. **N0 - Triage**: Filtra rapidez/impaciencia, determina elegibilidad
1. **N1 - Analista Metabólico**: Calcula TDEE, BMR, TA
2. **N2 - Selector Energético**: Define kcal objetivo y macros
3. **N3 - Snap a Plantilla**: Asigna plantilla comercial
4. **N4 - Sincronizador A/M/B**: Genera calendario mensual
5. **N5 - Reparto & Timing**: Distribuye macros en comidas
6. **N6 - Menús**: Genera menús reales con equivalencias
7. **N7 - Coach Adherencia**: Minimiza fricción
8. **N8 - Watchdog**: Auditoría final de seguridad

### Bloque 3: Seguimiento Entrenamiento (ES1-ES4)

1. **ES1 - Intérprete**: Convierte cuestionario → diagnóstico
2. **ES2 - Evaluador**: Cruza KPI, carga, recuperación
3. **ES3 - Arquitecto Ajustes**: Aplica ajustes cuantificados
4. **ES4 - Auditor**: Valida coherencia y handoff

### Bloque 4: Seguimiento Nutrición (NS1-NS4)

1. **NS1 - Intérprete Metabólico**: Diagnóstico mensual
2. **NS2 - Evaluador Energía**: Recalcula TDEE, detecta TA
3. **NS3 - Ajustador Macros**: Actualiza plan A/M/B
4. **NS4 - Auditor Nutricional**: Validación final

## 🔧 Uso del Sistema

### API Endpoints

#### 1. Generar Plan Inicial

```http
POST /api/admin/edn360/generate-initial-plan
Content-Type: multipart/form-data

{
  "questionnaire_id": "...",
  "client_id": "...",
  "admin_notes": "..." (opcional)
}
```

**Respuesta:**
```json
{
  "success": true,
  "plan_id": "edn360_...",
  "status": "draft",
  "duration_seconds": 120.5,
  "validation": {
    "valid": true,
    "errors": [],
    "warnings": []
  }
}
```

#### 2. Generar Seguimiento Mensual

```http
POST /api/admin/edn360/generate-followup-plan
Content-Type: multipart/form-data

{
  "client_id": "...",
  "followup_questionnaire_id": "...",
  "admin_notes": "..." (opcional)
}
```

#### 3. Obtener Plan

```http
GET /api/admin/edn360/plans/{plan_id}
```

#### 4. Modificar Plan con Chat IA

```http
POST /api/admin/edn360/plans/{plan_id}/chat
Content-Type: multipart/form-data

{
  "message": "Reduce las series de press banca en 2",
  "context": "..." (opcional)
}
```

**Respuesta:**
```json
{
  "success": true,
  "ai_response": "He reducido las series de press banca...",
  "modifications_made": true,
  "new_version": 2
}
```

#### 5. Aprobar Plan

```http
PUT /api/admin/edn360/plans/{plan_id}/approve
```

#### 6. Enviar Plan al Cliente

```http
POST /api/admin/edn360/plans/{plan_id}/send
Content-Type: multipart/form-data

{
  "delivery_method": "email|whatsapp|attach_to_docs",
  "custom_message": "..." (opcional)
}
```

## ⚙️ Reglas Duras del Sistema

### Entrenamiento

- ✅ Sesión ≤ 90 minutos
- ✅ Equilibrio Push/Pull: 0.9 - 1.1
- ✅ Equilibrio Cadera/Rodilla: 0.8 - 1.2
- ✅ CIT óptimo: 35 - 55
- ✅ IRG mínimo: ≥5 (óptimo ≥7)
- ✅ Desequilibrios <10%

### Nutrición

- ✅ Proteína ≥ 1.8 g/kg (óptimo: 2.0-2.4 g/kg)
- ✅ Grasa ≥ 0.6 g/kg (óptimo: 0.8-1.0 g/kg)
- ✅ Calorías mínimas: Hombre ≥1600 kcal, Mujer ≥1300 kcal
- ✅ Variación semanal ≤ ±10%
- ✅ Sincronización con días A/M/B del entrenamiento

## 🗄️ Base de Datos

### Collections MongoDB

- **edn360_plans**: Planes generados
- **edn360_questionnaires**: Cuestionarios procesados (opcional)

### Estructura de un Plan

```json
{
  "_id": "edn360_client123_1234567890",
  "client_id": "client123",
  "client_name": "Juan Pérez",
  "plan_type": "initial_complete|followup_complete",
  "status": "pending|generating|draft|approved|sent",
  "created_at": "2025-01-15T10:00:00Z",
  "training_plan": {
    "e1_perfil_tecnico": {...},
    "e2_capacidad_riesgo": {...},
    ...
  },
  "nutrition_plan": {
    "n0_triage": {...},
    "n1_analista_metabolico": {...},
    ...
  },
  "agent_executions": [...],
  "validation": {
    "valid": true,
    "errors": [],
    "warnings": []
  },
  "chat_history": [...],
  "modifications": [...]
}
```

## 🧪 Testing

Para probar el sistema:

1. **Crear un cuestionario de prueba**
2. **Generar plan inicial**:
   ```bash
   curl -X POST http://localhost:8001/api/admin/edn360/generate-initial-plan \
     -F "questionnaire_id=..." \
     -F "client_id=..." \
     -H "Authorization: Bearer YOUR_TOKEN"
   ```
3. **Verificar logs**: Ver la ejecución de cada agente en los logs del backend

## 🔐 Seguridad

- ✅ Todas las rutas requieren autenticación admin
- ✅ Validación de datos en cada agente
- ✅ Versionado de planes para trazabilidad
- ✅ Logs detallados de todas las operaciones

## 📈 Performance

- Tiempo estimado plan inicial: **2-4 minutos** (18 agentes)
- Tiempo estimado seguimiento: **1-2 minutos** (8 agentes)
- Optimización: Ejecución secuencial con validaciones

## 🚀 Próximas Mejoras

- [ ] Generación de PDFs automática
- [ ] Envío por email/WhatsApp
- [ ] Dashboard visual de métricas
- [ ] Paralelización de agentes cuando sea posible
- [ ] Cache de resultados parciales
- [ ] Sistema de notificaciones en tiempo real

## 📝 Notas de Desarrollo

- Los prompts completos de los agentes están en cada archivo del agente
- El orquestador maneja automáticamente los errores y reintentos
- Cada agente registra su ejecución para debugging
- Los contratos JSON garantizan compatibilidad entre agentes

## 🆘 Troubleshooting

### Error: "EMERGENT_LLM_KEY no configurada"
Solución: Añadir la clave en `/app/backend/.env`:
```
EMERGENT_LLM_KEY=your_key_here
```

### Error: "Agent execution failed"
Solución: Revisar logs del backend:
```bash
tail -f /var/log/supervisor/backend.err.log
```

### Plan con warnings
Solución: Los warnings no bloquean el plan, pero revisa:
- Equilibrios musculares
- CIT e IRG
- Distribución de macros

---

**Versión:** 1.0.0  
**Última actualización:** 2025-01-15  
**Desarrollado para:** Jorge Calcerrada Training System
