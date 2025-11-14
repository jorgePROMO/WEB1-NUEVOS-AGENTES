# Guía de Testing del Sistema E.D.N.360

## 📋 Pre-requisitos

1. ✅ Backend corriendo en puerto 8001
2. ✅ Frontend corriendo en puerto 3000
3. ✅ MongoDB activo
4. ✅ EMERGENT_LLM_KEY configurada en backend/.env

## 🧪 Tests de Backend (APIs)

### Test 1: Verificar que las APIs estén registradas

```bash
# Ver todas las rutas disponibles
curl -s http://localhost:8001/api/docs | grep -i edn360
```

### Test 2: Listar clientes (necesitas token)

```bash
# 1. Login como admin
curl -X POST "http://localhost:8001/api/auth/login?email=ecjtrainer@gmail.com&password=jorge3007" \
  -H "Content-Type: application/json"

# Guardar el token que recibes en la respuesta
TOKEN="tu_token_aqui"

# 2. Listar usuarios
curl -s "http://localhost:8001/api/admin/users" \
  -H "Authorization: Bearer $TOKEN" | jq
```

### Test 3: Generar Plan E.D.N.360 (REAL)

**IMPORTANTE:** Este test ejecutará los 18 agentes reales (tarda 2-4 minutos)

```bash
# Necesitas:
# - Un questionnaire_id válido
# - Un client_id válido
# - Token de admin

curl -X POST "http://localhost:8001/api/admin/edn360/generate-initial-plan" \
  -H "Authorization: Bearer $TOKEN" \
  -F "questionnaire_id=QUESTIONNAIRE_ID_AQUI" \
  -F "client_id=CLIENT_ID_AQUI" \
  -F "admin_notes=Test de generación de plan"
```

**Respuesta esperada:**
```json
{
  "success": true,
  "plan_id": "edn360_client123_1705320000",
  "status": "draft",
  "duration_seconds": 180.5,
  "validation": {
    "valid": true,
    "errors": [],
    "warnings": []
  }
}
```

### Test 4: Obtener Plan Generado

```bash
PLAN_ID="el_plan_id_que_recibiste"

curl -s "http://localhost:8001/api/admin/edn360/plans/$PLAN_ID" \
  -H "Authorization: Bearer $TOKEN" | jq
```

### Test 5: Chat para Modificar Plan

```bash
curl -X POST "http://localhost:8001/api/admin/edn360/plans/$PLAN_ID/chat" \
  -H "Authorization: Bearer $TOKEN" \
  -F "message=Reduce las series de press banca en 2"
```

### Test 6: Aprobar Plan

```bash
curl -X PUT "http://localhost:8001/api/admin/edn360/plans/$PLAN_ID/approve" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🎨 Tests de Frontend

### Test 1: Acceso al Dashboard Admin

1. Abre: https://aicoach-360.preview.emergentagent.com/admin
2. Login con credenciales de admin
3. Verifica que veas el tab **"E.D.N.360"** en el dashboard

### Test 2: Generar Plan desde UI

1. En el dashboard admin, clic en tab **"E.D.N.360"**
2. Tab **"Generar Plan"**
3. Selecciona un cliente del dropdown
4. Clic en **"Generar Plan Inicial"**
5. Espera 2-4 minutos
6. Verifica que aparezca un alert de éxito

### Test 3: Visualizar Plan Generado

1. Tab **"Planes Generados"**
2. Selecciona el mismo cliente
3. Deberías ver el plan con status "Borrador"
4. Clic en **"Ver Plan"**
5. Verifica que se muestre:
   - Perfil del cliente
   - Datos de entrenamiento (E1-E9)
   - Datos de nutrición (N0-N8)
   - Validaciones

### Test 4: Modificar Plan con Chat IA

1. Desde "Planes Generados", clic en **"Modificar"**
2. En el chat, escribe: "Reduce las series de sentadilla en 2"
3. Clic en enviar (icono de avión)
4. Espera respuesta de la IA
5. Verifica que se muestre la respuesta y cambios aplicados

### Test 5: Aprobar y Enviar Plan

1. Desde "Planes Generados", clic en **"Aprobar"**
2. Verifica que el badge cambie a "Aprobado"
3. Clic en **"Enviar"**
4. (Nota: Envío no implementado aún, mostrará mensaje)

---

## 🔍 Verificación de Logs

### Logs del Backend

```bash
# Ver logs en tiempo real
tail -f /var/log/supervisor/backend.out.log

# Ver solo los logs de E.D.N.360
tail -f /var/log/supervisor/backend.out.log | grep -E "E[1-9]|N[0-8]|ES[1-4]|NS[1-4]"

# Ver errores
tail -n 100 /var/log/supervisor/backend.err.log
```

### Logs del Frontend

```bash
# Ver compilación
tail -n 50 /var/log/supervisor/frontend.out.log

# Ver errores
tail -n 50 /var/log/supervisor/frontend.err.log
```

---

## ✅ Checklist de Validación

### Backend
- [ ] APIs registradas correctamente
- [ ] Orquestador puede ejecutarse
- [ ] Los 26 agentes están disponibles
- [ ] MongoDB conectado
- [ ] LLM Key configurada

### Frontend
- [ ] Tab E.D.N.360 visible en admin
- [ ] Dropdown de clientes funciona
- [ ] Botón "Generar Plan" funciona
- [ ] Chat de modificación funciona
- [ ] Visualización de planes funciona

### Sistema Completo
- [ ] Plan inicial se genera (2-4 min)
- [ ] Plan se guarda en MongoDB
- [ ] Chat modifica el plan
- [ ] Versionado funciona
- [ ] Validaciones se ejecutan

---

## 🐛 Troubleshooting

### Error: "EMERGENT_LLM_KEY no configurada"

**Solución:**
```bash
echo 'EMERGENT_LLM_KEY=tu_key_aqui' >> /app/backend/.env
sudo supervisorctl restart backend
```

### Error: "No module named 'edn360'"

**Solución:**
```bash
cd /app/backend
ls -la edn360/  # Verificar que existe
sudo supervisorctl restart backend
```

### Error: Frontend no compila

**Solución:**
```bash
cd /app/frontend
yarn install
sudo supervisorctl restart frontend
```

### Plan tarda más de 5 minutos

**Posibles causas:**
- API de OpenAI lenta
- Prompts muy largos
- Rate limiting

**Solución:**
- Esperar o revisar logs del backend

### Chat no modifica el plan

**Verificar:**
1. El mensaje es claro y específico
2. El plan existe en MongoDB
3. La respuesta de la IA incluye JSON modificado

---

## 📊 Métricas Esperadas

| Operación | Tiempo Esperado | Agentes Ejecutados |
|-----------|----------------|-------------------|
| Plan Inicial | 2-4 minutos | 18 (E1-E9 + N0-N8) |
| Plan Seguimiento | 1-2 minutos | 8 (ES1-ES4 + NS1-NS4) |
| Modificación Chat | 10-30 segundos | 1 (GPT-4o) |
| Aprobar Plan | <1 segundo | 0 |

---

## 🎯 Próximos Tests Recomendados

1. **Test de carga**: Generar 5 planes consecutivos
2. **Test de validación**: Crear plan con datos inválidos
3. **Test de seguimiento**: Generar plan de seguimiento mensual
4. **Test de errores**: Simular fallos de agentes
5. **Test de concurrencia**: 2 admins generando planes simultáneamente

---

## 📝 Registro de Tests Ejecutados

| Fecha | Test | Resultado | Notas |
|-------|------|-----------|-------|
| 2025-01-15 | Test 1 | ✅ | APIs registradas |
| 2025-01-15 | Test 2 | ⏳ | Pendiente |
| 2025-01-15 | Test 3 | ⏳ | Pendiente |

---

**Estado del Sistema:** ✅ Listo para testing
**Última actualización:** 2025-01-15
