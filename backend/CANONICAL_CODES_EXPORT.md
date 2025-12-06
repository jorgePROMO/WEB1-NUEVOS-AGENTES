# 📦 LISTA CANÓNICA DE EXERCISE_CODES - BACKEND PRODUCTIVO

## 📊 Estadísticas
- **Total códigos únicos**: 1243
- **Formato**: Array de strings ordenados alfabéticamente
- **Fuente**: exercise_catalog_edn360.json (catálogo enriquecido actual)

## 📄 Archivos Generados

### 1. backend_canonical_codes.json
**Descripción**: Lista simple de todos los exercise_codes (array de strings)
**Uso**: Para cargar en E4 v2 como lista oficial
**Formato**:
```json
[
  "abdominal_capullo",
  "abdominal_con_giro_peso_corporal",
  ...
  "zancadas_caminando_peso_corporal"
]
```

### 2. backend_canonical_codes_detailed.json
**Descripción**: Lista detallada con metadata por ejercicio
**Uso**: Para referencia y debugging
**Formato**:
```json
[
  {
    "exercise_code": "press_banca_mancuernas",
    "name_es": "press banca mancuernas",
    "exercise_family": "horizontal_push",
    "primary_muscles": ["pectorales"]
  },
  ...
]
```

### 3. e4_v2_to_backend_mapping.json
**Descripción**: Mapeo de códigos actuales de E4 v2 → códigos backend
**Uso**: Referencia para realinear E4 v2
**Contenido**: 12 mappings sugeridos

## 🔍 Códigos Problemáticos Detectados

Los siguientes códigos que genera E4 v2 actualmente **NO existen** en el catálogo backend:

| Código E4 v2 | Sugerencia Backend |
|--------------|-------------------|
| `sentadilla_barra_high_bar` | `sentadilla_barra` |
| `prensa_piernas_maquina` | `prensa_pierna_45_maquina` |
| `zancada_mancuernas` | `zancada_con_mancuernas` |
| `press_polea_media` | `press_pecho_poleas_pie` |
| `curl_femorales_tumbado_maquina` | `curl_femoral_tumbado_maquina` |
| `extension_cuadriceps_maquina` | `extension_pierna_maquina` |
| `elevaciones_laterales_maquina_sentado` | `elevaciones_laterales_maquina` |
| `abduccion_cadera_maquina` | `abduccion_lateral_cadera_maquina` |
| `elevacion_gemelos_prensa` | `elevacion_gemelos_sentado_maquina` |
| `press_hombros_mancuernas_ligero` | `press_hombros_sentado_mancuernas` |
| `sentadilla_peso_corporal` | `sentadilla_basica_peso_corporal` |
| `puente_gluteo_suelo` | `puente_gluteo_una_pierna` |

## ✅ Códigos Que SÍ Coinciden

Los siguientes códigos del ejemplo de E4 v2 **SÍ existen** en backend:
- ✅ `press_banca_mancuernas`
- ✅ `press_inclinado_mancuernas`
- ✅ `aperturas_medias_poleas`
- ✅ `fondos_triceps_suelo`
- ✅ `curl_biceps_barra`
- ✅ `press_pallof_horizontal`
- ✅ `plancha_lateral`

**Ratio actual**: 7/19 códigos coinciden (37%)
**Objetivo**: 100% coincidencia tras realineación

## 🎯 Próximos Pasos

1. ✅ Enviar `backend_canonical_codes.json` a equipo E4 v2
2. ⏳ Realinear E4 v2 contra lista oficial backend
3. ⏳ Validar nuevo output de E4 v2
4. ✅ Backend ya preparado para nuevo formato (rir, tempo, descanso_segundos)

## 📍 Ubicación de Archivos

```
/app/backend/
├── backend_canonical_codes.json (41KB)
├── backend_canonical_codes_detailed.json (236KB)
└── e4_v2_to_backend_mapping.json (738B)
```

---

Generado: 2025-12-06
Backend: exercise_catalog_edn360.json (1243 ejercicios)
