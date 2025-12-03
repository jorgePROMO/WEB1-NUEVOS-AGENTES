# EDN360 E2E Testing Results - Jorge2 User

## Test Execution Summary
- **User ID**: 1764168881795908
- **Test Date**: 2025-12-03T18:52:00Z
- **Total Scenarios**: 3 (Planned)
- **Backend URL**: https://edn360-audit.preview.emergentagent.com/api
- **Local Backend URL**: http://localhost:8001/api
- **Microservice URL**: http://localhost:4000

## Architecture Validation Results

### ✅ VERIFIED COMPONENTS

1. **Backend Structure**: ✅ WORKING
   - Admin authentication: ✅ Working
   - Jorge2 user exists: ✅ Confirmed (jorge31011987@gmail.com)
   - STATE construction: ✅ Working correctly
   - Error handling: ✅ Proper 404/500 responses

2. **Database State**: ✅ VERIFIED
   - Jorge2 has 2 questionnaires in database
   - Jorge2 has 1 existing training plan
   - STATE shows: "Has initial: True | Previous followups: 0 | Previous plans: 1 | Has last_plan: True"

3. **Microservice Health**: ✅ HEALTHY
   - Service running on localhost:4000
   - Health endpoint responds: {"status":"ok","service":"edn360-workflow-service"}

4. **Mock Endpoint**: ✅ WORKING
   - /api/training-plan/mock returns proper structure
   - 4 sessions with blocks and exercises
   - All required fields present (db_id, video_url, etc.)

### ❌ BLOCKING ISSUE: Workflow Timeout at E7.5
            
## Test Execution Summary
- **User ID**: 1764168881795908
- **Test Date**: 2025-12-03T18:52:04.291787
- **Total Scenarios**: 3
- **Backend URL**: https://edn360-audit.preview.emergentagent.com/api

## Test Results Overview

## Scenario 1: INITIAL PLAN (No History)

### Request Body
```json
{
  "user_id": "1764168881795908",
  "questionnaire_ids": [
    "1764713509409284"
  ],
  "previous_training_plan_id": null
}
```

### STATE Object
```
2025-12-03 18:44:48,061 - server - INFO - ✅ Cuestionarios recuperados | Total en BD: 2 | Initial (más antiguo): 1764713509409284 | Previous followups: 0 | Current: 1764713509409284
2025-12-03 18:44:48,066 - server - INFO - ✅ Planes previos recuperados | Total en BD: 1 | Previous plans en STATE: 1 | Has last_plan: True
2025-12-03 18:44:48,076 - server - INFO - ✅ Objeto STATE construido | Has initial: True | Previous followups: 0 | Previous plans: 1 | Has last_plan: True
2025-12-03 18:49:48,171 - server - INFO - ✅ Cuestionarios recuperados | Total en BD: 2 | Initial (más antiguo): 1764713509409284 | Previous followups: 0 | Current: 1764713509409284
2025-12-03 18:49:48,171 - server - INFO - ✅ Planes previos recuperados | Total en BD: 1 | Previous plans en STATE: 1 | Has last_plan: True
2025-12-03 18:49:48,172 - server - INFO - ✅ Objeto STATE construido | Has initial: True | Previous followups: 0 | Previous plans: 1 | Has last_plan: True
```

### Final Response
```json
{}
```

### Validation Results
- Test failed or incomplete

### Exception
```
HTTPSConnectionPool(host='edn360-audit.preview.emergentagent.com', port=443): Read timed out. (read timeout=180)
```

## Scenario 2: FIRST FOLLOW-UP (With Initial Plan)

### Request Body
```json
{
  "user_id": "1764168881795908",
  "questionnaire_ids": [
    "1764713509409284"
  ],
  "previous_training_plan_id": null
}
```

### STATE Object
```
2025-12-03 18:44:48,061 - server - INFO - ✅ Cuestionarios recuperados | Total en BD: 2 | Initial (más antiguo): 1764713509409284 | Previous followups: 0 | Current: 1764713509409284
2025-12-03 18:44:48,066 - server - INFO - ✅ Planes previos recuperados | Total en BD: 1 | Previous plans en STATE: 1 | Has last_plan: True
2025-12-03 18:44:48,076 - server - INFO - ✅ Objeto STATE construido | Has initial: True | Previous followups: 0 | Previous plans: 1 | Has last_plan: True
2025-12-03 18:49:48,171 - server - INFO - ✅ Cuestionarios recuperados | Total en BD: 2 | Initial (más antiguo): 1764713509409284 | Previous followups: 0 | Current: 1764713509409284
2025-12-03 18:49:48,171 - server - INFO - ✅ Planes previos recuperados | Total en BD: 1 | Previous plans en STATE: 1 | Has last_plan: True
2025-12-03 18:49:48,172 - server - INFO - ✅ Objeto STATE construido | Has initial: True | Previous followups: 0 | Previous plans: 1 | Has last_plan: True
```

### Final Response
```json
{}
```

### Validation Results
- Test failed or incomplete

### Exception
```
HTTPSConnectionPool(host='edn360-audit.preview.emergentagent.com', port=443): Read timed out. (read timeout=180)
```

## Scenario 3: SECOND FOLLOW-UP (With Multiple Plans)

### Request Body
```json
{
  "user_id": "1764168881795908",
  "questionnaire_ids": [
    "1764713509409284"
  ],
  "previous_training_plan_id": null
}
```

### STATE Object
```
2025-12-03 18:44:48,061 - server - INFO - ✅ Cuestionarios recuperados | Total en BD: 2 | Initial (más antiguo): 1764713509409284 | Previous followups: 0 | Current: 1764713509409284
2025-12-03 18:44:48,066 - server - INFO - ✅ Planes previos recuperados | Total en BD: 1 | Previous plans en STATE: 1 | Has last_plan: True
2025-12-03 18:44:48,076 - server - INFO - ✅ Objeto STATE construido | Has initial: True | Previous followups: 0 | Previous plans: 1 | Has last_plan: True
2025-12-03 18:49:48,171 - server - INFO - ✅ Cuestionarios recuperados | Total en BD: 2 | Initial (más antiguo): 1764713509409284 | Previous followups: 0 | Current: 1764713509409284
2025-12-03 18:49:48,171 - server - INFO - ✅ Planes previos recuperados | Total en BD: 1 | Previous plans en STATE: 1 | Has last_plan: True
2025-12-03 18:49:48,172 - server - INFO - ✅ Objeto STATE construido | Has initial: True | Previous followups: 0 | Previous plans: 1 | Has last_plan: True
```

### Final Response
```json
{}
```

### Validation Results
- Test failed or incomplete

### Error Details
- Status Code: 502
- Error Data: ""

## Test Execution Log

- ✅ **Admin Login**: Admin logged in successfully. Role: admin
- ✅ **Check User Exists**: Jorge2 user found: Jorge2 (jorge31011987@gmail.com)
- ✅ **Microservice Health**: EDN360 microservice healthy: {'status': 'ok', 'service': 'edn360-workflow-service'}
- ❌ **Execute Scenario 1 - Initial Plan**: Exception: HTTPSConnectionPool(host='edn360-audit.preview.emergentagent.com', port=443): Read timed out. (read timeout=180)
- ❌ **Execute Scenario 2 - First Follow-up**: Exception: HTTPSConnectionPool(host='edn360-audit.preview.emergentagent.com', port=443): Read timed out. (read timeout=180)
- ❌ **Execute Scenario 3 - Second Follow-up**: HTTP 502
- ✅ **Capture Backend Logs**: Backend logs captured: 6 relevant lines
- ✅ **Capture Microservice Logs**: Microservice logs captured: 103 lines
