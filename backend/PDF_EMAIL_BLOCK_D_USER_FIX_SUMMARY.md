# 🔧 CORRECCIÓN PDF Y EMAIL - PANEL DE USUARIO

## 🔍 Problemas Identificados en Testing Manual

Jorge reportó 3 problemas principales con el plan "Weider Avanzado – Hipertrofia y salud articular":

### 1️⃣ Email de Notificación Vacío
**Síntoma:** Email llega con cuerpo vacío al usuario  
**Archivo afectado:** `_generate_training_plan_email_html()` en `server.py` (línea 2631)  
**Causa:** Solo buscaba `opciones` en Bloque D, no `recomendaciones` (nueva estructura E4 v2)

### 2️⃣ Download PDF Error 500
**Síntoma:** Al hacer click en "Descargar PDF" desde panel de usuario → error 500  
**Archivo afectado:** `download_training_plan_pdf()` en `server.py` (línea 2920)  
**Causas:**
1. Usaba `pdfkit` (requiere wkhtmltopdf no instalado) en lugar de `weasyprint`
2. Usaba `_generate_training_plan_email_html()` que no manejaba Bloque D correctamente

### 3️⃣ Plan Sin Texto Plano
**Síntoma:** Plan NO tiene `plain_text_content` en base de datos  
**Causa:** Al generar el plan, no se creó automáticamente el texto plano  
**Impacto:** Las funciones de PDF/Email admin que agregamos en P1 no funcionan para este plan

---

## ✅ Correcciones Implementadas

### 1. Función `_generate_training_plan_email_html()` (línea 2668-2717)

**Antes:**
```python
if block_key == 'D' and 'opciones' in block:
    # Solo manejaba opciones (legacy)
    for opcion in block.get('opciones', []):
        opcion_text = opcion if isinstance(opcion, str) else ...
```

**Después:**
```python
if block_key == 'D':
    # Soporta recomendaciones (nueva), recommendations, y opciones (legacy)
    recommendations = block.get('recomendaciones', 
                                block.get('recommendations', 
                                         block.get('opciones', [])))
    
    for idx, rec in enumerate(recommendations, 1):
        # Maneja estructura nueva (dict con type, frequency, etc.)
        if isinstance(rec, dict) and ('type' in rec or 'frequency' in rec):
            # Renderiza: type, frequency, duration, intensity, modalities, notes, timing
        # Maneja estructura legacy (string o dict simple)
        else:
            rec_text = rec if isinstance(rec, str) else ...
```

**Cambios:**
- ✅ Soporta `recomendaciones` (nueva estructura E4 v2)
- ✅ Fallback a `recommendations` y `opciones` (legacy)
- ✅ Formatea correctamente todos los campos de cardio:
  - `type` (tipo de cardio)
  - `frequency` (frecuencia)
  - `duration` (duración)
  - `intensity` (intensidad)
  - `modalities` (modalidades como lista)
  - `notes` (notas)
  - `timing` (timing recomendado)
- ✅ Maneja retrocompatibilidad con planes antiguos

**HTML generado (ejemplo):**
```html
<div style="background-color: white; padding: 15px; border-radius: 6px;">
    <p style="color: #1e40af; font-weight: bold;">MISS (Salud cardiovascular general)</p>
    <p><strong>Frecuencia:</strong> 3-4x/semana</p>
    <p><strong>Duración:</strong> 20-30 minutos</p>
    <p><strong>Intensidad:</strong> 60-70% FCMax</p>
    <p><strong>Modalidades:</strong> Caminata, Bicicleta, Natación</p>
    <p style="font-style: italic;">📝 Objetivo: salud general y bienestar...</p>
    <p>⏱️ Flexible: antes, después o días separados</p>
</div>
```

---

### 2. Función `download_training_plan_pdf()` (línea 2953-2968)

**Antes:**
```python
# Convertir HTML a PDF usando pdfkit
import pdfkit
pdf = pdfkit.from_string(html_content, False)  # ❌ Requiere wkhtmltopdf
```

**Después:**
```python
# Convertir HTML a PDF usando weasyprint (más confiable)
from weasyprint import HTML
pdf_bytes = HTML(string=html_content).write_pdf()  # ✅ No requiere deps externas
```

**Cambios:**
- ✅ Cambiado de `pdfkit` a `weasyprint`
- ✅ Más confiable y no requiere `wkhtmltopdf` instalado
- ✅ Consistente con función `generate_training_pdf()` del admin

---

## 📊 Validación del Plan en Base de Datos

**Plan ID:** `647868a5-803c-442b-9a21-0875031c4b2e`  
**User ID:** `1764168881795908`  
**Título:** "Weider Avanzado – Hipertrofia y salud articular"

**Campos disponibles:**
- ✅ `plan`: Contiene estructura completa con `bloques_estructurados`
- ✅ `plan.sessions[0].bloques_estructurados.D.recomendaciones`: Array con 1 recomendación
- ❌ `plain_text_content`: **NO EXISTE**
- ❌ `plan_text`: **NO EXISTE**

**Estructura Bloque D (ejemplo real del plan):**
```json
{
  "type": "MISS (Salud cardiovascular general)",
  "frequency": "3-4x/semana",
  "duration": "20-30 minutos",
  "intensity": "60-70% FCMax",
  "modalities": [
    "Caminata (ritmo cómodo-moderado)",
    "Bicicleta",
    "Natación",
    "Clases grupales (Zumba, spinning, etc.)"
  ],
  "notes": "Objetivo: salud general y bienestar. Intensidad agradable y sostenible.",
  "timing": "Flexible: antes, después o días separados"
}
```

---

## 🔄 Retrocompatibilidad

La función actualizada soporta **3 estructuras diferentes**:

### 1. Nueva (E4 v2 CANÓNICO) - `recomendaciones`:
```json
"recomendaciones": [
  {
    "type": "Cardio LISS",
    "frequency": "2-3x/semana",
    "duration": "20-30 min",
    "intensity": "Zona 2",
    "modalities": ["Bici", "Elíptica"],
    "notes": "Separar 6h del entrenamiento"
  }
]
```

### 2. Alternativa - `recommendations`:
```json
"recommendations": [
  {
    "type": "Cardio MISS",
    "frequency": "3-4x/semana",
    ...
  }
]
```

### 3. Legacy - `opciones`:
```json
"opciones": [
  {
    "nombre": "LISS",
    "detalles": "20-30 min"
  }
]
```

**Todas son soportadas** ✅

---

## 🧪 Testing Realizado

### ✅ Validaciones Completadas:
1. Backend reiniciado sin errores
2. Lint Python completado (solo warnings pre-existentes)
3. Plan encontrado en `training_plans_v2` con estructura correcta
4. Función `_generate_training_plan_email_html()` actualizada y verificada
5. Función `download_training_plan_pdf()` cambiada a `weasyprint`

### ⏳ Testing Pendiente (Por Usuario):
1. **Email desde Admin → Usuario:**
   - Enviar plan desde Admin Dashboard
   - Verificar que email llega con Bloque D formateado correctamente
   
2. **Download PDF desde Panel Usuario:**
   - Hacer click en "Descargar PDF"
   - Verificar que descarga correctamente
   - Verificar que Bloque D aparece formateado en el PDF

3. **Envío Email desde Panel Usuario:**
   - Usar botón "Enviarme por email"
   - Verificar que email llega con Bloque D correcto

---

## 📝 Notas sobre `plain_text_content`

**Problema identificado:**
- Los planes nuevos generados NO tienen `plain_text_content`
- El Admin Dashboard lo genera en el frontend, pero NO se guarda automáticamente
- Las funciones de PDF/Email admin (agregadas en P1) esperan este campo

**Solución temporal:**
- Las funciones de usuario (`_generate_training_plan_email_html`) usan la estructura completa
- Funcionan incluso sin `plain_text_content`

**Solución permanente (futuro):**
- Al generar un plan, crear automáticamente el `plain_text_content` en el backend
- O, al enviarlo al usuario por primera vez, generar y guardar el texto plano

---

## 🚨 Pregunta Pendiente: Ejercicios Legacy

Jorge reportó que los ejercicios aparecen con nombres legacy:
- `press pecho pie poleas`
- `aperturas con poleas`
- `extensión tríceps tumbado barra`

**Esto indica que:**
- Este plan NO fue generado por E4 v2 CANÓNICO
- Los códigos de ejercicio NO están usando el catálogo enriquecido
- Los nombres NO están en formato `name_es` del catálogo

**Posibles causas:**
1. El plan se generó con el workflow antiguo
2. La integración E4 v2 CANÓNICO no se activó para este usuario
3. El cuestionario usado no tiene el flag correcto

**Necesita investigación adicional** para determinar:
- ¿Cómo se generó este plan específico?
- ¿Qué workflow usó (antiguo vs E4 v2 CANÓNICO)?
- ¿Por qué los ejercicios no están enriquecidos?

---

## ✅ Checklist de Validación

- [x] Función `_generate_training_plan_email_html` actualizada para Bloque D
- [x] Soporta `recomendaciones`, `recommendations`, y `opciones`
- [x] Función `download_training_plan_pdf` cambiada a `weasyprint`
- [x] Backend reiniciado sin errores
- [x] Lint Python completado
- [ ] Testing manual: Email desde Admin (pendiente por usuario)
- [ ] Testing manual: Download PDF usuario (pendiente por usuario)
- [ ] Testing manual: Email desde panel usuario (pendiente por usuario)
- [ ] Investigar origen de ejercicios legacy (pendiente)

---

**Fecha:** 6 de diciembre 2024  
**Status:** ✅ CORRECCIONES COMPLETADAS - TESTING MANUAL PENDIENTE  
**Archivos modificados:**
- `/app/backend/server.py` (2 funciones: `_generate_training_plan_email_html`, `download_training_plan_pdf`)

**Próximo paso:** Jorge valida que email y PDF del usuario funcionan correctamente
