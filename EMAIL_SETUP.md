# Configuración de Notificaciones por Email (Gmail)

## ¿Qué son las notificaciones por email?

El sistema ahora enviará correos automáticos a los clientes cuando:
1. Se les programa una nueva sesión/revisión
2. Se reagenda una sesión existente

## Cómo configurar Gmail para enviar notificaciones

### Paso 1: Obtener una contraseña de aplicación de Google

1. Ve a tu cuenta de Google: https://myaccount.google.com/
2. En el menú izquierdo, selecciona "Seguridad"
3. En "Cómo inicias sesión en Google", activa la "Verificación en dos pasos" (si aún no está activa)
4. Una vez activada la verificación en dos pasos, busca "Contraseñas de aplicaciones"
5. Selecciona "Correo" y "Otro (nombre personalizado)"
6. Escribe "Jorge Calcerrada App" como nombre
7. Haz clic en "Generar"
8. **Guarda la contraseña de 16 caracteres** que aparece (ejemplo: "abcd efgh ijkl mnop")

### Paso 2: Configurar las credenciales en tu aplicación

Necesitas editar el archivo `/app/backend/.env` y completar estos valores:

```env
SMTP_USER="tu-email@gmail.com"
SMTP_PASSWORD="tu-contraseña-de-aplicación-de-16-caracteres"
```

**Ejemplo:**
```env
SMTP_USER="jorge@example.com"
SMTP_PASSWORD="abcd efgh ijkl mnop"
```

### Paso 3: Reiniciar el backend

Después de configurar las credenciales, reinicia el backend para aplicar los cambios:

```bash
sudo supervisorctl restart backend
```

## Verificar que funciona

Cuando crees una sesión para un cliente desde el panel de administrador, el cliente debería recibir un email de notificación automáticamente.

## Notas importantes

- Las notificaciones solo se envían a los **clientes** (no al administrador)
- Si las credenciales de Gmail no están configuradas, las sesiones se crearán normalmente pero no se enviarán emails
- Los emails se envían desde tu cuenta de Gmail con el nombre "Jorge Calcerrada"
- Las contraseñas de aplicación son seguras y solo tienen acceso al correo (no a toda tu cuenta de Google)

## Troubleshooting

Si los emails no se envían:

1. Verifica que la verificación en dos pasos esté activa en tu cuenta de Google
2. Asegúrate de que la contraseña de aplicación está correctamente copiada (sin espacios extra)
3. Revisa los logs del backend: `tail -f /var/log/supervisor/backend.err.log`
