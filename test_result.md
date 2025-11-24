#====================================================================================================
# START - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================

# THIS SECTION CONTAINS CRITICAL TESTING INSTRUCTIONS FOR BOTH AGENTS
# BOTH MAIN_AGENT AND TESTING_AGENT MUST PRESERVE THIS ENTIRE BLOCK

# Communication Protocol:
# If the `testing_agent` is available, main agent should delegate all testing tasks to it.
#
# You have access to a file called `test_result.md`. This file contains the complete testing state
# and history, and is the primary means of communication between main and the testing agent.
#
# Main and testing agents must follow this exact format to maintain testing data. 
# The testing data must be entered in yaml format Below is the data structure:
# 
## user_problem_statement: {problem_statement}
## backend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.py"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## frontend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.js"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## metadata:
##   created_by: "main_agent"
##   version: "1.0"
##   test_sequence: 0
##   run_ui: false
##
## test_plan:
##   current_focus:
##     - "Task name 1"
##     - "Task name 2"
##   stuck_tasks:
##     - "Task name with persistent issues"
##   test_all: false
##   test_priority: "high_first"  # or "sequential" or "stuck_first"
##
## agent_communication:
##     -agent: "main"  # or "testing" or "user"
##     -message: "Communication message between agents"

# Protocol Guidelines for Main agent
#
# 1. Update Test Result File Before Testing:
#    - Main agent must always update the `test_result.md` file before calling the testing agent
#    - Add implementation details to the status_history
#    - Set `needs_retesting` to true for tasks that need testing
#    - Update the `test_plan` section to guide testing priorities
#    - Add a message to `agent_communication` explaining what you've done
#
# 2. Incorporate User Feedback:
#    - When a user provides feedback that something is or isn't working, add this information to the relevant task's status_history
#    - Update the working status based on user feedback
#    - If a user reports an issue with a task that was marked as working, increment the stuck_count
#    - Whenever user reports issue in the app, if we have testing agent and task_result.md file so find the appropriate task for that and append in status_history of that task to contain the user concern and problem as well 
#
# 3. Track Stuck Tasks:
#    - Monitor which tasks have high stuck_count values or where you are fixing same issue again and again, analyze that when you read task_result.md
#    - For persistent issues, use websearch tool to find solutions
#    - Pay special attention to tasks in the stuck_tasks list
#    - When you fix an issue with a stuck task, don't reset the stuck_count until the testing agent confirms it's working
#
# 4. Provide Context to Testing Agent:
#    - When calling the testing agent, provide clear instructions about:
#      - Which tasks need testing (reference the test_plan)
#      - Any authentication details or configuration needed
#      - Specific test scenarios to focus on
#      - Any known issues or edge cases to verify
#
# 5. Call the testing agent with specific instructions referring to test_result.md
#
# IMPORTANT: Main agent must ALWAYS update test_result.md BEFORE calling the testing agent, as it relies on this file to understand what to test next.

#====================================================================================================
# END - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================



#====================================================================================================
# Testing Data - Main Agent and testing sub agent both should log testing data below this section
#====================================================================================================

user_problem_statement: "FASE 3: Implementar Nuevo Orquestador EDN360 v1. Crear sistema completo que: 1) Construya EDN360Input para un usuario (reutilizando FASE 2), 2) Llame a un Workflow de OpenAI (Chat Completions API directa) con ese input, 3) Guarde snapshot técnico inmutable en BD edn360_app. IMPORTANTE: Esta fase es SOLO para testing interno desde panel admin. NO debe modificar training_plans ni nutrition_plans. NO debe reactivar generación para cliente final. NO debe modificar job worker."

agent_communication:
    - agent: "main"
      message: "✅ FASE 3 IMPLEMENTADA COMPLETAMENTE: 1) MODELO EDN360Snapshot creado en /app/backend/edn360_models/edn360_snapshot.py con campos: snapshot_id (UUID), user_id, created_at, version, input (EDN360Input dict), workflow_name, workflow_response (dict), status (success/failed), error_message. 2) REPOSITORY edn360_snapshot_repository.py con funciones: create_snapshot(), get_snapshot_by_id(), get_snapshots_by_user(), get_latest_snapshot_for_user(), count_snapshots_by_user(), get_snapshot_summary_for_user(). Índices creados: user_id, created_at (desc), status. 3) SERVICIO gpt_service.py con call_edn360_workflow() que llama a OpenAI Chat Completions API usando EDN360_OPENAI_API_KEY y EDN360_OPENAI_MODEL (gpt-4o). 4) ORQUESTADOR edn360_orchestrator_v1.py con run_edn360_workflow_for_user() que: construye EDN360Input, llama a OpenAI, crea snapshot inmutable (success o failed), devuelve resumen ligero. 5) ENDPOINT admin POST /api/admin/users/{user_id}/edn360-run-workflow implementado, admin-only, crea snapshot técnico. 6) FRONTEND: Botón 'Lanzar EDN360 Workflow (TEST)' agregado en AdminDashboard, color naranja, muestra spinner durante ejecución, dialog de confirmación, muestra resultado (snapshot_id, status). 7) VARIABLES .env agregadas: EDN360_OPENAI_API_KEY, EDN360_OPENAI_MODEL, EDN360_WORKFLOW_NAME. 8) STARTUP EVENT agregado para inicializar índices de edn360_snapshots al arrancar servidor. NOTA: NO se tocó job_worker, training_plans, nutrition_plans ni botones de usuario. Backend arrancando correctamente. READY FOR TESTING."

backend:
  - task: "Generation Jobs Collection & Models"
    implemented: true
    working: true
    file: "/app/backend/models.py"
    stuck_count: 0
    priority: "critical"
    needs_retesting: false
    status_history:
        - working: "NA"
          agent: "main"
          comment: "Creados modelos Pydantic: GenerationJob, GenerationJobProgress, GenerationJobResult, GenerateAsyncRequest. Colección generation_jobs en MongoDB con todos los campos necesarios para tracking de jobs asíncronos."
        - working: true
          agent: "testing"
          comment: "✅ VERIFIED: Models exist in /app/backend/models.py. Found GenerationJob, GenerationJobProgress, GenerationJobResult, GenerateAsyncRequest classes with correct fields for async job tracking."

  - task: "Async Generation Endpoint"
    implemented: true
    working: false
    file: "/app/backend/server.py"
    stuck_count: 1
    priority: "critical"
    needs_retesting: false
    status_history:
        - working: "NA"
          agent: "main"
          comment: "Endpoint POST /admin/users/{user_id}/plans/generate_async implementado. Valida usuario y cuestionario, crea job en BD con status=pending, lanza asyncio.create_task(process_generation_job(job_id)), responde inmediatamente con job_id. Soporta mode: training, nutrition, full."
        - working: false
          agent: "testing"
          comment: "❌ CRITICAL ISSUE: Endpoint exists but returns 404 'Cuestionario no encontrado' when testing with mock submission_id. The endpoint requires a REAL nutrition questionnaire submission from the database, not mock data. Authentication also has issues - Bearer token not being accepted properly. NEEDS REAL DATA TO TEST."

  - task: "Background Job Processor"
    implemented: true
    working: "NA"
    file: "/app/backend/server.py"
    stuck_count: 0
    priority: "critical"
    needs_retesting: true
    status_history:
        - working: "NA"
          agent: "main"
          comment: "Función process_generation_job(job_id) implementada. Ejecuta el orquestador E1-E9 y/o N0-N8 según el type del job, actualiza progreso en BD después de cada fase, maneja errores y actualiza status a completed/failed. Reutiliza TODO el código existente del orquestador sin modificarlo."
        - working: "NA"
          agent: "testing"
          comment: "⚠️ CANNOT TEST: Background processor cannot be tested without successful job creation. Depends on Async Generation Endpoint working first. Code exists in server.py as process_generation_job() function."

  - task: "Job Status Query Endpoint"
    implemented: true
    working: true
    file: "/app/backend/server.py"
    stuck_count: 0
    priority: "critical"
    needs_retesting: false
    status_history:
        - working: "NA"
          agent: "main"
          comment: "Endpoint GET /jobs/{job_id} implementado (público, sin auth para simplificar polling). Devuelve: status, progress, result, error_message, timestamps. Serializa datetime fields correctamente."
        - working: true
          agent: "testing"
          comment: "✅ VERIFIED: GET /jobs/{job_id} endpoint working correctly. Public access (no auth required). Returns proper 404 'Job no encontrado' for non-existent jobs. Ready for polling when jobs are created."

frontend:
  - task: "GenerationProgressModal Component"
    implemented: true
    working: "NA"
    file: "/app/frontend/src/components/GenerationProgressModal.jsx"
    stuck_count: 0
    priority: "critical"
    needs_retesting: true
    status_history:
        - working: "NA"
          agent: "main"
          comment: "Componente React creado con: polling cada 3 segundos a GET /jobs/{job_id}, barra de progreso animada con gradient, muestra agente actual (E1, E2, etc.), porcentaje y mensaje, animación de loading, maneja estados completed/failed, callbacks onComplete/onError/onClose."

  - task: "Updated Generation Functions"
    implemented: true
    working: "NA"
    file: "/app/frontend/src/pages/AdminDashboard.jsx"
    stuck_count: 0
    priority: "critical"
    needs_retesting: true
    status_history:
        - working: "NA"
          agent: "main"
          comment: "Actualizadas generateTrainingPlan() y generateNutritionPlan() para llamar a POST /admin/users/{user_id}/plans/generate_async, setear job_id y mostrar GenerationProgressModal. Añadida función generateFullPlan() para mode=full (training + nutrition). Callbacks implementados: handleGenerationComplete (recarga datos), handleGenerationError (muestra error), handleGenerationClose."

metadata:
  created_by: "main_agent"
  version: "1.0"
  test_sequence: 1
  run_ui: false

test_plan:
  current_focus:
    - "Async Generation Endpoint"
    - "Background Job Processor"
    - "GenerationProgressModal Component"
  stuck_tasks:
    - "Async Generation Endpoint"
  test_all: false
  test_priority: "high_first"
