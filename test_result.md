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

user_problem_statement: "Sistema E.D.N.360 - Error 504 Timeout al generar planes. Usuario reporta: 'AL INTENTAR CREAR EL PRIMER PROGRAMA DE ENTRENAMIENTO, ME SALE Error al generar plan: Request failed with status code 504'. Implementar arquitectura asíncrona basada en jobs para evitar timeouts y mejorar UX."

agent_communication:
    - agent: "main"
      message: "🚀 SISTEMA DE JOBS ASÍNCRONO IMPLEMENTADO: Creada arquitectura completa para generación asíncrona de planes E.D.N.360. BACKEND: 1) Nueva colección generation_jobs con campos: user_id, type (training/nutrition/full), submission_id, status (pending/running/completed/failed), progress (phase, current_agent, completed_steps, percentage), result (training_plan_id, nutrition_plan_id), error_message, timestamps. 2) Endpoint POST /admin/users/{user_id}/plans/generate_async que crea job y lanza background task, responde inmediatamente con job_id. 3) Función process_generation_job(job_id) que ejecuta el orquestador E1-E9 o N0-N8 en background, actualiza progreso después de cada agente, guarda resultado en BD. 4) Endpoint GET /jobs/{job_id} para consultar estado. FRONTEND: 1) Componente GenerationProgressModal con polling cada 3 segundos, barra de progreso animada, muestra agente actual y porcentaje. 2) Actualizadas funciones generateTrainingPlan() y generateNutritionPlan() para usar endpoint asíncrono. 3) Nueva función generateFullPlan() para generar training + nutrition en un solo job. 4) Callbacks handleGenerationComplete/Error/Close. TODO EL ORQUESTADOR E1-E9 y N0-N8 SE MANTIENE SIN CAMBIOS. READY FOR TESTING."

backend:
  - task: "Generation Jobs Collection & Models"
    implemented: true
    working: "NA"
    file: "/app/backend/models.py"
    stuck_count: 0
    priority: "critical"
    needs_retesting: true
    status_history:
        - working: "NA"
          agent: "main"
          comment: "Creados modelos Pydantic: GenerationJob, GenerationJobProgress, GenerationJobResult, GenerateAsyncRequest. Colección generation_jobs en MongoDB con todos los campos necesarios para tracking de jobs asíncronos."

  - task: "Async Generation Endpoint"
    implemented: true
    working: "NA"
    file: "/app/backend/server.py"
    stuck_count: 0
    priority: "critical"
    needs_retesting: true
    status_history:
        - working: "NA"
          agent: "main"
          comment: "Endpoint POST /admin/users/{user_id}/plans/generate_async implementado. Valida usuario y cuestionario, crea job en BD con status=pending, lanza asyncio.create_task(process_generation_job(job_id)), responde inmediatamente con job_id. Soporta mode: training, nutrition, full."

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

  - task: "Job Status Query Endpoint"
    implemented: true
    working: "NA"
    file: "/app/backend/server.py"
    stuck_count: 0
    priority: "critical"
    needs_retesting: true
    status_history:
        - working: "NA"
          agent: "main"
          comment: "Endpoint GET /jobs/{job_id} implementado (público, sin auth para simplificar polling). Devuelve: status, progress, result, error_message, timestamps. Serializa datetime fields correctamente."

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
    - "Job Status Query Endpoint"
    - "Background Job Processor"
    - "GenerationProgressModal Component"
  stuck_tasks: []
  test_all: false
  test_priority: "high_first"
