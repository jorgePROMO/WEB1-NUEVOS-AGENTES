# 📦 LISTA CANÓNICA BACKEND - PARA E4 V2

## 📊 Información General
- **Total códigos**: 1243
- **Formato**: JSON array (lista simple de strings)
- **Fuente**: exercise_catalog_edn360.json (catálogo backend productivo)
- **Uso**: Cargar en E4 v2 para alineación 100%

## 📄 Archivo Principal

**backend_canonical_codes.json** (41KB)

Contiene un array JSON con los 1243 exercise_codes ordenados alfabéticamente:

```json
[
  "abdominal_capullo",
  "abdominal_con_giro_peso_corporal",
  ...
  "zancadas_caminando_peso_corporal"
]
```

## 🔍 Códigos Problemáticos Detectados (9)

Estos códigos están en E4 v2 actual pero NO en backend:

| # | Código E4 v2 Actual | Código Backend Correcto | Diferencia |
|---|---------------------|------------------------|------------|
| 1 | `press_hombros_mancuernas_ligero` | `press_hombros_sentado_mancuernas` | descriptor "ligero" |
| 2 | `press_polea_media` | `press_pecho_poleas_pie` | naming convention |
| 3 | `elevaciones_laterales_maquina_sentado` | `elevaciones_laterales_maquina` | descriptor "sentado" |
| 4 | `sentadilla_peso_corporal` | `sentadilla_basica_peso_corporal` | falta "basica" |
| 5 | `puente_gluteo_suelo` | `puente_gluteo_una_pierna` | especificidad |
| 6 | `curl_femorales_tumbado_maquina` | `curl_femoral_tumbado_maquina` | **plural vs singular** |
| 7 | `extension_cuadriceps_maquina` | `extension_pierna_maquina` | "cuadriceps" vs "pierna" |
| 8 | `abduccion_cadera_maquina` | `abduccion_lateral_cadera_maquina` | falta "lateral" |
| 9 | `elevacion_gemelos_prensa` | `elevacion_gemelos_sentado_maquina` | equipo diferente |

## ✅ Códigos Que SÍ Coinciden (10/19 del ejemplo)

Estos códigos del ejemplo E4 v2 YA están correctos:
- `aperturas_medias_poleas`
- `press_banca_mancuernas`
- `press_inclinado_mancuernas`
- `fondos_triceps_suelo`
- `curl_biceps_barra`
- `press_pallof_horizontal`
- `sentadilla_barra`
- `prensa_pierna_45_maquina`
- `zancada_con_mancuernas`
- `plancha_lateral`

## 🎯 Objetivo

**100% de los exercise_codes generados por E4 v2 deben estar en backend_canonical_codes.json**

- Sin excepciones
- Sin variaciones (plural/singular, descriptores adicionales, etc.)
- Matching exacto de strings

## 📥 Cómo Usar Este Archivo

1. Cargar `backend_canonical_codes.json` en E4 v2
2. Configurar E4 v2 para que SOLO use códigos de esta lista
3. Eliminar cualquier lista alternativa o mapeos intermedios
4. Validar que cada ejercicio generado existe en la lista
5. Generar nuevos JSONs de prueba
6. Enviar a backend para validación final

## 🔄 Status Actual

- ✅ **E4 v2 CANÓNICO 100% ALINEADO** (Validado el 6 de diciembre 2024)
- ✅ Mapeo temporal de 9 códigos **ELIMINADO** de server.py
- ✅ Archivo `temp_e4_v2_mappings.json` **ELIMINADO**
- ✅ Backend mantiene fuzzy matching solo para retrocompatibilidad con planes legacy
- 🎉 Sistema limpio y escalable

---

**Archivos Disponibles**:
- `backend_canonical_codes.json` - Lista canónica completa (1243 códigos)
- `backend_canonical_codes_detailed.json` - Con metadata (para referencia)
- ~~`temp_e4_v2_mappings.json`~~ - **ELIMINADO (ya no necesario)**
