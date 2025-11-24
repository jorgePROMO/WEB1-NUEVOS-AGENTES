# CUESTIONARIO DE SEGUIMIENTO - Variables y Estructura Completa

**Documento:** Especificación técnica del cuestionario de seguimiento mensual EDN360  
**Fecha:** Enero 2025  
**Colección MongoDB:** `follow_up_submissions` (BD Web)  
**Tipo:** Cuestionario mensual de evolución y ajuste  
**Periodicidad:** Mensual (aprox. 30 días después del último plan)

---

## 📋 ESTRUCTURA GENERAL

```javascript
{
  _id: string,                        // ID único del cuestionario de seguimiento
  user_id: string,                    // ID del usuario en BD Web
  submission_date: datetime,          // Fecha y hora de envío
  days_since_last_plan: number,       // Días desde el último plan
  previous_plan_id: string,           // ID del plan anterior
  previous_questionnaire_id: string,  // ID del cuestionario anterior (inicial o followup previo)
  measurement_type: string,           // Tipo de medición ("smart_scale" / "manual")
  measurements: { ... },              // Medidas corporales
  adherence: { ... },                 // Adherencia al plan
  wellbeing: { ... },                 // Bienestar general
  changes_perceived: { ... },         // Cambios percibidos
  feedback: { ... },                  // Feedback y objetivos
  status: string,                     // Estado del seguimiento
  ai_analysis: object | null,         // Análisis de IA (si generado)
  ai_analysis_edited: boolean,        // Si el análisis fue editado manualmente
  new_plan_id: string | null,         // ID del nuevo plan generado (si existe)
  created_at: datetime,               // Fecha de creación del registro
  updated_at: datetime                // Última actualización
}
```

---

## 🔍 SECCIONES DEL CUESTIONARIO

### 1. METADATOS Y CONTEXTO

Estos campos se generan automáticamente al crear el seguimiento:

| Variable | Tipo | Descripción | Ejemplo | Autogenerado |
|----------|------|-------------|---------|--------------|
| `_id` | string | ID único del seguimiento | "1763222319583652" | ✅ Sí |
| `user_id` | string | ID del usuario | "1762976907472415" | ✅ Sí |
| `submission_date` | datetime | Fecha de envío | "2025-11-15 15:58:39.583000" | ✅ Sí |
| `days_since_last_plan` | number | Días desde el último plan | 0 (o 30, 60, etc.) | ✅ Sí |
| `previous_plan_id` | string | ID del plan anterior | "1763221056533638" | ✅ Sí |
| `previous_questionnaire_id` | string | ID del cuestionario anterior | "1762977457211469" | ✅ Sí |
| `created_at` | datetime | Fecha de creación | "2025-11-15 15:58:39.583000" | ✅ Sí |
| `updated_at` | datetime | Última actualización | "2025-11-15 15:58:39.583000" | ✅ Sí |

---

### 2. TIPO DE MEDICIÓN

| Variable | Tipo | Pregunta | Opciones | Requerido |
|----------|------|---------|---------|-----------|
| `measurement_type` | string | ¿Cómo vas a registrar tus medidas? | "smart_scale" / "manual" | ✅ Sí |

**Descripción:**
- **"smart_scale":** El usuario tiene báscula inteligente (datos automáticos de grasa, músculo, agua, etc.)
- **"manual":** El usuario mide manualmente con cinta métrica (perímetros corporales)

---

### 3. MEDIDAS CORPORALES (measurements)

Las medidas disponibles dependen del `measurement_type` seleccionado.

#### 3.1. Medidas Comunes (Ambos tipos)

| Variable | Tipo | Pregunta | Unidad | Requerido |
|----------|------|---------|--------|-----------|
| `peso` | string/number | Peso corporal actual | kg | ✅ Sí |

#### 3.2. Medidas de Báscula Inteligente (measurement_type = "smart_scale")

| Variable | Tipo | Pregunta | Unidad | Ejemplo | Requerido |
|----------|------|---------|--------|---------|-----------|
| `grasa_corporal` | string/number | Porcentaje de grasa corporal | % | "31" | ✅ Sí |
| `masa_muscular` | string/number | Masa muscular | kg | "73" | ✅ Sí |
| `grasa_visceral` | string/number | Nivel de grasa visceral | nivel | "9" | ⚠️ Opcional |
| `agua_corporal` | string/number | Porcentaje de agua corporal | % | "55" | ⚠️ Opcional |

#### 3.3. Medidas Manuales (measurement_type = "manual")

| Variable | Tipo | Pregunta | Unidad | Requerido |
|----------|------|---------|--------|-----------|
| `circunferencia_pecho` | string/number | Circunferencia de pecho | cm | ⚠️ Opcional |
| `circunferencia_cintura` | string/number | Circunferencia de cintura | cm | ✅ Sí |
| `circunferencia_gluteo` | string/number | Circunferencia de glúteo/cadera | cm | ⚠️ Opcional |
| `circunferencia_muslo` | string/number | Circunferencia de muslo | cm | ⚠️ Opcional |
| `circunferencia_brazo_relajado` | string/number | Circunferencia de brazo relajado | cm | ⚠️ Opcional |
| `circunferencia_brazo_flexionado` | string/number | Circunferencia de brazo flexionado | cm | ⚠️ Opcional |
| `circunferencia_gemelo` | string/number | Circunferencia de gemelo | cm | ⚠️ Opcional |

#### 3.4. Satisfacción con Cambios (Ambos tipos)

| Variable | Tipo | Pregunta | Opciones | Requerido |
|----------|------|---------|---------|-----------|
| `satisfecho_cambios` | string | ¿Estás satisfecho con los cambios físicos? | "Muy insatisfecho" / "Insatisfecho" / "Neutral" / "Satisfecho" / "Muy satisfecho" | ⚠️ Opcional |

**Nota:** Todos los campos de `measurements` que no corresponden al tipo seleccionado se quedan en `null`.

---

### 4. ADHERENCIA AL PLAN (adherence)

| Variable | Tipo | Pregunta | Formato | Ejemplo | Requerido |
|----------|------|---------|---------|---------|-----------|
| `constancia_entrenamiento` | string | ¿Qué porcentaje de entrenamientos has completado? | "0-10%" / "10-30%" / "30-50%" / "50-70%" / "70-90%" / "90-100%" | "90%" | ✅ Sí |
| `seguimiento_alimentacion` | string | ¿Qué porcentaje de adherencia tuviste a la alimentación? | "0-10%" / "10-30%" / "30-50%" / "50-70%" / "70-90%" / "90-100%" | "90%" | ✅ Sí |

**Descripción:**
- `constancia_entrenamiento`: Mide cuántos entrenamientos del plan completó el cliente
- `seguimiento_alimentacion`: Mide cuánto siguió las pautas nutricionales

---

### 5. BIENESTAR GENERAL (wellbeing)

#### 5.1. Factores Externos

| Variable | Tipo | Pregunta | Formato | Ejemplo | Requerido |
|----------|------|---------|---------|---------|-----------|
| `factores_externos` | string | ¿Ha habido cambios importantes en tu vida este mes? (trabajo, horarios, estrés, viajes, etc.) | Texto libre (textarea) | "Me han cambiado el turno de trabajo, ahora trabajo por las mañanas y entrenaré a las 18h" | ⚠️ Opcional |

#### 5.2. Estado Anímico y Energía

| Variable | Tipo | Pregunta | Opciones | Requerido |
|----------|------|---------|---------|-----------|
| `energia_animo_motivacion` | string | ¿Cómo ha sido tu energía, ánimo y motivación este mes? | "Mucho peor" / "Peor" / "Igual" / "Mejorado" / "Mucho mejor" | ✅ Sí |

#### 5.3. Sueño y Estrés

| Variable | Tipo | Pregunta | Opciones | Requerido |
|----------|------|---------|---------|-----------|
| `sueno_estres` | string | ¿Cómo ha sido tu sueño y nivel de estrés? | "Mucho peor" / "Peor" / "Igual" / "Mejorado" / "Mucho mejor" | ✅ Sí |

---

### 6. CAMBIOS PERCIBIDOS (changes_perceived)

#### 6.1. Molestias o Lesiones

| Variable | Tipo | Pregunta | Opciones | Requerido |
|----------|------|---------|---------|-----------|
| `molestias_dolor_lesion` | string | ¿Cómo han evolucionado tus molestias, dolor o lesiones? | "Mucho peor" / "Peor" / "Igual" / "Mejorado" / "Mucho mejor" / "No tenía" | ✅ Sí |

#### 6.2. Cambios Corporales

| Variable | Tipo | Pregunta | Formato | Ejemplo | Requerido |
|----------|------|---------|---------|---------|-----------|
| `cambios_corporales` | string | ¿Qué cambios corporales has notado este mes? | Texto libre (textarea) | "Más músculo y más tripa y grasa general" | ✅ Sí |

**Descripción:**
El cliente describe en sus propias palabras los cambios físicos que ha percibido (puede ser subjetivo).

#### 6.3. Fuerza y Rendimiento

| Variable | Tipo | Pregunta | Opciones | Requerido |
|----------|------|---------|---------|-----------|
| `fuerza_rendimiento` | string | ¿Cómo ha evolucionado tu fuerza y rendimiento? | "Mucho peor" / "Peor" / "Igual" / "Mejorado" / "Mucho mejor" | ✅ Sí |

---

### 7. FEEDBACK Y OBJETIVOS (feedback)

#### 7.1. Objetivo del Próximo Mes

| Variable | Tipo | Pregunta | Formato | Ejemplo | Requerido |
|----------|------|---------|---------|---------|-----------|
| `objetivo_proximo_mes` | string | ¿Cuál es tu objetivo principal para el próximo mes? | Texto libre (textarea) | "Quiero seguir ganando masa muscular pero sin ganar grasa" | ✅ Sí |

#### 7.2. Cambios Deseados en el Plan

| Variable | Tipo | Pregunta | Formato | Ejemplo | Requerido |
|----------|------|---------|---------|---------|-----------|
| `cambios_deseados` | string | ¿Qué cambios te gustaría hacer en el plan de entrenamiento o nutrición? | Texto libre (textarea) | "Sobre todo lo del cambio de turno" | ⚠️ Opcional |

#### 7.3. Comentarios Adicionales

| Variable | Tipo | Pregunta | Formato | Requerido |
|----------|------|---------|---------|-----------|
| `comentarios_adicionales` | string | ¿Algo más que quieras comentarnos? | Texto libre (textarea) | ⚠️ Opcional |

---

### 8. ESTADO Y ANÁLISIS (Campos del Sistema)

Estos campos se gestionan automáticamente por el sistema:

| Variable | Tipo | Descripción | Valores Posibles | Autogenerado |
|----------|------|-------------|------------------|--------------|
| `status` | string | Estado del seguimiento | "pending_analysis" / "analyzed" / "plan_generated" / "archived" | ✅ Sí |
| `ai_analysis` | object / null | Análisis generado por IA (outputs de agentes) | JSON con outputs E1-E9, N0-N8 | ⚠️ Condicional |
| `ai_analysis_edited` | boolean | Si el análisis fue editado manualmente por admin | true / false | ✅ Sí (default: false) |
| `new_plan_id` | string / null | ID del nuevo plan generado a partir de este seguimiento | "1763..." / null | ⚠️ Condicional |

**Estados del seguimiento:**
- **"pending_analysis":** Cuestionario recién enviado, esperando análisis
- **"analyzed":** Análisis de IA completado, esperando generación de plan
- **"plan_generated":** Plan nuevo generado exitosamente
- **"archived":** Seguimiento archivado (no se generará plan)

---

## 📊 RESUMEN DE VARIABLES

### Por Sección

| Sección | Variables | Requeridas | Opcionales |
|---------|-----------|------------|------------|
| **Metadatos** | 8 | 8 | 0 |
| **Tipo de medición** | 1 | 1 | 0 |
| **Medidas corporales** | 9 | 1-3 | 6-8 |
| **Adherencia** | 2 | 2 | 0 |
| **Bienestar** | 3 | 2 | 1 |
| **Cambios percibidos** | 3 | 3 | 0 |
| **Feedback** | 3 | 1 | 2 |
| **Sistema** | 4 | 4 | 0 |
| **TOTAL** | 33 | 22-24 | 9-11 |

### Por Tipo de Dato

| Tipo | Cantidad | Variables |
|------|----------|-----------|
| **string** | ~25 | Mayoría de campos |
| **number** | ~9 | Medidas corporales |
| **datetime** | 3 | `submission_date`, `created_at`, `updated_at` |
| **boolean** | 1 | `ai_analysis_edited` |
| **object** | 1 | `ai_analysis` |

---

## 🔧 NOTAS TÉCNICAS

### 1. Diferencias según measurement_type

El cuestionario cambia dinámicamente según el tipo de medición:

#### Si `measurement_type = "smart_scale"`:
```javascript
measurements: {
  peso: "90",
  grasa_corporal: "31",
  masa_muscular: "73",
  grasa_visceral: "9",
  agua_corporal: "55",
  // Los campos manuales quedan en null
  circunferencia_pecho: null,
  circunferencia_cintura: null,
  // ... etc
}
```

#### Si `measurement_type = "manual"`:
```javascript
measurements: {
  peso: "90",
  // Los campos de báscula quedan en null
  grasa_corporal: null,
  masa_muscular: null,
  grasa_visceral: null,
  agua_corporal: null,
  // Campos manuales activos
  circunferencia_cintura: "95",
  circunferencia_brazo_flexionado: "38",
  // ... etc
}
```

### 2. Validación de Adherencia

Los porcentajes de adherencia se validan con opciones predefinidas:
- "0-10%"
- "10-30%"
- "30-50%"
- "50-70%"
- "70-90%"
- "90-100%"

### 3. Escala de Mejora (5 puntos)

Varios campos usan una escala de 5 puntos:
- "Mucho peor"
- "Peor"
- "Igual"
- "Mejorado"
- "Mucho mejor"

Campos que usan esta escala:
- `energia_animo_motivacion`
- `sueno_estres`
- `molestias_dolor_lesion`
- `fuerza_rendimiento`

### 4. Almacenamiento en MongoDB

```javascript
{
  _id: string,
  user_id: string,
  submission_date: ISODate,
  days_since_last_plan: number,
  previous_plan_id: string,
  previous_questionnaire_id: string,
  measurement_type: "smart_scale" | "manual",
  measurements: {
    peso: string,
    // ... campos según measurement_type
  },
  adherence: {
    constancia_entrenamiento: string,
    seguimiento_alimentacion: string
  },
  wellbeing: {
    factores_externos: string,
    energia_animo_motivacion: string,
    sueno_estres: string
  },
  changes_perceived: {
    molestias_dolor_lesion: string,
    cambios_corporales: string,
    fuerza_rendimiento: string
  },
  feedback: {
    objetivo_proximo_mes: string,
    cambios_deseados: string,
    comentarios_adicionales: string
  },
  status: string,
  ai_analysis: object | null,
  ai_analysis_edited: boolean,
  new_plan_id: string | null,
  created_at: ISODate,
  updated_at: ISODate
}
```

### 5. Uso en Arquitectura Client Drawer

En la nueva arquitectura, este cuestionario se almacenará como:

```javascript
// En client_drawers collection
{
  user_id: "1762...",
  services: {
    shared_questionnaires: [
      {
        submission_id: "1762977457211469",
        submitted_at: ISODate,
        source: "initial",
        raw_payload: { /* cuestionario inicial */ }
      },
      {
        submission_id: "1763222319583652",  // ID del followup
        submitted_at: ISODate,
        source: "followup",
        raw_payload: { /* cuestionario de seguimiento */ }
      }
    ]
  }
}
```

### 6. Flujo de Procesamiento

1. **Usuario completa cuestionario** → Se guarda en `follow_up_submissions`
2. **Sistema detecta nuevo followup** → `status = "pending_analysis"`
3. **IA analiza datos** → Genera `ai_analysis` (outputs de agentes)
4. **Sistema genera nuevo plan** → `status = "plan_generated"`, `new_plan_id` asignado
5. **Plan enviado al cliente** → Ciclo se repite en 30 días

---

## 📋 EJEMPLO COMPLETO DE CUESTIONARIO DE SEGUIMIENTO

```javascript
{
  "_id": "1763222319583652",
  "user_id": "1762976907472415",
  "submission_date": "2025-11-15 15:58:39.583000",
  "days_since_last_plan": 0,
  "previous_plan_id": "1763221056533638",
  "previous_questionnaire_id": "1762977457211469",
  
  // Tipo de medición
  "measurement_type": "smart_scale",
  
  // Medidas corporales
  "measurements": {
    "peso": "90",
    "grasa_corporal": "31",
    "masa_muscular": "73",
    "grasa_visceral": "9",
    "agua_corporal": "55",
    // Campos manuales en null (no aplica para báscula inteligente)
    "circunferencia_pecho": null,
    "circunferencia_cintura": null,
    "circunferencia_gluteo": null,
    "circunferencia_muslo": null,
    "circunferencia_brazo_relajado": null,
    "circunferencia_brazo_flexionado": null,
    "circunferencia_gemelo": null,
    "satisfecho_cambios": null
  },
  
  // Adherencia al plan
  "adherence": {
    "constancia_entrenamiento": "90%",
    "seguimiento_alimentacion": "90%"
  },
  
  // Bienestar general
  "wellbeing": {
    "factores_externos": "Me han cambiado el turno de trabajo, ahora trabajo por las mañanas y entrenaré a las 18h",
    "energia_animo_motivacion": "Mejorado",
    "sueno_estres": "Mejorado"
  },
  
  // Cambios percibidos
  "changes_perceived": {
    "molestias_dolor_lesion": "Mejorado",
    "cambios_corporales": "Más músculo y más tripa y grasa general",
    "fuerza_rendimiento": "Mejorado"
  },
  
  // Feedback y objetivos
  "feedback": {
    "objetivo_proximo_mes": "Quiero seguir ganando masa muscular pero sin ganar grasa",
    "cambios_deseados": "Sobre todo lo del cambio de turno",
    "comentarios_adicionales": null
  },
  
  // Estado y análisis del sistema
  "status": "pending_analysis",
  "ai_analysis": null,
  "ai_analysis_edited": false,
  "new_plan_id": null,
  
  // Timestamps
  "created_at": "2025-11-15 15:58:39.583000",
  "updated_at": "2025-11-15 15:58:39.583000"
}
```

---

## 🔍 COMPARACIÓN CON CUESTIONARIO INICIAL

| Aspecto | Cuestionario Inicial | Cuestionario Seguimiento |
|---------|---------------------|--------------------------|
| **Propósito** | Conocer al cliente por primera vez | Evaluar evolución mensual |
| **Periodicidad** | Una vez (al inicio) | Mensual (cada 30 días aprox.) |
| **Duración** | Largo (~85 campos) | Corto (~18 campos útiles) |
| **Enfoque** | Historial completo (salud, experiencia, objetivos) | Cambios recientes (medidas, adherencia, feedback) |
| **Medidas** | Básicas (peso, altura, grasa) | Detalladas según tipo de medición |
| **Contexto** | Profundo (trabajo, horarios, dieta) | Cambios desde último plan |
| **Complejidad** | Alta (muchas secciones) | Media (enfocado en evolución) |

---

## 📊 ANÁLISIS DE ADHERENCIA

El cuestionario de seguimiento permite evaluar:

1. **Adherencia cuantitativa:**
   - % de entrenamientos completados
   - % de seguimiento de alimentación

2. **Adherencia cualitativa:**
   - Energía y motivación
   - Calidad del sueño
   - Nivel de estrés

3. **Resultados objetivos:**
   - Cambios en peso
   - Cambios en composición corporal
   - Cambios en perímetros

4. **Resultados subjetivos:**
   - Percepción de cambios corporales
   - Evolución de molestias/lesiones
   - Mejora de fuerza/rendimiento

5. **Factores externos:**
   - Cambios en trabajo
   - Cambios en horarios
   - Eventos de vida importantes

**Estos 5 factores permiten a la IA ajustar el plan de forma inteligente.**

---

## 🎯 USO EN NUEVO ORQUESTADOR

El nuevo orquestador EDN360 usará este cuestionario para:

1. **Comparar con cuestionario inicial:**
   - Objetivo inicial vs objetivo actual
   - Progreso hacia la meta

2. **Detectar patrones:**
   - Baja adherencia → Simplificar plan
   - Alta adherencia + bajo progreso → Ajustar intensidad
   - Factores externos → Adaptar horarios/volumen

3. **Ajustar estrategia:**
   - Training: Intensidad, volumen, frecuencia
   - Nutrition: Calorías, macros, distribución

4. **Generar snapshot versionado:**
   - ClientContext actualizado con datos del followup
   - Nuevo snapshot inmutable
   - Nuevo plan derivado del snapshot

---

**FIN DEL DOCUMENTO - CUESTIONARIO DE SEGUIMIENTO**

**Autor:** AI Engineer  
**Fecha:** Enero 2025  
**Versión:** 1.0
