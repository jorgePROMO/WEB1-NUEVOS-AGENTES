# 🔄 Sistema de Actualizaciones Automáticas - PWA

## ✅ ¿Cómo Funciona?

Tu aplicación ahora tiene un **sistema de actualización automática** que NO requiere que los usuarios hagan nada.

---

## 🚀 Actualización Automática

### Para tus Clientes (PWA Instalada):

1. **Abren la app** → Automáticamente chequea si hay nueva versión
2. **Si hay actualización** → Se descarga en segundo plano
3. **Aplicación automática** → Se aplica y recarga sola
4. **Sin intervención** → El usuario ni se entera

**Tiempo:** 2-5 segundos desde que abren la app

---

## 🔧 ¿Cómo Actualizar tu App?

### Cuando hagas cambios:

1. **Edita el código** (lo que sea)
2. **Actualiza la versión** en `/app/frontend/public/service-worker.js`:
   ```javascript
   const CACHE_VERSION = 'v1.0.1'; // Cambiar aquí
   ```
3. **Reinicia servicios**:
   ```bash
   sudo supervisorctl restart frontend
   ```
4. **¡Listo!** Los clientes recibirán la actualización automáticamente

---

## 📊 Estrategia de Caché Inteligente

### Network First (Siempre fresco):
- ✅ **API calls** (`/api/*`) → Siempre datos actualizados
- ✅ **HTML pages** → Siempre la última versión
- ✅ **Respuestas del servidor** → Sin caché

### Cache First (Rendimiento):
- ✅ **Imágenes** → Se cachean para rapidez
- ✅ **CSS/JS** → Se cachean pero se actualizan en segundo plano
- ✅ **Iconos/Logos** → Permanecen cacheados

---

## ⏱️ Frecuencia de Actualización

- **Chequeo automático:** Cada 60 segundos mientras la app está abierta
- **Al abrir la app:** Chequeo inmediato
- **Detección:** Instantánea cuando hay nueva versión
- **Aplicación:** 2 segundos después de detectar cambios

---

## 🎯 Versionado Semántico

Usa este formato para versiones:

```
v1.0.0 → Versión inicial
v1.0.1 → Pequeños cambios (bugs, textos)
v1.1.0 → Nueva funcionalidad menor
v2.0.0 → Cambio mayor / Rediseño
```

**Ejemplo:**
- Cambias un color → `v1.0.1`
- Añades GPT informe → `v1.1.0`
- Rediseñas todo → `v2.0.0`

---

## 📱 Experiencia del Usuario

### Escenario 1: Usuario con app instalada
1. Abre la app (puede estar offline)
2. App carga instantáneamente (desde caché)
3. En segundo plano chequea actualizaciones
4. Si hay nueva versión:
   - Se descarga silenciosamente
   - Se aplica automáticamente
   - Recarga la app (2 segundos)
5. Usuario ve la nueva versión

### Escenario 2: Usuario sin conexión
1. Abre la app
2. Funciona completamente (todo cacheado)
3. Al recuperar conexión, se actualiza automáticamente

---

## 🔍 Logs para Depuración

En la consola del navegador verás:

```
✅ PWA: Service Worker registrado
🔄 Nueva versión detectada, actualizando...
✨ Nueva versión lista
🔄 Service Worker actualizado, recargando...
```

Para ver logs:
1. F12 → Consola
2. Buscar mensajes con emoji

---

## 🛠️ Comandos Útiles

### Ver versión actual del Service Worker:
```javascript
navigator.serviceWorker.getRegistration().then(reg => {
  console.log('Versión actual:', reg.active);
});
```

### Forzar actualización manual:
```javascript
navigator.serviceWorker.getRegistration().then(reg => {
  reg.update();
});
```

### Limpiar caché (desarrollo):
```javascript
caches.keys().then(keys => {
  keys.forEach(key => caches.delete(key));
});
```

---

## ⚠️ Importante: Cambiar Versión

**SIEMPRE** que hagas un cambio importante, actualiza la versión:

```javascript
// En: /app/frontend/public/service-worker.js
const CACHE_VERSION = 'v1.0.X'; // ← Incrementar aquí
```

**Si no cambias la versión**, los usuarios no recibirán la actualización.

---

## 🎉 Ventajas de este Sistema

✅ **Cero fricción** - Usuarios no hacen nada
✅ **Siempre actualizado** - Máximo 60 segundos de delay
✅ **Funciona offline** - App sigue funcionando sin internet
✅ **Rápido** - Caché inteligente = carga instantánea
✅ **Automático** - No requiere app stores ni permisos

---

## 📞 Soporte

Si un usuario reporta que no ve cambios:

1. **Pídele que cierre y abra la app** (fuerza actualización)
2. **Espera 60 segundos** (chequeo automático)
3. **Si persiste:** Pídele que borre caché del navegador

En 99% de casos, se actualiza solo.

---

**Fecha de implementación:** 1 de Noviembre, 2025  
**Versión actual:** v1.0.0
