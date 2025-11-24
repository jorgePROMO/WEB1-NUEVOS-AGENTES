# CORRECCIÓN - Cuestionario Inicial con measurement_type

**Fecha:** 24 Enero 2025  
**Solicitado por:** Jorge Calcerrada  
**Motivo:** Inclusión de campo crítico `measurement_type` no documentado

---

## ⚠️ CORRECCIÓN APLICADA

### Campo Faltante Identificado

**Variable:** `measurement_type`  
**Ubicación en cuestionario:** Sección 2 (antes de medidas antropométricas)  
**Tipo:** string  
**Requerido:** ✅ Sí  

### Pregunta en el Cuestionario

**"¿Cómo vas a medirte?"**

Selecciona el método que usarás para registrar tus medidas corporales:

---

## 📊 OPCIONES DE measurement_type

### 1. "smart_scale" - ⚖️ Báscula inteligente

**Descripción:** Con datos de % grasa, % músculo, % agua, masa ósea, grasa visceral, etc.

**Campos activos:**
- ✅ `peso` (kg) - Requerido
- ✅ `altura_cm` (cm) - Requerido
- ✅ `grasa_porcentaje` (%) - Requerido
- ⚠️ `masa_muscular_porcentaje` (%) - Opcional
- ⚠️ `masa_osea_kg` (kg) - Opcional
- ⚠️ `agua_porcentaje` (%) - Opcional
- ⚠️ `grasa_visceral` (nivel) - Opcional

**Campos inactivos:** Todos los de cinta métrica (pecho, cintura, cadera, bíceps, muslo)

---

### 2. "tape_measure" - 📏 Báscula + Cinta métrica

**Descripción:** Con circunferencias corporales (pecho, cintura, cadera, bíceps, muslo)

**Campos activos:**
- ✅ `peso` (kg) - Requerido
- ✅ `altura_cm` (cm) - Requerido
- ⚠️ `pecho_cm` (cm) - Opcional
- ✅ `cintura_cm` (cm) - Requerido
- ✅ `cadera_cm` (cm) - Requerido
- ⚠️ `biceps_relajado_cm` (cm) - Opcional
- ⚠️ `biceps_flexionado_cm` (cm) - Opcional
- ⚠️ `muslo_cm` (cm) - Opcional

**Campos inactivos:** Todos los de báscula inteligente (grasa_porcentaje, masa_muscular, agua, etc.)

---

### 3. "none" - ❌ No tengo cómo medirme

**Descripción:** Solo proporcionaré peso y altura estimados

**Campos activos:**
- ✅ `peso` (kg estimado) - Requerido
- ✅ `altura_cm` (cm) - Requerido

**Campos inactivos:** Todos los demás campos de medición

---

## 🔍 IMPACTO EN EL CUESTIONARIO

### Estructura Actualizada

```javascript
{
  "_id": "1762977457211469",
  "user_id": "1762976907472415",
  "responses": {
    // ... datos personales ...
    
    // ⚠️ NUEVO CAMPO CRÍTICO
    "measurement_type": "smart_scale",  // o "tape_measure" o "none"
    
    // Campos dinámicos según measurement_type
    "peso": "85",
    "altura_cm": "172",
    // ... resto de medidas según tipo ...
    
    // ... resto del cuestionario ...
  },
  "submitted_at": "2025-11-12 19:57:37.211000",
  "plan_generated": true,
  "plan_id": "1763496790805117"
}
```

### Lógica de Validación

1. **Usuario selecciona measurement_type** (obligatorio)
2. **Frontend muestra campos dinámicamente:**
   - Si `smart_scale` → Muestra campos de porcentajes
   - Si `tape_measure` → Muestra campos de circunferencias
   - Si `none` → Solo muestra peso y altura
3. **Backend valida según tipo:**
   - Campos requeridos dependen de `measurement_type`
   - Campos no aplicables se ignoran o quedan en `null`

---

## 📄 DOCUMENTO ACTUALIZADO

**Archivo:** `/app/CUESTIONARIO_INICIAL_VARIABLES.md`

**Cambios aplicados:**

1. ✅ **Añadida sección 2:** "TIPO DE MEDICIÓN"
2. ✅ **Reorganizadas secciones 2.1 a 2.4:**
   - 2.1: Medidas Comunes (todos los tipos)
   - 2.2: Medidas Báscula Inteligente
   - 2.3: Medidas Cinta Métrica
   - 2.4: Medidas Sin Herramientas
3. ✅ **Actualizado resumen de variables:** +1 campo crítico
4. ✅ **Añadida sección de Notas Técnicas:** Explicación de campos dinámicos
5. ✅ **Actualizado ejemplo completo:** Incluye `measurement_type` con valores reales

---

## 📊 RESUMEN DE VARIABLES ACTUALIZADO

### Total de Variables

| Antes | Después | Diferencia |
|-------|---------|------------|
| ~85 variables | ~90 variables | +5 variables (measurement_type + variantes de medición) |

### Variables de Medición

| Tipo | Comunes | Específicas | Total |
|------|---------|-------------|-------|
| **smart_scale** | 2 (peso, altura) | 5 (grasa%, músculo%, agua%, masa_osea, grasa_visceral) | 7 |
| **tape_measure** | 2 (peso, altura) | 6 (pecho, cintura, cadera, bíceps x2, muslo) | 8 |
| **none** | 2 (peso, altura) | 0 | 2 |

---

## ✅ VALIDACIÓN

### Cuestionarios Existentes en BD

Los cuestionarios ya enviados pueden **NO tener** el campo `measurement_type` si fueron enviados antes de esta implementación.

**Estrategia de migración:**
- Cuestionarios sin `measurement_type` → Inferir según campos presentes:
  - Si tiene `grasa_porcentaje` → `measurement_type = "smart_scale"`
  - Si tiene `cintura_cm` y `cadera_cm` → `measurement_type = "tape_measure"`
  - Si solo tiene peso y altura → `measurement_type = "none"`

### Nuevos Cuestionarios

Todos los cuestionarios nuevos **DEBEN** incluir `measurement_type` como campo obligatorio.

---

## 🎯 PRÓXIMOS PASOS

### Para el Nuevo Orquestador

El nuevo orquestador EDN360 deberá:

1. **Leer `measurement_type` del cuestionario**
2. **Validar que los campos requeridos estén presentes:**
   - `smart_scale` → Requiere grasa_porcentaje
   - `tape_measure` → Requiere cintura_cm y cadera_cm
   - `none` → Solo peso y altura
3. **Ajustar análisis según datos disponibles:**
   - Con báscula inteligente → Análisis preciso de composición corporal
   - Con cinta métrica → Análisis de distribución de grasa
   - Sin herramientas → Análisis solo por peso/altura (menos preciso)

### Para la Arquitectura client_drawer

El campo `measurement_type` se almacenará en el `SharedQuestionnaire`:

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
        raw_payload: {
          measurement_type: "smart_scale",  // ⚠️ Campo crítico
          peso: "85",
          altura_cm: "172",
          grasa_porcentaje: "28",
          // ... resto de campos
        }
      }
    ]
  }
}
```

---

## 📝 CONCLUSIÓN

El campo `measurement_type` es **crítico** porque:

1. ✅ Determina qué medidas corporales están disponibles
2. ✅ Afecta a la validación de campos requeridos
3. ✅ Impacta en la precisión del análisis de composición corporal
4. ✅ Influye en las recomendaciones del orquestador

**El documento `CUESTIONARIO_INICIAL_VARIABLES.md` ha sido actualizado con esta información.**

---

**FIN DEL DOCUMENTO DE CORRECCIÓN**

**Autor:** AI Engineer  
**Fecha:** 24 Enero 2025  
**Estado:** ✅ Corregido y documentado
