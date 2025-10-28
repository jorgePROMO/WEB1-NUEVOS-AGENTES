# 📋 Cuestionario con Google Sheets - Opciones de Implementación

## ✅ Funcionalidad de Eliminar Documentos - COMPLETADA

### 👤 USUARIOS:
- ✅ Ven lista de "Mis Documentos Subidos" en tab Perfil
- ✅ Botón "Eliminar" en cada documento que subieron
- ✅ Confirmación antes de eliminar
- ✅ Actualización automática tras eliminar

### 👨‍💼 ADMIN:
- ✅ Botón eliminar (🗑️) en documentos enviados (azul)
- ✅ Botón eliminar (🗑️) en documentos recibidos (verde)
- ✅ Botón descargar en todos los documentos
- ✅ Confirmación antes de eliminar

---

## 📋 CUESTIONARIO CON GOOGLE SHEETS - 3 OPCIONES

### **OPCIÓN 1: Google Forms (MÁS FÁCIL Y RÁPIDA)** ⭐ RECOMENDADA

**Ventajas:**
- ✅ Sin programación adicional
- ✅ Google crea la hoja automáticamente
- ✅ Respuestas organizadas en tiempo real
- ✅ Puedes editar preguntas fácilmente
- ✅ Visualización de estadísticas automática

**Cómo funciona:**
1. Creas el cuestionario en Google Forms
2. Google Forms guarda automáticamente en Google Sheets
3. Te doy el link del formulario
4. Lo incrustamos en el modal de tu web

**Implementación:** 5 minutos
```javascript
// Solo necesitas darme la URL del Google Form
const questionnaireUrl = "https://docs.google.com/forms/d/e/TU_FORM_ID/viewform";
```

---

### **OPCIÓN 2: Cuestionario Personalizado en React + Google Sheets API** 💻

**Ventajas:**
- ✅ Diseño 100% personalizado con tus colores
- ✅ Control total sobre la experiencia del usuario
- ✅ Puedes agregar lógica condicional (mostrar preguntas según respuestas previas)
- ✅ Validaciones personalizadas
- ✅ Integración perfecta con tu landing

**Desventajas:**
- ⚠️ Requiere configurar Google Sheets API
- ⚠️ Requiere credenciales de Google Cloud
- ⚠️ Más tiempo de implementación

**Pasos necesarios:**
1. Crear proyecto en Google Cloud Console
2. Activar Google Sheets API
3. Crear credenciales (OAuth 2.0 o Service Account)
4. Programar el formulario en React
5. Conectar con Google Sheets API

**Tiempo de implementación:** 2-3 horas
**Costo:** Gratis (Google Sheets API tiene límites generosos)

---

### **OPCIÓN 3: Cuestionario en React + Google Apps Script** 🔧

**Ventajas:**
- ✅ Sin necesidad de credenciales complejas
- ✅ Diseño personalizado
- ✅ Más simple que la Opción 2
- ✅ Funciona mediante webhook

**Cómo funciona:**
1. Creo el formulario en React con tu diseño
2. Creas un Google Apps Script (te doy el código)
3. El formulario envía datos al script
4. El script los guarda en tu Google Sheet

**Tiempo de implementación:** 1-2 horas

---

## 🎯 MI RECOMENDACIÓN

### Para empezar AHORA mismo: **OPCIÓN 1 (Google Forms)**
- Es la más rápida
- Funciona perfecto
- Las respuestas van automáticamente a Sheets
- Se ve profesional en el modal

### Para diseño 100% personalizado más adelante: **OPCIÓN 3**
- Cuando tengas más tiempo
- Diseño totalmente a tu gusto
- Mantiene la misma funcionalidad

---

## 📝 INFORMACIÓN QUE NECESITO DE TI

Para cualquiera de las opciones, necesito saber:

### 1. **Preguntas del Cuestionario**
Dime qué preguntas quieres incluir. Por ejemplo:
- Nombre completo
- Email
- Edad
- Objetivo principal (perder peso, ganar músculo, etc.)
- Nivel de actividad física actual
- ¿Tienes alguna lesión o condición médica?
- etc.

### 2. **¿Qué opción prefieres?**
- Opción 1: Google Forms (rápido, funciona ya)
- Opción 2: Personalizado con API (más complejo)
- Opción 3: Personalizado con Apps Script (intermedio)

---

## 🚀 SI ELIGES OPCIÓN 1 (Google Forms)

**Lo que harías tú:**
1. Ve a https://forms.google.com
2. Crea un nuevo formulario
3. Agrega todas tus preguntas
4. Haz clic en "Respuestas" → Icono de Google Sheets → "Crear hoja de cálculo"
5. Copia el enlace del formulario (no de la hoja)
6. Me lo pasas

**Lo que hago yo:**
1. Tomo tu URL
2. La pongo en el código: `const questionnaireUrl = "TU_URL";`
3. Listo - funciona en el modal

**Tiempo total:** 15 minutos

---

## 💡 ALTERNATIVA: Typeform, JotForm, etc.

También puedo incrustar:
- Typeform (muy bonito visualmente)
- JotForm
- Microsoft Forms
- Cualquier servicio que tenga iframe

Todos estos también pueden conectarse con Google Sheets (con Zapier o similar).

---

## ❓ PREGUNTAS PARA TI

1. **¿Qué preguntas debe tener el cuestionario?** (o me pasas el PDF que mencionaste)

2. **¿Qué opción prefieres?**
   - [ ] Opción 1: Google Forms (rápido)
   - [ ] Opción 2: Personalizado con API
   - [ ] Opción 3: Personalizado con Script

3. **¿Quieres que te ayude a crear el Google Form ahora?** (si eliges Opción 1)

4. **¿Tienes preferencia de diseño/colores para el cuestionario?** (si eliges Opción 2 o 3)

---

## 🎨 VISTA PREVIA DEL MODAL

El modal que ya creé tiene estas dimensiones:
- **Ancho:** 100% (máximo 1280px en desktop)
- **Alto:** 90% de la pantalla
- **Responsive:** Se adapta a móvil y tablet
- **Botón cerrar:** X en la esquina superior derecha
- **Fondo:** Oscuro con blur elegante

Cualquier formulario que elijas se verá perfecto en este modal.

---

¿Qué opción prefieres y qué preguntas quieres en el cuestionario? 🚀
