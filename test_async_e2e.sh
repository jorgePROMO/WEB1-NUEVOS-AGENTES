#!/bin/bash

# Test E2E del Sistema de Generación Asíncrona E.D.N.360

API="https://exerule-system.preview.emergentagent.com/api"
USER_ID="1762976907472415"
SUBMISSION_ID="1762977457211469"

echo "================================"
echo "🧪 TEST E2E - Generación Asíncrona"
echo "================================"
echo ""

# 1. Login como admin
echo "📝 PASO 1: Login como admin..."
LOGIN_RESPONSE=$(curl -s -X POST "${API}/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "ecjtrainer@gmail.com",
    "password": "jorge3007"
  }')

TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*"' | sed 's/"access_token":"\([^"]*\)"/\1/')

if [ -z "$TOKEN" ]; then
  echo "❌ Error: No se pudo obtener token"
  exit 1
fi

echo "✅ Token obtenido: ${TOKEN:0:20}..."
echo ""

# 2. Crear job de generación asíncrona
echo "🚀 PASO 2: Crear job de generación (mode: training)..."
JOB_RESPONSE=$(curl -s -X POST "${API}/admin/users/${USER_ID}/plans/generate_async" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${TOKEN}" \
  -d '{
    "submission_id": "'${SUBMISSION_ID}'",
    "mode": "training"
  }')

echo "Response: $JOB_RESPONSE"

JOB_ID=$(echo $JOB_RESPONSE | grep -o '"job_id":"[^"]*"' | sed 's/"job_id":"\([^"]*\)"/\1/')

if [ -z "$JOB_ID" ]; then
  echo "❌ Error: No se pudo crear el job"
  echo "Response completo: $JOB_RESPONSE"
  exit 1
fi

echo "✅ Job creado: $JOB_ID"
echo ""

# 3. Polling del estado del job
echo "📊 PASO 3: Consultando estado del job..."
echo "Esperando 5 segundos para que el job comience a procesarse..."
sleep 5

for i in {1..10}; do
  echo ""
  echo "--- Consulta $i ---"
  
  STATUS_RESPONSE=$(curl -s "${API}/jobs/${JOB_ID}")
  
  STATUS=$(echo $STATUS_RESPONSE | grep -o '"status":"[^"]*"' | sed 's/"status":"\([^"]*\)"/\1/')
  PERCENTAGE=$(echo $STATUS_RESPONSE | grep -o '"percentage":[0-9]*' | sed 's/"percentage"://')
  CURRENT_AGENT=$(echo $STATUS_RESPONSE | grep -o '"current_agent":"[^"]*"' | sed 's/"current_agent":"\([^"]*\)"/\1/')
  MESSAGE=$(echo $STATUS_RESPONSE | grep -o '"message":"[^"]*"' | sed 's/"message":"\([^"]*\)"/\1/')
  
  echo "Status: $STATUS"
  echo "Progress: ${PERCENTAGE}%"
  echo "Current Agent: $CURRENT_AGENT"
  echo "Message: $MESSAGE"
  
  if [ "$STATUS" = "completed" ]; then
    echo ""
    echo "✅ Job completado exitosamente!"
    
    TRAINING_PLAN_ID=$(echo $STATUS_RESPONSE | grep -o '"training_plan_id":"[^"]*"' | sed 's/"training_plan_id":"\([^"]*\)"/\1/')
    echo "Training Plan ID: $TRAINING_PLAN_ID"
    
    break
  fi
  
  if [ "$STATUS" = "failed" ]; then
    echo ""
    echo "❌ Job falló"
    ERROR=$(echo $STATUS_RESPONSE | grep -o '"error_message":"[^"]*"' | sed 's/"error_message":"\([^"]*\)"/\1/')
    echo "Error: $ERROR"
    
    break
  fi
  
  echo "Esperando 10 segundos antes de la siguiente consulta..."
  sleep 10
done

echo ""
echo "================================"
echo "✅ TEST COMPLETADO"
echo "================================"
