# CUESTIONARIO INICIAL - Variables y Estructura Completa

**Documento:** Especificación técnica del cuestionario inicial EDN360  
**Fecha:** Enero 2025  
**Colección MongoDB:** `nutrition_questionnaire_submissions` (BD Web)  
**Tipo:** Cuestionario único que cubre TRAINING + NUTRITION  

---

## 📋 ESTRUCTURA GENERAL

```javascript
{
  _id: string,                    // ID único del cuestionario
  user_id: string,                // ID del usuario en BD Web
  responses: { ... },             // Objeto con todas las respuestas
  submitted_at: datetime,         // Fecha y hora de envío
  plan_generated: boolean,        // Si se generó plan (legacy)
  plan_id: string                 // ID del plan generado (legacy)
}
```

---

## 🔍 SECCIONES DEL CUESTIONARIO

**⚠️ IMPORTANTE:** El cuestionario inicial tiene campos dinámicos según la selección de `measurement_type` (báscula inteligente, cinta métrica, o sin herramientas).

### 1. DATOS PERSONALES

#### 1.1. Identificación Básica

| Variable | Tipo | Pregunta/Descripción | Ejemplo | Requerido |
|----------|------|---------------------|---------|-----------|
| `nombre_completo` | string | Nombre completo del cliente | "Jorge1" | ✅ Sí |
| `email` | string | Email de contacto | "jorge31011987promo@gmail.com" | ✅ Sí |
| `fecha_nacimiento` | date | Fecha de nacimiento (formato: YYYY-MM-DD) | "1987-01-31" | ✅ Sí |
| `sexo` | string | Sexo biológico | "HOMBRE" / "MUJER" | ✅ Sí |
| `profesion` | string | Profesión u ocupación | "Fontanero" | ✅ Sí |
| `direccion` | string | Dirección completa | "Calle Helsinki 7, piso 8, puerta 1" | ⚠️ Opcional |
| `telefono` | string | Teléfono de contacto | "669080819" | ✅ Sí |

---

### 2. TIPO DE MEDICIÓN

**⚠️ CAMPO CRÍTICO:** Esta pregunta determina qué campos de medición estarán disponibles.

| Variable | Tipo | Pregunta | Opciones | Requerido |
|----------|------|---------|---------|-----------|
| `measurement_type` | string | ¿Cómo vas a medirte? | "smart_scale" / "tape_measure" / "none" | ✅ Sí |

**Opciones disponibles:**

1. **"smart_scale"** - ⚖️ Báscula inteligente
   - Con datos de % grasa, % músculo, % agua, masa ósea, grasa visceral, etc.
   
2. **"tape_measure"** - 📏 Báscula + Cinta métrica
   - Con circunferencias corporales (pecho, cintura, cadera, bíceps, muslo)
   
3. **"none"** - ❌ No tengo cómo medirme
   - Solo peso y altura estimados

**Impacto:** Los campos de medición disponibles cambian según esta selección (ver sección 2.1 a 2.4).

---

### 2.1. MEDIDAS ANTROPOMÉTRICAS - Comunes (Todos los tipos)

Estos campos están disponibles independientemente del `measurement_type`:

| Variable | Tipo | Pregunta | Unidad | Requerido |
|----------|------|---------|--------|-----------|
| `peso` | string/number | Peso corporal actual | kg | ✅ Sí |
| `altura_cm` | string/number | Altura | cm | ✅ Sí |

---

### 2.2. MEDIDAS - Báscula Inteligente (measurement_type = "smart_scale")

Cuando el usuario selecciona **báscula inteligente**, estos campos están disponibles:

| Variable | Tipo | Pregunta | Unidad | Ejemplo | Requerido |
|----------|------|---------|--------|---------|-----------|
| `peso` | string/number | Peso | kg | "85" | ✅ Sí |
| `altura_cm` | string/number | Altura | cm | "172" | ✅ Sí |
| `grasa_porcentaje` | string/number | % Grasa Corporal | % | "28" | ✅ Sí |
| `masa_muscular_porcentaje` | string/number | % Masa Muscular | % | "35" | ⚠️ Opcional |
| `masa_osea_kg` | string/number | Masa Ósea | kg | "3.2" | ⚠️ Opcional |
| `agua_porcentaje` | string/number | % Agua Corporal | % | "55" | ⚠️ Opcional |
| `grasa_visceral` | string/number | Grasa Visceral | nivel | "9" | ⚠️ Opcional |

**Nota:** Los campos de circunferencias quedan en `null` o no se envían.

---

### 2.3. MEDIDAS - Cinta Métrica (measurement_type = "tape_measure")

Cuando el usuario selecciona **báscula + cinta métrica**, estos campos están disponibles:

| Variable | Tipo | Pregunta | Unidad | Requerido |
|----------|------|---------|--------|-----------|
| `peso` | string/number | Peso | kg | ✅ Sí |
| `altura_cm` | string/number | Altura | cm | ✅ Sí |
| `pecho_cm` | string/number | Circunferencia de Pecho | cm | ⚠️ Opcional |
| `cintura_cm` | string/number | Circunferencia de Cintura | cm | ✅ Sí |
| `cadera_cm` | string/number | Circunferencia de Cadera | cm | ✅ Sí |
| `biceps_relajado_cm` | string/number | Circunferencia de Bíceps Relajado | cm | ⚠️ Opcional |
| `biceps_flexionado_cm` | string/number | Circunferencia de Bíceps Flexionado | cm | ⚠️ Opcional |
| `muslo_cm` | string/number | Circunferencia de Muslo | cm | ⚠️ Opcional |

**Nota:** Los campos de báscula inteligente (grasa_porcentaje, masa_muscular, etc.) quedan en `null` o no se envían.

---

### 2.4. MEDIDAS - Sin Herramientas (measurement_type = "none")

Cuando el usuario selecciona **no tengo cómo medirme**, solo estos campos están disponibles:

| Variable | Tipo | Pregunta | Unidad | Requerido |
|----------|------|---------|--------|-----------|
| `peso` | string/number | Peso estimado | kg | ✅ Sí |
| `altura_cm` | string/number | Altura | cm | ✅ Sí |

**Nota:** Todos los demás campos de medición quedan en `null` o no se envían.

---

### 3. SALUD Y MEDICACIÓN

#### 3.1. Medicamentos y Enfermedades Crónicas

| Variable | Tipo | Pregunta | Ejemplo | Requerido |
|----------|------|---------|---------|-----------|
| `medicamentos` | string | ¿Tomas algún medicamento regularmente? | "Eutirox75" | ⚠️ Opcional |
| `enfermedad_cronica` | string | ¿Tienes alguna enfermedad crónica? | "Hipotiroidismo" | ⚠️ Opcional |

#### 3.2. Hábitos de Salud

| Variable | Tipo | Pregunta | Opciones/Ejemplo | Requerido |
|----------|------|---------|------------------|-----------|
| `fuma_cantidad` | string | ¿Fumas? ¿Cuánto? | "No" / "Vapeo" / "10 cigarrillos/día" | ✅ Sí |
| `bebe_cantidad` | string | ¿Bebes alcohol? ¿Cuánto? | "No" / "5 cervezas a la semana" | ✅ Sí |

#### 3.3. Condiciones de Salud (Sí/No)

Todas las siguientes variables son de tipo **string** con valores "Sí" / "No" / texto descriptivo:

| Variable | Pregunta | Ejemplo |
|----------|----------|---------|
| `retencion_liquidos` | ¿Tienes retención de líquidos? | "No" |
| `problemas_corazon` | ¿Tienes problemas cardíacos? | "No" |
| `hipertension` | ¿Tienes hipertensión? | "No" |
| `diabetes` | ¿Tienes diabetes? | "No" |
| `colesterol` | ¿Tienes colesterol alto? | "No" |
| `sobrepeso` | ¿Tienes sobrepeso diagnosticado? | "No" |
| `epilepsia` | ¿Tienes epilepsia? | "No" |
| `alergias_intolerancias` | ¿Tienes alergias o intolerancias alimentarias? | "No" |
| `problema_ejercicio` | ¿Algún problema que impida hacer ejercicio? | "No" |
| `operaciones` | ¿Has tenido operaciones recientes? | "No" |
| `embarazo` | ¿Estás embarazada? (solo mujeres) | "No" |
| `problemas_respiratorios` | ¿Tienes problemas respiratorios? | "No" |
| `problemas_musculares` | ¿Tienes problemas musculares? | "Manguito rotador de los 2 hombros" |
| `varo_valgo` | ¿Tienes varo o valgo en rodillas? | "No" |
| `hernias_protusiones` | ¿Tienes hernias o protrusiones? | "L4-L5" |
| `artrosis` | ¿Tienes artrosis? | "No" |
| `menopausia` | ¿Estás en menopausia? (solo mujeres) | "No" |
| `osteoporosis` | ¿Tienes osteoporosis? | "No" |

**Nota:** Cuando la respuesta es "Sí", el usuario puede especificar detalles adicionales.

---

### 4. TRABAJO Y ACTIVIDAD DIARIA

#### 4.1. Características del Trabajo

| Variable | Tipo | Pregunta | Opciones/Ejemplo | Requerido |
|----------|------|---------|------------------|-----------|
| `estres_profesion` | string | Nivel de estrés en tu profesión | "Nada" / "Poco" / "Normal" / "Mucho" / "Demasiado" | ✅ Sí |
| `movimiento_trabajo` | string | Nivel de movimiento en tu trabajo | "Nada" / "Poco" / "Normal" / "Mucho" / "Demasiado" | ✅ Sí |
| `dia_trabajo` | string | Describe un día típico de trabajo | "Chapuzas a domicilio" | ✅ Sí |
| `descansa_trabajo` | string | ¿Puedes descansar durante el trabajo? | "Sí" / "No" | ✅ Sí |
| `horas_trabajo` | string/number | Horas de trabajo al día | "10" | ✅ Sí |

#### 4.2. Actividad Física Diaria

| Variable | Tipo | Pregunta | Opciones/Ejemplo | Requerido |
|----------|------|---------|------------------|-----------|
| `actividad_fisica_diaria` | string | Nivel de actividad física diaria | "Sedentario" / "Poco activo" / "Activo" / "Muy activo" | ✅ Sí |
| `trabajo_fisicamente` | string | ¿Tu trabajo es físicamente demandante? | "No" / "Sí, moderado" / "Sí, intenso" | ✅ Sí |
| `horas_ocio_semana` | string/number | Horas de ocio a la semana | "3" | ✅ Sí |
| `tipo_persona` | string | ¿Qué tipo de persona eres? | "Muy activo/a" / "Activo/a" / "Poco activo/a" / "Sedentario/a" | ✅ Sí |

---

### 5. EXPERIENCIA DEPORTIVA

#### 5.1. Historial Deportivo

| Variable | Tipo | Pregunta | Opciones/Ejemplo | Requerido |
|----------|------|---------|------------------|-----------|
| `practicado_deporte` | string | ¿Has practicado deporte alguna vez? | "Sí" / "No" | ✅ Sí |
| `experiencia_negativa` | string | ¿Has tenido alguna experiencia negativa con el deporte? | "Sí" / "No" + descripción | ⚠️ Opcional |
| `constante_deporte` | string | ¿Has sido constante con el deporte? | "Sí" / "No" / "A veces" | ✅ Sí |
| `tiempo_dedicaba` | string | ¿Cuánto tiempo dedicabas al deporte? | "3h al día, 5 días a la semana" | ⚠️ Opcional |
| `nivel_deporte` | string | ¿Cuál era tu nivel? | "Principiante" / "Intermedio" / "Avanzado" / "Profesional" | ⚠️ Opcional |

#### 5.2. Experiencia en Gimnasio

| Variable | Tipo | Pregunta | Opciones/Ejemplo | Requerido |
|----------|------|---------|------------------|-----------|
| `entrenado_gimnasio` | string | ¿Has entrenado en gimnasio? | "Sí" / "No" | ✅ Sí |
| `entrenador_personal` | string | ¿Has tenido entrenador personal? | "Sí" / "No" | ⚠️ Opcional |

#### 5.3. Capacidades Físicas Actuales

| Variable | Tipo | Pregunta | Opciones | Requerido |
|----------|------|---------|---------|-----------|
| `resistencia_cardiorespiratoria` | string | Tu resistencia cardiorrespiratoria es... | "Nula" / "Baja" / "Media" / "Alta" / "Muy alta" | ✅ Sí |
| `fuerza` | string | Tu fuerza es... | "Nula" / "Baja" / "Media" / "Alta" / "Muy alta" | ✅ Sí |
| `flexibilidad` | string | Tu flexibilidad es... | "Nula" / "Baja" / "Media" / "Alta" / "Muy alta" | ✅ Sí |
| `agilidad_coordinacion` | string | Tu agilidad y coordinación es... | "Nula" / "Baja" / "Media" / "Alta" / "Muy alta" | ✅ Sí |

---

### 6. DISPONIBILIDAD Y PREFERENCIAS DE ENTRENAMIENTO

#### 6.1. Disponibilidad Temporal

| Variable | Tipo | Pregunta | Opciones/Ejemplo | Requerido |
|----------|------|---------|------------------|-----------|
| `dias_semana_entrenar` | string | ¿Cuántos días a la semana puedes entrenar? | "1-2" / "3-4" / "5-6" / "7" | ✅ Sí |
| `tiempo_sesion` | string | ¿Cuánto tiempo por sesión? | "30 min" / "45 min" / "60 min" / "90 min" / "120 min" | ✅ Sí |
| `entrena_manana_tarde` | string | Prefieres entrenar por la... | "Mañana" / "Tarde" / "Noche" / "Me da igual" | ✅ Sí |

#### 6.2. Lugar y Material

| Variable | Tipo | Pregunta | Opciones/Ejemplo | Requerido |
|----------|------|---------|------------------|-----------|
| `gimnasio` | string | ¿Tienes acceso a gimnasio? | "Sí" / "No" | ✅ Sí |
| `material_casa` | string | ¿Qué material tienes en casa? | "Nada" / "Mancuernas" / "Bandas elásticas" / "Barra y discos" / etc. | ✅ Sí |
| `actividades_realizar` | string | ¿Qué actividades prefieres realizar? | "pesas y máquinas de gimnasio" / "running" / "natación" / etc. | ✅ Sí |

#### 6.3. Características Personales

| Variable | Tipo | Pregunta | Opciones/Ejemplo | Requerido |
|----------|------|---------|------------------|-----------|
| `cuesta_coger_peso` | string | ¿Te cuesta coger peso/músculo? | "Sí" / "No" / "No lo sé" | ✅ Sí |

#### 6.4. Motivaciones

| Variable | Tipo | Pregunta | Formato | Requerido |
|----------|------|---------|---------|-----------|
| `motivos_entrenar` | array | ¿Cuáles son tus motivos para entrenar? | Array de strings (múltiple selección) | ⚠️ Opcional |

**Opciones disponibles:**
- "Perder grasa"
- "Ganar músculo"
- "Mejorar salud"
- "Mejorar rendimiento deportivo"
- "Reducir estrés"
- "Mejorar imagen corporal"
- "Otro" (especificar)

---

### 7. HORARIOS DIARIOS

| Variable | Tipo | Pregunta | Formato | Ejemplo | Requerido |
|----------|------|---------|---------|---------|-----------|
| `hora_levanta` | time | ¿A qué hora te levantas? | HH:MM | "05:54" | ✅ Sí |
| `hora_desayuno` | time | ¿A qué hora desayunas? | HH:MM | "06:54" | ✅ Sí |
| `hora_almuerzo` | time | ¿A qué hora almuerzas (snack media mañana)? | HH:MM | "09:55" | ⚠️ Opcional |
| `hora_comida` | time | ¿A qué hora comes? | HH:MM | "13:55" | ✅ Sí |
| `hora_merienda` | time | ¿A qué hora meriendas? | HH:MM | "16:55" | ⚠️ Opcional |
| `hora_cena` | time | ¿A qué hora cenas? | HH:MM | "20:55" | ✅ Sí |
| `hora_acuesta` | time | ¿A qué hora te acuestas? | HH:MM | "22:55" | ✅ Sí |

#### 7.1. Sueño

| Variable | Tipo | Pregunta | Opciones/Ejemplo | Requerido |
|----------|------|---------|------------------|-----------|
| `horas_duerme` | string | ¿Cuántas horas duermes? | "4-5" / "6-7" / "8-9" / "10+" | ✅ Sí |

---

### 8. HÁBITOS ALIMENTARIOS

#### 8.1. Patrón de Comidas

| Variable | Tipo | Pregunta | Opciones/Ejemplo | Requerido |
|----------|------|---------|------------------|-----------|
| `comidas_dia` | string | ¿Cuántas comidas haces al día? | "2" / "3" / "4" / "5" / "6" / "Más de 6" | ✅ Sí |
| `comidas_fuertes_ligeras` | string | ¿Qué comidas son fuertes y cuáles ligeras? | "Fuertes comida, el resto ligeras" | ✅ Sí |

#### 8.2. Preferencias y Restricciones

| Variable | Tipo | Pregunta | Ejemplo | Requerido |
|----------|------|---------|---------|-----------|
| `alimento_no_soporta` | string | ¿Hay alimentos que no soportas? | "Coliflor, patata y cerdo" | ⚠️ Opcional |
| `comida_favorita` | string | ¿Cuál es tu comida favorita? | "paella y canelones" | ⚠️ Opcional |

#### 8.3. Frecuencia de Consumo

| Variable | Tipo | Pregunta | Opciones/Ejemplo | Requerido |
|----------|------|---------|------------------|-----------|
| `comida_basura_frecuencia` | string | ¿Con qué frecuencia comes comida basura? | "Nunca" / "1-2 veces/semana" / "3-4 veces/semana" / "A diario" | ✅ Sí |
| `come_fuera_casa` | string | ¿Comes fuera de casa frecuentemente? | "Nunca" / "A veces" / "A menudo" / "Siempre" | ✅ Sí |
| `azucar_dulces_bolleria` | string | ¿Consumes azúcar, dulces o bollería? | "Nunca" / "A veces" / "A menudo" / "A diario" | ✅ Sí |
| `anade_sal` | string | ¿Añades sal a las comidas? | "No" / "Sí, poco" / "Sí, normal" / "Sí, mucho" | ✅ Sí |
| `bebidas_gas` | string | ¿Bebes bebidas con gas/azucaradas? | "Nunca" / "A veces" / "A menudo" / "A diario" | ✅ Sí |

#### 8.4. Historial de Dietas

| Variable | Tipo | Pregunta | Ejemplo | Requerido |
|----------|------|---------|---------|-----------|
| `dietas_anteriores` | string | ¿Has hecho dietas anteriormente? ¿Cuáles? ¿Resultado? | "Keto y me fue genial" | ⚠️ Opcional |

#### 8.5. Suplementación

| Variable | Tipo | Pregunta | Ejemplo | Requerido |
|----------|------|---------|---------|-----------|
| `sustancias_alteran` | string | ¿Tomas sustancias que alteren el metabolismo? | "Eutirox 75" | ⚠️ Opcional |
| `suplementacion` | string | ¿Tomas algún suplemento? | "proteína, creatina y magnesio" | ⚠️ Opcional |

---

### 9. OBJETIVOS Y MOTIVACIÓN

#### 9.1. Objetivo Principal

| Variable | Tipo | Pregunta | Opciones/Ejemplo | Requerido |
|----------|------|---------|------------------|-----------|
| `objetivo_fisico` | string | ¿Cuál es tu objetivo físico principal? | "Perder grasa" / "Ganar músculo" / "Definición" / "Mantener" / "Rendimiento" | ✅ Sí |

#### 9.2. Contexto de Experiencia

| Variable | Tipo | Pregunta | Ejemplo | Requerido |
|----------|------|---------|---------|-----------|
| `experiencia_ejercicio_constante` | string | ¿Has hecho ejercicio de forma constante? Cuéntame tu experiencia | "He sido culturista profesional" | ✅ Sí |
| `impedido_constancia` | string | ¿Qué te ha impedido ser constante? | "Aumento de trabajo y he sido padre" | ⚠️ Opcional |

#### 9.3. Motivación

| Variable | Tipo | Pregunta | Ejemplo | Requerido |
|----------|------|---------|---------|-----------|
| `motiva_ejercicio` | string | ¿Qué te motiva a hacer ejercicio? | "que siempre me ha gustado verme grande y definido" | ✅ Sí |

#### 9.4. Energía General

| Variable | Tipo | Pregunta | Opciones | Requerido |
|----------|------|---------|---------|-----------|
| `nivel_energia_dia` | string | ¿Cómo es tu nivel de energía durante el día? | "Muy bajo" / "Bajo" / "Medio" / "Alto" / "Muy alto" | ✅ Sí |

---

### 10. COMENTARIOS ADICIONALES

| Variable | Tipo | Pregunta | Formato | Requerido |
|----------|------|---------|---------|-----------|
| `comentarios_adicionales` | string | ¿Algo más que quieras contarnos? | Texto libre (textarea) | ⚠️ Opcional |

---

## 📊 RESUMEN DE VARIABLES

### Por Tipo de Dato

| Tipo | Cantidad | Variables |
|------|----------|-----------|
| **string** | ~85 | La mayoría de campos |
| **date** | 1 | `fecha_nacimiento` |
| **time** | 7 | `hora_levanta`, `hora_desayuno`, `hora_almuerzo`, `hora_comida`, `hora_merienda`, `hora_cena`, `hora_acuesta` |
| **array** | 1 | `motivos_entrenar` |
| **boolean** | 2 | `plan_generated` (metadato), otras implícitas como "Sí"/"No" |

### Por Obligatoriedad

| Tipo | Cantidad Aproximada |
|------|---------------------|
| **Requerido** | ~50 campos |
| **Opcional** | ~35 campos |

### Por Sección

| Sección | Variables | Requeridas | Opcionales |
|---------|-----------|------------|------------|
| **Datos Personales** | 7 | 5-6 | 1-2 |
| **Tipo de Medición** | 1 | 1 | 0 |

---

## 🔧 NOTAS TÉCNICAS

### 1. Validación de Datos

- **Email:** Validación de formato email válido
- **Fecha de nacimiento:** Formato YYYY-MM-DD
- **Horarios:** Formato HH:MM (24 horas)
- **Números:** Peso, altura, porcentajes - validación numérica
- **Opciones múltiples:** Valores predefinidos estrictos

### 2. Campos Condicionales

Algunos campos solo se muestran/validan según el sexo:
- `embarazo` → Solo mujeres
- `menopausia` → Solo mujeres

### 3. Campos con Especificación

Cuando el usuario responde "Sí" a ciertas preguntas, puede especificar detalles:
- `problemas_musculares` → "Manguito rotador de los 2 hombros"
- `hernias_protusiones` → "L4-L5"
- `dietas_anteriores` → "Keto y me fue genial"

### 4. Almacenamiento en MongoDB

```javascript
{
  _id: string,
  user_id: string,
  responses: {
    // TODAS las variables del cuestionario aquí
    nombre_completo: string,
    email: string,
    // ... (85+ campos)
  },
  submitted_at: ISODate,
  plan_generated: boolean,
  plan_id: string
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
        submission_id: "1762977457211469",  // ID en BD Web
        submitted_at: ISODate,
        source: "initial",
        raw_payload: { /* responses completas */ }
      }
    ]
  }
}
```

---

## 📋 EJEMPLO COMPLETO DE CUESTIONARIO

```javascript
{
  "_id": "1762977457211469",
  "user_id": "1762976907472415",
  "responses": {
    "nombre_completo": "Jorge1",
    "email": "jorge31011987promo@gmail.com",
    "fecha_nacimiento": "1987-01-31",
    "sexo": "HOMBRE",
    "profesion": "Fontanero",
    "direccion": "Calle Helsinki 7, piso 8, puerta 1",
    "telefono": "669080819",
    "peso": "85",
    "altura_cm": "172",
    "grasa_porcentaje": "28",
    "cintura_cm": "",
    "cadera_cm": "",
    "biceps_relajado_cm": "",
    "biceps_flexionado_cm": "",
    "muslo_cm": "",
    "medicamentos": "Eutirox75",
    "enfermedad_cronica": "Hipotiroidismo",
    "fuma_cantidad": "Vapeo",
    "bebe_cantidad": "5 cervezas a la semana",
    "retencion_liquidos": "No",
    "problemas_corazon": "No",
    "hipertension": "No",
    "diabetes": "No",
    "colesterol": "No",
    "sobrepeso": "No",
    "epilepsia": "No",
    "alergias_intolerancias": "No",
    "problema_ejercicio": "No",
    "operaciones": "No",
    "embarazo": "No",
    "problemas_respiratorios": "No",
    "problemas_musculares": "Manguito rotador de los 2 hombros",
    "varo_valgo": "No",
    "hernias_protusiones": "L4-L5",
    "artrosis": "No",
    "menopausia": "No",
    "osteoporosis": "No",
    "estres_profesion": "Mucho",
    "movimiento_trabajo": "Mucho",
    "dia_trabajo": "Chapuzas a domicilio",
    "descansa_trabajo": "No",
    "horas_trabajo": "10",
    "actividad_fisica_diaria": "Muy activo",
    "trabajo_fisicamente": "Sí, intenso",
    "horas_ocio_semana": "3",
    "practicado_deporte": "Sí",
    "experiencia_negativa": "No",
    "constante_deporte": "Sí",
    "tiempo_dedicaba": "3h al día, 5 días a la semana",
    "nivel_deporte": "Avanzado",
    "entrenado_gimnasio": "Sí",
    "entrenador_personal": "No",
    "resistencia_cardiorespiratoria": "Baja",
    "fuerza": "Alta",
    "flexibilidad": "Media",
    "agilidad_coordinacion": "Media",
    "dias_semana_entrenar": "3-4",
    "tiempo_sesion": "60 min",
    "entrena_manana_tarde": "Mañana",
    "gimnasio": "Sí",
    "material_casa": "Nada",
    "actividades_realizar": "pesas y máquinas de gimnasio",
    "tipo_persona": "Muy activo/a",
    "cuesta_coger_peso": "No",
    "motivos_entrenar": [],
    "hora_levanta": "05:54",
    "hora_desayuno": "06:54",
    "hora_almuerzo": "09:55",
    "hora_comida": "13:55",
    "hora_merienda": "16:55",
    "hora_cena": "20:55",
    "hora_acuesta": "22:55",
    "horas_duerme": "6-7",
    "comidas_dia": "4",
    "comidas_fuertes_ligeras": "Fuertes comida, el resto ligeras",
    "alimento_no_soporta": "Coliflor, patata y cerdo",
    "comida_favorita": "paella y canelones",
    "comida_basura_frecuencia": "1-2 veces/semana",
    "dietas_anteriores": "Keto y me fue genial",
    "sustancias_alteran": "Eutirox 75",
    "suplementacion": "proteína, creatina y magnesio",
    "come_fuera_casa": "A veces",
    "azucar_dulces_bolleria": "A veces",
    "anade_sal": "Sí, mucho",
    "bebidas_gas": "A veces",
    "objetivo_fisico": "Perder grasa",
    "experiencia_ejercicio_constante": "He sido culturista profesional",
    "impedido_constancia": "Aumento de trabajo y he sido padre",
    "motiva_ejercicio": "que siempre me ha gustado verme grande y definido",
    "nivel_energia_dia": "Medio",
    "comentarios_adicionales": ""
  },
  "submitted_at": "2025-11-12 19:57:37.211000",
  "plan_generated": true,
  "plan_id": "1763496790805117"
}
```

---

**FIN DEL DOCUMENTO - CUESTIONARIO INICIAL**

**Autor:** AI Engineer  
**Fecha:** Enero 2025  
**Versión:** 1.0
