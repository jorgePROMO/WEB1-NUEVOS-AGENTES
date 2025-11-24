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
  - task: "EDN360Snapshot Model & Collection"
    implemented: true
    working: "NA"
    file: "/app/backend/edn360_models/edn360_snapshot.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
        - working: "NA"
          agent: "main"
          comment: "Modelo Pydantic EDN360Snapshot creado con campos: snapshot_id (UUID), user_id, created_at, version, input (EDN360Input dict), workflow_name, workflow_response (dict), status (success/failed), error_message. Modelo tiene helpers: is_success(), is_failed(), get_summary(). Funciones auxiliares: validate_snapshot_status(), create_success_snapshot(), create_failed_snapshot()."

  - task: "EDN360 Snapshot Repository"
    implemented: true
    working: "NA"
    file: "/app/backend/repositories/edn360_snapshot_repository.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
        - working: "NA"
          agent: "main"
          comment: "Repository creado con funciones: create_snapshot() (insert inmutable), get_snapshot_by_id(), get_snapshots_by_user() (con filtros limit y status), get_latest_snapshot_for_user(), count_snapshots_by_user(), get_snapshot_summary_for_user(). Función ensure_snapshot_indexes() crea índices: user_id, created_at (desc), status. Índices inicializados exitosamente en startup."

  - task: "GPT Service - OpenAI Integration"
    implemented: true
    working: "NA"
    file: "/app/backend/services/gpt_service.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
        - working: "NA"
          agent: "main"
          comment: "Servicio call_edn360_workflow() implementado. Usa OpenAI Chat Completions API directa (NO Assistants). Configuración: EDN360_OPENAI_API_KEY (propia del usuario), EDN360_OPENAI_MODEL (gpt-4o), response_format JSON. Maneja errores: APIError, APIConnectionError, RateLimitError, JSONDecodeError. Devuelve workflow_response con _metadata (tokens, model). Helper validate_workflow_response() para validar respuesta. NOTA: API Key placeholder 'TU_API_KEY_AQUI' en .env debe reemplazarse con key real."

  - task: "EDN360 Orchestrator v1"
    implemented: true
    working: "NA"
    file: "/app/backend/services/edn360_orchestrator_v1.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
        - working: "NA"
          agent: "main"
          comment: "Orquestador run_edn360_workflow_for_user() implementado. Flujo: 1) Construye EDN360Input usando build_edn360_input_for_user() (FASE 2), 2) Llama a call_edn360_workflow(), 3) Crea snapshot inmutable (success o failed), 4) Devuelve resumen ligero (snapshot_id, status, created_at, workflow_name, has_response). Maneja errores: EDN360NoDrawerError, EDN360NoQuestionnaireError, errores de OpenAI. Siempre devuelve resultado (nunca lanza excepciones). NO modifica training_plans ni nutrition_plans."

  - task: "Admin Endpoint - Run Workflow"
    implemented: true
    working: "NA"
    file: "/app/backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
        - working: "NA"
          agent: "main"
          comment: "Endpoint POST /api/admin/users/{user_id}/edn360-run-workflow implementado. Admin-only (require_admin). Valida que usuario existe, llama a run_edn360_workflow_for_user(), devuelve resultado con snapshot info. Respuestas: 200 OK (success o failed), 404 Not Found (usuario inexistente), 500 Internal Server Error. NO modifica training_plans ni nutrition_plans."

  - task: "Startup Indexes Initialization"
    implemented: true
    working: true
    file: "/app/backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
        - working: "NA"
          agent: "main"
          comment: "Startup event startup_fase3_indexes() agregado. Llama a ensure_snapshot_indexes() al arrancar servidor. Índices creados en colección edn360_snapshots: user_id, created_at (desc), status."
        - working: true
          agent: "main"
          comment: "✅ VERIFIED: Backend arrancado exitosamente. Logs muestran '✅ Índice creado: edn360_snapshots.user_id', '✅ Índice creado: edn360_snapshots.created_at', '✅ Índice creado: edn360_snapshots.status', '✅ Índices de edn360_snapshots verificados', '✅ Índices de FASE 3 inicializados correctamente'. Backend funcionando en puerto 8001."

frontend:
  - task: "EDN360 Workflow Launch Button"
    implemented: true
    working: "NA"
    file: "/app/frontend/src/pages/AdminDashboard.jsx"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
        - working: "NA"
          agent: "main"
          comment: "Botón 'Lanzar EDN360 Workflow (TEST)' agregado en AdminDashboard después del botón 'Ver EDN360 Input'. Estilo: color naranja (bg-orange-50, border-orange-300, text-orange-700). Estados: launchingWorkflow, workflowResult, showWorkflowResultModal. Función handleLaunchWorkflow() implementada: 1) Confirmación con window.confirm, 2) Llamada POST a /api/admin/users/{user_id}/edn360-run-workflow, 3) Muestra resultado con alert (snapshot_id, status, error_message), 4) Spinner animado durante ejecución. Deshabilitado cuando está lanzando workflow."

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
