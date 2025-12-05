# FORMATO DEFINITIVO DEL CATÁLOGO DE EJERCICIOS EDN360 v2.0

**Fecha:** 2025-12-05  
**Estado:** APROBADO por Jorge  
**Versión:** DEFINITIVA

---

## ✅ FORMATO JSON OFICIAL

```json
{
  "metadata": {
    "version": "2.0.0",
    "fecha_creacion": "YYYY-MM-DD",
    "descripcion": "Catálogo oficial de ejercicios EDN360"
  },
  "ejercicios": [
    {
      "id": "string_unico_slug",
      "nombre": "Nombre Legible del Ejercicio",
      "patrones": ["patron_1", "patron_2"],
      "tipos": ["tipo_1"],
      "nivel_recomendado": ["principiante", "intermedio", "avanzado"],
      "grupo_muscular_principal": ["musculo_1", "musculo_2"],
      "grupo_muscular_secundario": ["musculo_3"],
      "url_video": "https://...",
      "instrucciones": "Descripción de ejecución",
      "precauciones": ["precaucion_1", "precaucion_2"],
      "equipo_necesario": ["equipo_1", "equipo_2"],
      "contexto_apropiado": ["gym_completo", "home_gym_basico"],
      "tags_adicionales": ["tag_1", "tag_2"]
    }
  ]
}
```

---

## 🔒 REGLAS CRÍTICAS

### 1. CAMPO `patrones` - TAXONOMÍA ESTRICTA

**⚠️ IMPORTANTE:** El campo `patrones` DEBE seguir EXACTAMENTE la taxonomía del K1.

**Valores ÚNICOS permitidos:**
- `empuje_horizontal`
- `empuje_vertical`
- `tiron_horizontal`
- `tiron_vertical`
- `dominante_rodilla`
- `dominante_cadera`
- `zancada`
- `core_antirotacion`
- `core_antiextension`
- `core_antiflexion`
- `core_rotacional`

❌ **NO INVENTAR** nuevos patrones  
❌ **NO USAR** variaciones o sinónimos  
✅ **USAR SOLO** los valores exactos de arriba

### 2. CAMPO `tipos` - TAXONOMÍA ESTRICTA

**Valores permitidos:**
- `compuesto_alta_demanda`
- `compuesto_media_demanda`
- `aislamiento`
- `correctivo_estabilidad`
- `pliometrico`
- `balistico`
- `metabolico_circuito`

### 3. CAMPO `id` - FORMATO

- Slug único: lowercase, sin espacios, sin caracteres especiales
- Usar guiones bajos `_` como separador
- Ejemplos: `press_banca_barra`, `sentadilla_goblet`, `crunch_abdominal`

### 4. CAMPO `url_video` - URLS OFICIALES

- Solo URLs de videos oficiales proporcionados por Jorge
- NO buscar videos externos
- NO generar URLs
- Formato válido: `https://...` o `null` si no hay video aún

### 5. CAMPO `equipo_necesario` - VALORES

**Valores permitidos:**
- `barra`
- `mancuernas`
- `kettlebell`
- `maquina`
- `cables`
- `bandas`
- `peso_corporal`
- `trx`
- `banco`
- `rack`
- `otros`

### 6. CAMPO `contexto_apropiado` - VALORES

**Valores permitidos:**
- `gym_completo`
- `home_gym_basico`
- `minimo_equipo`
- `exterior`

---

## 📝 EJEMPLO COMPLETO

```json
{
  "metadata": {
    "version": "2.0.0",
    "fecha_creacion": "2025-12-05",
    "descripcion": "Catálogo oficial EDN360 - Compatible con K1"
  },
  "ejercicios": [
    {
      "id": "press_banca_barra",
      "nombre": "Press de Banca con Barra",
      "patrones": ["empuje_horizontal"],
      "tipos": ["compuesto_alta_demanda"],
      "nivel_recomendado": ["principiante", "intermedio", "avanzado"],
      "grupo_muscular_principal": ["pecho", "triceps"],
      "grupo_muscular_secundario": ["hombro_anterior"],
      "url_video": "https://www.youtube.com/watch?v=EJEMPLO_OFICIAL",
      "instrucciones": "Acostado en banco plano, bajar barra al pecho controladamente, empujar hacia arriba manteniendo escápulas retraídas.",
      "precauciones": [
        "Requiere rack de seguridad",
        "No recomendado con lesiones de hombro agudas"
      ],
      "equipo_necesario": ["barra", "banco", "rack"],
      "contexto_apropiado": ["gym_completo"],
      "tags_adicionales": ["basico", "fuerza", "hipertrofia", "tren_superior"]
    }
  ]
}
```

---

## ✅ VALIDACIÓN

El sistema validará automáticamente:
1. ✅ Que `patrones` solo contenga valores de la taxonomía K1
2. ✅ Que `tipos` solo contenga valores de la taxonomía K1
3. ✅ Que `id` sea un slug válido
4. ✅ Que `url_video` sea una URL válida o null
5. ✅ Que todos los campos requeridos estén presentes

---

## 🚀 CÓMO SERÁ USADO

1. **E4** consultará el catálogo y seleccionará ejercicios por `id`
2. **Backend** enriquecerá con `nombre`, `url_video`, `instrucciones`
3. **Frontend** mostrará toda la información al usuario final

---

**ESTE ES EL FORMATO DEFINITIVO APROBADO.**  
Jorge: puedes proceder a crear tu catálogo usando este formato.
