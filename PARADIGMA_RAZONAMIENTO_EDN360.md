# CAMBIO DE PARADIGMA EN EDN360
## De Reglas Fijas a Razonamiento Experto

**Fecha:** 22 Noviembre 2025  
**Fase:** 1 (E2 y E4 - Núcleo Decisional)  
**Estado:** Implementado para validación

---

## 🎯 OBJETIVO DEL CAMBIO

Transformar EDN360 de un sistema basado en **reglas fijas y condicionales** a uno que **razona como un entrenador experto**, utilizando la base de conocimiento como guía contextual, no como manual de instrucciones.

---

## ❌ PARADIGMA ANTERIOR (Reglas Fijas)

### Ejemplo E2 - Evaluador de Capacidad:

```python
# ANTES: Lógica rígida codificada
def calcular_seg(cliente):
    seg_base = 10
    
    if cliente.lesion_activa_severa:
        seg_base -= 3
    if cliente.edad > 50:
        seg_base -= 1
    if cliente.imc > 30:
        seg_base -= 1
    if cliente.principiante:
        seg_base -= 1
    
    return max(seg_base, 2)

# Resultado: SEG = 6 (fórmula matemática)
```

**Problemas:**
- No considera contexto completo
- Penalizaciones arbitrarias
- Ignora experiencia técnica vs edad
- No distingue lesión mecánica vs estructural
- Resultado: número sin significado real

### Ejemplo E4 - Arquitecto del Mesociclo:

```python
# ANTES: Plantilla fija por nivel
if nivel == "intermedio":
    volumen_pecho = 12-16  # Tabla fija
    rir_base = 3-4
    
if objetivo == "perdida_grasa":
    volumen *= 0.7  # Factor genérico

# Resultado: Plan genérico sin adaptación
```

**Problemas:**
- Volumen de tabla sin considerar contexto
- No adapta a déficit calórico real
- Progresión lineal forzada (irreal)
- Ignora limitaciones clínicas
- Resultado: plantilla, no diseño personalizado

---

## ✅ NUEVO PARADIGMA (Razonamiento Experto)

### Ejemplo E2 - Evaluador con Razonamiento:

```
ENTRADA:
Cliente: Avanzado técnicamente, 8 meses inactivo, lumbalgia mecánica ocasional,
contexto laboral 70h/semana, objetivo dual hipertrofia + pérdida grasa.

RAZONAMIENTO INTERNO:

1. ANÁLISIS PERFIL:
"Cliente con 10 años experiencia culturismo, técnica excelente, memoria motriz intacta.
Parón 8 meses por lesión + COVID. Lumbalgia mecánica (no degenerativa), responde 
bien a movilidad. Contexto estresante (70h trabajo, 6-7h sueño)."

2. PRINCIPIOS EDN360 CONSULTADOS:
- Experiencia técnica > edad cronológica
- Re-acondicionamiento ≠ principiante
- Lesión mecánica ≠ lesión estructural
- Historial de adaptación indica resiliencia

3. DECISIÓN SEG:
"SEG 7.5/10
- No es 9 porque requiere precaución (parón + lumbalgia)
- No es 5 porque experiencia le protege
- 7.5 refleja capacidad REAL: puede progresar con gestión inteligente"

4. JUSTIFICACIÓN:
"La edad (38) es factor menor frente a 10 años experiencia. La lumbalgia es 
mecánica (hiperextensión), no estructural, manejable con selección biomecánica 
inteligente. El parón reduce capacidad actual, pero memoria muscular permite 
re-acondicionamiento acelerado (no tratarlo como principiante)."

SALIDA:
{
  "seg_score": 7.5,
  "interpretacion": "Alta experiencia técnica pero desacondicionamiento estructural...",
  "razonamiento_interno": {
    "analisis_perfil": "...",
    "principios_aplicados": [...],
    "decisiones_clave": {...},
    "justificaciones": {...}
  },
  "split_recomendado": "Upper-Lower espaciado (no estándar)",
  "rir_objetivo": "Progresivo 5→3→2 (re-acondicionamiento acelerado)",
  ...
}
```

**Ventajas:**
- ✅ Considera contexto completo
- ✅ Aplica principios fisiológicos, no fórmulas
- ✅ Distingue entre tipos de lesión
- ✅ Reconoce experiencia previa vs estado actual
- ✅ Resultado: evaluación con significado real

### Ejemplo E4 - Arquitecto con Razonamiento:

```
ENTRADA:
Cliente intermedio, objetivo dual (hipertrofia + pérdida grasa), déficit calórico,
70h trabajo, 6-7h sueño, 4 días disponibles, lumbalgia ocasional.

RAZONAMIENTO INTERNO:

1. ANÁLISIS CONTEXTO:
"Objetivo dual requiere volumen suficiente para mantener músculo. Déficit calórico 
limita recuperación (-15% vs mantenimiento). Contexto estresante (70h trabajo) 
impide acumulación lineal de fatiga. Lumbalgia requiere gestión de carga axial."

2. PRINCIPIOS EDN360:
- Hipertrofia en déficit: volumen moderado-alto, intensidad media (RIR 3-4)
- Gestión fatiga: ondulación > progresión lineal en contextos de estrés
- Periodización contextual: estructura debe permitir recuperación
- Especificidad objetivo dual: mantener músculo + crear déficit

3. DISEÑO MESOCICLO:
"ESTRUCTURA: Ondulado 80% → 100% → 105% → 65% (no lineal)
RAZÓN: Contexto estresante no permite acumulación lineal. Pico S3 seguido 
descarga S4 permite máximo estímulo sin romper recuperación.

VOLUMEN PECHO: 12 series
CÁLCULO: Base intermedio 12-16 × factor déficit 0.85 = 10-14 → elijo 12
RAZÓN: Punto medio que permite hipertrofia sin exceder recuperación en déficit.

VOLUMEN CUÁDRICEPS: 12 series (reducido)
CÁLCULO: Base 14-18 × déficit 0.85 = 12-15 → reduzco a 12 por lumbalgia
RAZÓN: Limitación lumbar requiere reducir carga axial.

VOLUMEN ISQUIOS: 13 series (aumentado)
RAZÓN: Compensar reducción quad + fortalecer cadena posterior protege lumbar.

RIR PATRÓN: 5 (S1) → 4 (S2) → 3/5 ondulado (S3) → 4-5 (S4)
RAZÓN: Progresión acelerada por memoria muscular, pero ondulación S3 gestiona 
fatiga. Déficit impide sostener RIR <3 sin riesgo."

4. VALIDACIÓN:
"COHERENCIA OBJETIVO: Volumen 12-14 series/grupo mantiene músculo en déficit.
SOSTENIBILIDAD: 90 series en 260 min es viable (3 min/serie).
GESTIÓN RIESGOS: Volumen quad reducido + isquio aumentado protege lumbar.
REALISMO: Progresión NO promete +5% carga semanal (irreal en déficit)."

SALIDA:
{
  "mesocycle": {
    "razonamiento_interno": {...},
    "fases": [
      {"semana": 1, "volumen_pct": 80, "rir": 5, "justificacion": "..."},
      {"semana": 2, "volumen_pct": 100, "rir": 4, "justificacion": "..."},
      {"semana": 3, "volumen_pct": 105, "rir": "3/5", "justificacion": "..."},
      {"semana": 4, "volumen_pct": 65, "rir": "4-5", "justificacion": "..."}
    ],
    "volumen_por_grupo": {
      "pecho": {"series": 12, "razon": "..."},
      "cuadriceps": {"series": 12, "razon": "reducido por lumbalgia"},
      "isquios": {"series": 13, "razon": "aumentado para proteger lumbar"}
    },
    ...
  }
}
```

**Ventajas:**
- ✅ Estructura adaptada a contexto (no plantilla)
- ✅ Volumen calculado contextualmente (no tabla)
- ✅ Progresión realista (ondulada, no lineal forzada)
- ✅ Integra limitaciones clínicas en diseño
- ✅ Resultado: mesociclo personalizado con lógica clara

---

## 📊 COMPARACIÓN DIRECTA

### Caso: Cliente avanzado con 8 meses de parón

| Aspecto | ANTES (Reglas) | DESPUÉS (Razonamiento) |
|---------|----------------|------------------------|
| **SEG** | 6 (fórmula: 10 - 1 edad - 3 parón) | 7.5 (experiencia protege, parón temporal) |
| **Clasificación** | Principiante (por parón) | Avanzado desacondicionado |
| **RIR inicial** | 5 permanente (principiante) | 5→3→2 progresivo (memoria muscular) |
| **Volumen** | Bajo (principiante) | Intermedio-alto (experiencia real) |
| **Split** | Full-body (estándar) | Upper-Lower espaciado (lumbalgia) |
| **Progresión** | Lenta (8 semanas adaptación) | Acelerada (4 semanas a capacidad) |

**Resultado:**
- ❌ ANTES: Plan subóptimo (lo trata como principiante)
- ✅ DESPUÉS: Plan óptimo (reconoce capacidad real)

---

## 🧩 ELEMENTOS CLAVE DEL NUEVO SISTEMA

### 1. Razonamiento Interno Explícito

Cada agente ahora incluye sección `razonamiento_interno`:

```json
{
  "razonamiento_interno": {
    "analisis_perfil": "Descripción detallada del cliente",
    "principios_kb_aplicados": [
      "Principio 1",
      "Principio 2"
    ],
    "decisiones_clave": {
      "seg": "Justificación SEG",
      "split": "Justificación split",
      "volumen": "Justificación volumen"
    },
    "justificaciones": {
      "coherencia_fisiologica": "...",
      "gestion_riesgos": "...",
      "realismo": "..."
    }
  }
}
```

### 2. Proceso Decisional Estandarizado

Todos los agentes siguen:

1. **ANALIZAR** contexto completo
2. **CONSULTAR** base EDN360 (principios, no recetas)
3. **EVALUAR** coherencia fisiológica
4. **DECIDIR** estrategia óptima
5. **JUSTIFICAR** internamente

### 3. Criterios Prioritarios

- **Coherencia** frente a automatismo
- **Adaptación** frente a plantilla
- **Prevención** frente a agresividad innecesaria
- **Realismo** frente a perfección teórica

### 4. Base de Conocimiento como GUÍA

- ❌ NO es manual de instrucciones
- ✅ ES conjunto de principios fisiológicos
- Los agentes **interpretan** principios, no ejecutan reglas

---

## 🚀 IMPLEMENTACIÓN FASE 1

### Agentes Transformados:

1. **E2 - Evaluador de Capacidad** ✅
   - Archivo: `e2_capacity_v2_reasoning.py`
   - Cambio: De fórmula SEG a análisis contextual
   - Validación: razonamiento_interno obligatorio

2. **E4 - Arquitecto del Mesociclo** ✅
   - Archivo: `e4_architect_v2_reasoning.py`
   - Cambio: De plantillas a diseño contextual
   - Validación: razonamiento_interno obligatorio

### Próximos Agentes (Fase 2):

3. **E1 - Analista del Atleta**
4. **E3 - Analista de Historial**
5. **E5 - Ingeniero de Sesiones**
6. **E6 - Técnico Clínico**
7. **E8 - Auditor** (validación de coherencia)

---

## ✅ VALIDACIÓN DEL CAMBIO

### Test Case: Usuario Jorge1

**Perfil:**
- Avanzado técnicamente (10 años experiencia)
- 8 meses inactivo
- Lumbalgia mecánica ocasional
- Contexto estresante (70h trabajo)
- Objetivo dual: hipertrofia + pérdida grasa

**Comparación Esperada:**

| Métrica | ANTES | DESPUÉS |
|---------|-------|---------|
| SEG | 5-6 (bajo por parón) | 7.5 (alto por experiencia) |
| Clasificación | Principiante | Avanzado desacondicionado |
| RIR S1 | 5 | 5 |
| RIR S2-3 | 5 | 3-4 |
| Volumen total | ~65 series | ~90 series |
| Progresión | Lenta (8 sem) | Acelerada (4 sem) |
| Adaptación lumbar | Prohibiciones genéricas | Selección biomecánica |

**Resultado:**
- Plan ANTES: Subóptimo (infraestima capacidad)
- Plan DESPUÉS: Óptimo (reconoce capacidad real)

---

## 📋 PRÓXIMOS PASOS

1. ✅ **Fase 1 completada:** E2 y E4 con razonamiento
2. **Validar con usuario real** (Jorge1)
3. **Comparar planes:** ANTES vs DESPUÉS
4. **Si validación exitosa:**
   - Escalar a E1, E3, E5, E6
   - Transformar E8 en validador de coherencia
5. **Iteración continua:** Mejorar prompts basándose en calidad del razonamiento

---

## 🎓 FILOSOFÍA DEL SISTEMA

> "EDN360 no debe ejecutar comandos.  
> Debe PENSAR como Jorge, DECIDIR como Jorge, ESCALAR el criterio de Jorge.  
> Un sistema con inteligencia, no uno que obedece checklists."

**Principio fundamental:**

```
RAZONA → DECIDE → JUSTIFICA
```

No:
```
IF condición → THEN acción
```

---

## 📊 MÉTRICAS DE ÉXITO

Un agente con razonamiento exitoso debe:

1. ✅ **Razonamiento explícito:** Cada decisión tiene justificación contextual
2. ✅ **Coherencia fisiológica:** Decisiones basadas en principios EDN360
3. ✅ **Gestión inteligente:** Riesgos gestionados contextualmente, no prohibiciones genéricas
4. ✅ **Realismo y adaptación:** Plan viable con contexto real del cliente

---

**Fecha de implementación:** 22 Noviembre 2025  
**Responsable:** Sistema EDN360  
**Estado:** En validación (Fase 1)
