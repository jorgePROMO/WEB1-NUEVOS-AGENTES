# INFORME FASE 2 COMPLETADA - Definición EDN360_INPUT

**Fecha:** 24 Enero 2025  
**Fase:** FASE 2 - Definición del contrato EDN360_INPUT  
**Estado:** ✅ COMPLETADA  
**Responsable:** AI Engineer  
**Solicitado por:** Jorge Calcerrada  

---

## 📋 RESUMEN EJECUTIVO

La FASE 2 (Definición EDN360_INPUT) ha sido **completada exitosamente**.

### ✅ OBJETIVOS CUMPLIDOS

1. ✅ **Modelo Pydantic EDN360Input definido** (contrato estándar)
2. ✅ **Builder implementado** (`build_edn360_input_for_user`)
3. ✅ **Endpoint admin creado** (`GET /api/admin/users/{user_id}/edn360-input-preview`)
4. ✅ **Frontend modificado** (botón "Ver EDN360 Input" + modal JSON viewer)
5. ✅ **Sin llamadas a OpenAI** (como se solicitó)
6. ✅ **Sin reactivación de generación de planes** (como se solicitó)
7. ✅ **Sin modificaciones de BD** (como se solicitó)

### 🎯 RESULTADO

Tenemos un **contrato estándar EDN360Input** que:
- ✅ Unifica perfil de usuario + cuestionarios
- ✅ Se construye desde BD Web + client_drawers
- ✅ Está listo para usarse con Workflows de OpenAI
- ✅ Es visible desde el panel admin (JSON completo)

---

## 📦 1. MODELO EDN360Input

### Archivo Creado

**Ruta:** `/app/backend/models/edn360_input.py` (~350 líneas)

### Estructura del Modelo

#### 1.1. EDN360UserProfile

```python
class EDN360UserProfile(BaseModel):
    """Perfil básico del usuario (BD Web)"""
    user_id: str
    name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    created_at: Optional[datetime]
    subscription_plan: Optional[str]  # team, pro, etc.
    subscription_status: Optional[str]  # verified, pending, etc.
```

**Fuente:** `test_database.users`

**Campos incluidos:**
- ✅ ID, nombre, email, teléfono
- ✅ Fecha de creación
- ✅ Plan de suscripción actual
- ✅ Estado del pago

#### 1.2. EDN360Questionnaire

```python
class EDN360Questionnaire(BaseModel):
    """Cuestionario individual (inicial o followup)"""
    submission_id: str  # ID en BD Web
    submitted_at: datetime
    source: str  # "nutrition_initial" | "followup"
    payload: Dict[str, Any]  # Contenido completo del cuestionario
```

**Fuente:** `edn360_app.client_drawers.services.shared_questionnaires`

**Campos incluidos:**
- ✅ `submission_id`: ID del cuestionario en BD Web
- ✅ `submitted_at`: Fecha de envío
- ✅ `source`: Tipo de cuestionario
  - `"nutrition_initial"`: Cuestionario inicial detallado
  - `"followup"`: Cuestionario de seguimiento mensual
  - `"prospect_initial"`: Cuestionario de prospección (futuro)
- ✅ `payload`: Documento completo del cuestionario (raw_payload)

#### 1.3. EDN360Input (Modelo Raíz)

```python
class EDN360Input(BaseModel):
    """
    Contrato estándar para Workflows de OpenAI.
    
    Fuentes:
    - user_profile: BD Web (test_database.users)
    - questionnaires: BD EDN360_APP (edn360_app.client_drawers)
    
    Orden de cuestionarios:
    - ASCENDENTE por submitted_at (más antiguo → más reciente)
    - Primer elemento: Cuestionario inicial
    - Siguientes: Followups mensuales
    """
    user_profile: EDN360UserProfile
    questionnaires: List[EDN360Questionnaire]
    generated_at: datetime  # Timestamp de generación
    version: str  # Versión del contrato (1.0.0)
```

### Métodos Helper

El modelo incluye métodos útiles:

```python
# Obtener cuestionario inicial
edn360_input.get_initial_questionnaire() -> Optional[EDN360Questionnaire]

# Obtener todos los followups
edn360_input.get_followup_questionnaires() -> List[EDN360Questionnaire]

# Obtener el más reciente
edn360_input.get_latest_questionnaire() -> Optional[EDN360Questionnaire]

# Contar cuestionarios
edn360_input.questionnaire_count() -> int

# Verificar si hay followups
edn360_input.has_followups() -> bool
```

### Excepciones Personalizadas

```python
class EDN360NoDrawerError(Exception):
    """Usuario no tiene client_drawer"""
    pass

class EDN360NoQuestionnaireError(Exception):
    """Drawer sin cuestionarios"""
    pass
```

---

## 🏗️ 2. BUILDER: build_edn360_input_for_user

### Archivo Creado

**Ruta:** `/app/backend/services/edn360_input_builder.py` (~250 líneas)

### Función Principal

```python
async def build_edn360_input_for_user(user_id: str) -> EDN360Input:
    """
    Construye el EDN360Input para un usuario.
    
    Proceso:
    1. Lee perfil de BD Web (test_database.users)
    2. Lee client_drawer de BD EDN360_APP (edn360_app.client_drawers)
    3. Mapea shared_questionnaires a EDN360Questionnaire
    4. Ordena cuestionarios cronológicamente (ASCENDENTE)
    5. Retorna EDN360Input completo
    """
```

### Origen de Datos

#### Paso 1: Perfil de Usuario (BD Web)

**Colección:** `test_database.users`

**Mapeo:**
```python
EDN360UserProfile(
    user_id=user_doc["_id"],
    name=user_doc.get("name"),
    email=user_doc.get("email"),
    phone=user_doc.get("phone"),
    created_at=user_doc.get("created_at"),
    subscription_plan=user_doc.get("subscription", {}).get("plan"),
    subscription_status=user_doc.get("subscription", {}).get("payment_status")
)
```

#### Paso 2: Client Drawer (BD EDN360_APP)

**Colección:** `edn360_app.client_drawers`

**Función usada:** `get_drawer_by_user_id(user_id)`

**Verifica:**
- ✅ Si no existe drawer → `EDN360NoDrawerError`
- ✅ Si drawer sin cuestionarios → Permite (questionnaires=[])

#### Paso 3: Mapeo de Cuestionarios

**Fuente:** `drawer.services.shared_questionnaires`

**Mapeo:**
```python
for sq in shared_questionnaires:
    questionnaire = EDN360Questionnaire(
        submission_id=sq.submission_id,
        submitted_at=sq.submitted_at,
        source=sq.source,
        payload=sq.raw_payload
    )
```

#### Paso 4: Ordenamiento de Cuestionarios

**Criterio:** Ordenados por `submitted_at` **ASCENDENTE**

```python
questionnaires.sort(key=lambda q: q.submitted_at)
```

**Orden final:**
1. Primer elemento: Cuestionario MÁS ANTIGUO (inicial)
2. Siguientes: Followups en orden cronológico
3. Último elemento: Cuestionario MÁS RECIENTE

**Ejemplo:**
```javascript
[
  {submission_id: "001", submitted_at: "2025-01-01", source: "nutrition_initial"},  // Inicial
  {submission_id: "002", submitted_at: "2025-02-01", source: "followup"},          // Followup 1
  {submission_id: "003", submitted_at: "2025-03-01", source: "followup"}           // Followup 2 (más reciente)
]
```

### Funciones Helper

**Validación:**
```python
await validate_edn360_input_for_user(user_id) -> tuple[bool, list[str]]
# Retorna (es_valido, lista_de_errores)
```

**Resumen:**
```python
await get_edn360_input_summary(user_id) -> dict
# Retorna resumen sin cargar todo el payload
# Útil para UI
```

### Logs Generados

```
🏗️  Construyendo EDN360Input para user_id: 1762976907472415
✅ Perfil de usuario cargado: Jorge1
✅ Client_drawer encontrado: client_1762976907472415
📋 Cuestionarios ordenados cronológicamente: 2 total
✅ EDN360Input construido exitosamente: 2 cuestionario(s)
```

---

## 🔌 3. ENDPOINT ADMIN

### Endpoint Creado

**Método:** `GET`  
**Ruta:** `/api/admin/users/{user_id}/edn360-input-preview`  
**Autenticación:** Requiere admin (header `Authorization: Bearer <token>`)

### Comportamiento

```python
@api_router.get("/admin/users/{user_id}/edn360-input-preview")
async def get_edn360_input_preview(user_id: str, request: Request):
    """
    Vista previa del EDN360Input para un usuario.
    
    FASE 2: Solo construye y devuelve el JSON.
    NO llama a ningún modelo de IA.
    """
    # 1. Verificar que es admin
    admin = await require_admin(request)
    
    # 2. Construir EDN360Input
    edn360_input = await build_edn360_input_for_user(user_id)
    
    # 3. Serializar y retornar
    return {
        "success": True,
        "user_id": user_id,
        "edn360_input": edn360_input.dict(),
        "metadata": { ... }
    }
```

### Respuestas

#### 200 OK - Éxito

```json
{
  "success": true,
  "user_id": "1762976907472415",
  "edn360_input": {
    "user_profile": {
      "user_id": "1762976907472415",
      "name": "Jorge1",
      "email": "jorge@example.com",
      "phone": "669080819",
      "created_at": "2025-01-10T12:00:00Z",
      "subscription_plan": "team",
      "subscription_status": "verified"
    },
    "questionnaires": [
      {
        "submission_id": "1762977457211469",
        "submitted_at": "2025-11-12T19:57:37.211000",
        "source": "nutrition_initial",
        "payload": { /* cuestionario completo */ }
      }
    ],
    "generated_at": "2025-01-24T15:30:00Z",
    "version": "1.0.0"
  },
  "metadata": {
    "questionnaires_count": 1,
    "has_initial": true,
    "has_followups": false,
    "generated_at": "2025-01-24T15:30:00Z",
    "version": "1.0.0"
  }
}
```

#### 404 Not Found - Sin drawer

```json
{
  "detail": {
    "error": "no_drawer",
    "message": "Usuario 1762... no tiene client_drawer. Esto puede ocurrir si el usuario nunca ha completado un cuestionario o si el dual-write no estaba activado cuando lo hizo.",
    "user_id": "1762976907472415"
  }
}
```

#### 404 Not Found - Sin cuestionarios

```json
{
  "detail": {
    "error": "no_questionnaires",
    "message": "Usuario 1762... tiene client_drawer pero sin cuestionarios",
    "user_id": "1762976907472415"
  }
}
```

#### 500 Internal Server Error

```json
{
  "detail": {
    "error": "internal_error",
    "message": "Error generando EDN360Input: <descripción del error>",
    "user_id": "1762976907472415"
  }
}
```

### Logs del Endpoint

```
✅ EDN360Input generado para user_id 1762976907472415: 1 cuestionario(s)
```

O en caso de error:
```
⚠️  No drawer para user_id 1762976907472415: Usuario no tiene client_drawer...
❌ Error generando EDN360Input para user_id 1762976907472415: <error>
```

---

## 🖥️ 4. FRONTEND - Panel Admin

### Cambios Realizados

**Archivo:** `/app/frontend/src/pages/AdminDashboard.jsx`

### 4.1. Estados Añadidos

```javascript
// EDN360 Input Preview - FASE 2
const [showEDN360InputModal, setShowEDN360InputModal] = useState(false);
const [edn360InputData, setEDN360InputData] = useState(null);
const [loadingEDN360Input, setLoadingEDN360Input] = useState(false);
```

### 4.2. Función de Manejo

```javascript
const handleViewEDN360Input = async (userId) => {
  setLoadingEDN360Input(true);
  setShowEDN360InputModal(true);
  setEDN360InputData(null);
  
  try {
    const response = await axios.get(
      `${API}/admin/users/${userId}/edn360-input-preview`,
      {
        headers: { Authorization: `Bearer ${token}` },
        withCredentials: true
      }
    );
    
    setEDN360InputData(response.data);
    console.log('✅ EDN360Input cargado:', response.data);
  } catch (error) {
    console.error('❌ Error cargando EDN360Input:', error);
    
    if (error.response?.status === 404) {
      alert(
        error.response?.data?.detail?.message || 
        'Este usuario no tiene client_drawer o no ha completado cuestionarios.'
      );
    } else {
      alert('Error al cargar EDN360Input. Ver consola para detalles.');
    }
    
    setShowEDN360InputModal(false);
  } finally {
    setLoadingEDN360Input(false);
  }
};
```

### 4.3. Botón "Ver EDN360 Input"

**Ubicación:** Panel de gestión de cliente, junto a botones "Editar", "Chat", "Templates"

**Estilo:** Color índigo (diferente de los demás botones)

```jsx
<Button
  size="sm"
  variant="outline"
  className="bg-indigo-50 border-indigo-300 text-indigo-700 hover:bg-indigo-100"
  onClick={() => handleViewEDN360Input(selectedClient.id)}
>
  <FileText className="h-4 w-4 mr-2" />
  Ver EDN360 Input
</Button>
```

**Captura visual:**
```
[Editar] [Chat] [Templates] [Ver EDN360 Input] [Verificar pago] ...
                              ^^^^^^^^^^^^^^^^
                              (Botón índigo nuevo)
```

### 4.4. Modal de Vista Previa

**Características:**

1. **Header:**
   - Título: "EDN360 Input Preview"
   - Icono FileText
   - Botón cerrar (X)
   - Fondo índigo

2. **Metadata Section:**
   - User ID
   - Número de cuestionarios
   - Tiene inicial (✅/❌)
   - Tiene followups (✅/❌)

3. **JSON Viewer:**
   - Fondo oscuro (terminal style)
   - Texto en verde (monospace)
   - Scroll vertical (max 500px)
   - Botón "📋 Copiar JSON"

4. **Info Box:**
   - Explicación de FASE 2
   - Indica que el JSON es para Workflows de OpenAI

**Estados del modal:**

**Cargando:**
```
┌─────────────────────────────────────┐
│  EDN360 Input Preview          ✕   │
├─────────────────────────────────────┤
│                                     │
│       [spinner animado]             │
│   Construyendo EDN360Input...       │
│                                     │
└─────────────────────────────────────┘
```

**Cargado (con datos):**
```
┌─────────────────────────────────────────────┐
│  EDN360 Input Preview                  ✕   │
├─────────────────────────────────────────────┤
│ 📊 Metadata                                 │
│ User ID: 1762...  Cuestionarios: 2         │
│ Inicial: ✅ Sí    Followups: ✅ Sí         │
│                                             │
│ 📄 EDN360Input JSON       [📋 Copiar JSON] │
│ ┌─────────────────────────────────────┐   │
│ │ {                                   │   │
│ │   "user_profile": { ... },          │   │
│ │   "questionnaires": [ ... ],        │   │
│ │   "generated_at": "...",            │   │
│ │   "version": "1.0.0"                │   │
│ │ }                                   │   │
│ └─────────────────────────────────────┘   │
│                                             │
│ ℹ️ FASE 2: Este JSON es el contrato...    │
└─────────────────────────────────────────────┘
```

**Error (sin drawer):**
```
Alert: Este usuario no tiene client_drawer o 
       no ha completado cuestionarios.

Modal se cierra automáticamente
```

### 4.5. Flujo de Usuario

1. Admin selecciona un cliente del listado
2. Admin ve el panel de gestión del cliente
3. Admin hace clic en "Ver EDN360 Input"
4. Se abre modal con spinner "Construyendo EDN360Input..."
5. Endpoint retorna JSON
6. Modal muestra metadata + JSON completo
7. Admin puede:
   - Copiar el JSON completo al portapapeles
   - Revisar el contenido
   - Cerrar el modal

---

## ✅ 5. CONFIRMACIONES

### 5.1. Modelo EDN360Input

- [x] Archivo `/app/backend/models/edn360_input.py` creado
- [x] Clase `EDN360UserProfile` con 7 campos
- [x] Clase `EDN360Questionnaire` con 4 campos
- [x] Clase `EDN360Input` con 4 campos + metadatos
- [x] Métodos helper implementados (5 métodos)
- [x] Excepciones personalizadas (2 excepciones)
- [x] Función de validación

### 5.2. Builder

- [x] Archivo `/app/backend/services/edn360_input_builder.py` creado
- [x] Función `build_edn360_input_for_user()` implementada
- [x] Lee de BD Web (`test_database.users`)
- [x] Lee de BD EDN360_APP (`edn360_app.client_drawers`)
- [x] Ordena cuestionarios por `submitted_at` ASCENDENTE
- [x] Maneja errores (sin drawer, sin cuestionarios)
- [x] Logs informativos

### 5.3. Endpoint Admin

- [x] Ruta: `GET /api/admin/users/{user_id}/edn360-input-preview`
- [x] Requiere autenticación admin
- [x] Retorna JSON completo del EDN360Input
- [x] Manejo de errores 404/500
- [x] Logs de éxito y error

### 5.4. Frontend

- [x] Botón "Ver EDN360 Input" añadido (color índigo)
- [x] Modal de vista previa implementado
- [x] Metadata visible (user ID, cuestionarios count, etc.)
- [x] JSON viewer con scroll
- [x] Botón "Copiar JSON"
- [x] Info box de FASE 2
- [x] Loading state (spinner)
- [x] Error handling (alerts)

### 5.5. Restricciones Cumplidas

- [x] NO se han hecho llamadas a OpenAI
- [x] NO se ha reactivado generación de planes
- [x] NO se han modificado colecciones de BD Web
- [x] NO se han creado datos nuevos en client_drawers (más allá de dual-write)
- [x] NO se ha tocado el job worker

---

## 📊 6. EJEMPLO DE EDN360Input COMPLETO

### Input de Usuario con 1 Cuestionario

```json
{
  "user_profile": {
    "user_id": "1762976907472415",
    "name": "Jorge1",
    "email": "jorge31011987promo@gmail.com",
    "phone": "669080819",
    "created_at": "2025-11-12T18:00:00Z",
    "subscription_plan": "team",
    "subscription_status": "verified"
  },
  "questionnaires": [
    {
      "submission_id": "1762977457211469",
      "submitted_at": "2025-11-12T19:57:37.211000",
      "source": "nutrition_initial",
      "payload": {
        "_id": "1762977457211469",
        "user_id": "1762976907472415",
        "responses": {
          "nombre_completo": "Jorge1",
          "email": "jorge31011987promo@gmail.com",
          "fecha_nacimiento": "1987-01-31",
          "sexo": "HOMBRE",
          "profesion": "Fontanero",
          "measurement_type": "smart_scale",
          "peso": "85",
          "altura_cm": "172",
          "grasa_porcentaje": "28",
          "objetivo_fisico": "Perder grasa",
          // ... resto de campos del cuestionario (90+ campos)
        },
        "submitted_at": "2025-11-12 19:57:37.211000",
        "plan_generated": true,
        "plan_id": "1763496790805117"
      }
    }
  ],
  "generated_at": "2025-01-24T15:30:00.123456",
  "version": "1.0.0"
}
```

### Input de Usuario con Inicial + 2 Followups

```json
{
  "user_profile": { /* ... */ },
  "questionnaires": [
    {
      "submission_id": "001",
      "submitted_at": "2025-01-01T10:00:00Z",
      "source": "nutrition_initial",
      "payload": { /* cuestionario inicial completo */ }
    },
    {
      "submission_id": "002",
      "submitted_at": "2025-02-01T10:00:00Z",
      "source": "followup",
      "payload": { /* primer followup */ }
    },
    {
      "submission_id": "003",
      "submitted_at": "2025-03-01T10:00:00Z",
      "source": "followup",
      "payload": { /* segundo followup */ }
    }
  ],
  "generated_at": "2025-01-24T15:30:00Z",
  "version": "1.0.0"
}
```

---

## 🎯 7. USO DEL EDN360Input

### Caso de Uso 1: Testing Manual de Workflows

**Flujo:**

1. Admin abre panel de cliente
2. Clic en "Ver EDN360 Input"
3. Copia el JSON completo
4. Abre OpenAI Workflows
5. Pega el JSON como input de test
6. Ejecuta Workflow E1, E2, ..., E9
7. Verifica outputs

### Caso de Uso 2: Validar Estructura de Datos

**Flujo:**

1. Verificar que cliente tiene cuestionarios
2. Ver EDN360 Input
3. Revisar metadata:
   - ¿Tiene cuestionario inicial?
   - ¿Tiene followups?
   - ¿Orden correcto?
4. Inspeccionar payload:
   - ¿Todos los campos presentes?
   - ¿Formato correcto?

### Caso de Uso 3: Debugging

**Flujo:**

1. Usuario reporta problema con su plan
2. Admin revisa EDN360 Input
3. Verifica qué datos tiene el sistema:
   - ¿Perfil completo?
   - ¿Cuestionarios correctos?
   - ¿Fechas coherentes?
4. Identifica si falta información
5. Solicita al usuario completar datos faltantes

---

## 📝 8. PRÓXIMOS PASOS (Fases Siguientes)

### FASE 3: Nuevo Orquestador

**Objetivo:** Implementar orquestador que use EDN360Input

**Tareas:**
1. Diseñar arquitectura del nuevo orquestador
2. Implementar lectura de EDN360Input
3. Llamar a Workflows de OpenAI con EDN360Input
4. Recibir ClientContext (outputs E1-E9, N0-N8)
5. Crear snapshots inmutables en client_drawers
6. Generar planes derivados de snapshots

### FASE 4: Integración con Workflows

**Objetivo:** Conectar orquestador con OpenAI Workflows

**Tareas:**
1. Configurar API de OpenAI Workflows
2. Implementar llamadas secuenciales (E1→E2→...→E9)
3. Manejar errores y reintentos
4. Almacenar outputs en snapshots
5. Validar integridad de ClientContext

### FASE 5: Reactivación de Generación

**Objetivo:** Reactivar generación de planes con nuevo sistema

**Tareas:**
1. Conectar endpoint de generación al nuevo orquestador
2. Probar generación end-to-end
3. Reactivar job worker con nuevo flujo
4. Reactivar botones frontend
5. Monitorear tasa de éxito

---

## ✅ 9. CHECKLIST DE CONFIRMACIÓN

### Modelo EDN360Input

- [x] `EDN360UserProfile` definido (7 campos)
- [x] `EDN360Questionnaire` definido (4 campos)
- [x] `EDN360Input` definido (4 campos)
- [x] Métodos helper (5 métodos)
- [x] Excepciones personalizadas
- [x] Validación implementada

### Builder

- [x] Función `build_edn360_input_for_user()` implementada
- [x] Lee BD Web (users)
- [x] Lee BD EDN360_APP (client_drawers)
- [x] Mapea cuestionarios correctamente
- [x] Ordena por fecha ASCENDENTE
- [x] Maneja errores (sin drawer, sin cuestionarios)
- [x] Logs informativos

### Endpoint Admin

- [x] Ruta definida: `GET /api/admin/users/{user_id}/edn360-input-preview`
- [x] Requiere admin
- [x] Retorna JSON completo
- [x] Metadata incluida
- [x] Manejo de errores 404/500
- [x] Logs de éxito/error

### Frontend

- [x] Botón "Ver EDN360 Input" añadido
- [x] Modal implementado
- [x] Metadata visible
- [x] JSON viewer con scroll
- [x] Botón copiar JSON
- [x] Info box FASE 2
- [x] Loading state
- [x] Error handling

### Restricciones

- [x] Sin llamadas a OpenAI
- [x] Sin reactivación de generación
- [x] Sin modificaciones de BD Web
- [x] Sin datos nuevos en client_drawers
- [x] Sin cambios en job worker

---

## 📝 10. RESUMEN FINAL

### Estado del Sistema: "Contrato EDN360Input Definido y Operativo"

La FASE 2 está **completada y operativa**:

✅ **DEFINIDO:**
- Modelo Pydantic EDN360Input (contrato estándar)
- Builder que construye desde BD Web + client_drawers
- Endpoint admin para vista previa
- Frontend con botón + modal JSON viewer

✅ **FUNCIONAL:**
- Admin puede ver EDN360Input de cualquier usuario
- JSON completo disponible para copiar
- Orden de cuestionarios consistente (ascendente)
- Metadata útil (count, has_initial, has_followups)

✅ **PREPARADO PARA:**
- Testing manual de Workflows de OpenAI
- Implementación del nuevo orquestador (FASE 3)
- Integración con Workflows E1-E9, N0-N8

### Próxima Acción Recomendada

**Opciones:**

1. **Testing manual con OpenAI Workflows:**
   - Copiar EDN360Input de un usuario real
   - Testear en OpenAI Workflows manualmente
   - Validar que el formato es correcto

2. **Iniciar FASE 3 (Nuevo Orquestador):**
   - Diseñar arquitectura del orquestador
   - Implementar llamadas a Workflows
   - Crear sistema de snapshots

3. **Documentar Workflows E1-E9:**
   - Definir inputs/outputs esperados
   - Crear tests de validación
   - Preparar prompts

---

**FIN DEL INFORME FASE 2**

**Autor:** AI Engineer  
**Fecha:** 24 Enero 2025  
**Estado:** ✅ COMPLETADA  
**Aprobación:** Pendiente Jorge Calcerrada
