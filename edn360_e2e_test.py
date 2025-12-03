#!/usr/bin/env python3
"""
EDN360 E2E Testing - Jorge2 Evolutionary Workflow
Tests the complete evolutionary flow for user Jorge2 (1764168881795908)
"""

import requests
import json
import sys
import os
from datetime import datetime
import time

# Backend URL from frontend/.env
BACKEND_URL = "https://training-plan-gen.preview.emergentagent.com/api"

class EDN360E2ETester:
    def __init__(self):
        self.admin_token = None
        self.results = []
        self.plan_ids = []  # Store plan IDs for sequential testing
        
    def log_result(self, test_name, success, message, response_data=None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        self.results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        if response_data and not success:
            print(f"   Response: {json.dumps(response_data, indent=2)[:500]}...")
    
    def admin_login(self):
        """Admin login for EDN360 testing"""
        url = f"{BACKEND_URL}/auth/login"
        params = {
            "email": "ecjtrainer@gmail.com",
            "password": "jorge3007"
        }
        
        try:
            response = requests.post(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                if "user" in data and "token" in data and data["user"].get("role") == "admin":
                    self.admin_token = data["token"]
                    self.log_result("Admin Login", True, 
                                  f"Admin logged in successfully. Role: {data['user']['role']}")
                    return True
                else:
                    self.log_result("Admin Login", False, 
                                  "Response missing user/token or not admin role", data)
            else:
                self.log_result("Admin Login", False, 
                              f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Admin Login", False, f"Exception: {str(e)}")
        
        return False

    def case_1_initial_plan(self):
        """
        CASE 1: Plan Inicial (Sin Historial)
        Request: user_id + questionnaire_ids: ["edn360_inicial_jorge2"]
        Expected: is_evolutionary: false, STATE with last_plan: null, previous_plans: []
        """
        if not self.admin_token:
            self.log_result("CASE 1 - Initial Plan", False, "No admin token available")
            return False
            
        user_id = "1764168881795908"
        questionnaire_ids = ["edn360_inicial_jorge2"]
        
        url = f"{BACKEND_URL}/training-plan"
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        payload = {
            "user_id": user_id,
            "questionnaire_ids": questionnaire_ids
        }
        
        try:
            print(f"\n🧪 CASE 1: Plan Inicial (Sin Historial)")
            print(f"   User ID: {user_id}")
            print(f"   Questionnaire IDs: {questionnaire_ids}")
            print(f"   Expected: is_evolutionary=false, no previous plans")
            
            response = requests.post(url, json=payload, headers=headers, timeout=120)
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                if "client_training_program_enriched" in data and "is_evolutionary" in data:
                    is_evolutionary = data["is_evolutionary"]
                    training_program = data["client_training_program_enriched"]
                    
                    # For initial plan, should be False
                    if not is_evolutionary:
                        # Verify training program structure
                        if "sessions" in training_program and len(training_program["sessions"]) > 0:
                            sessions = training_program["sessions"]
                            
                            # Verify sessions have blocks with exercises
                            valid_structure = True
                            exercise_count = 0
                            
                            for session in sessions:
                                if "blocks" not in session:
                                    valid_structure = False
                                    break
                                for block in session["blocks"]:
                                    if "exercises" not in block:
                                        valid_structure = False
                                        break
                                    for exercise in block["exercises"]:
                                        exercise_count += 1
                                        # Verify exercise has required fields
                                        required_fields = ["db_id", "name", "series", "reps", "rpe", "notes", "video_url"]
                                        if not all(field in exercise for field in required_fields):
                                            valid_structure = False
                                            break
                            
                            if valid_structure and exercise_count > 0:
                                # Store plan info for next case
                                self.plan_1_info = {
                                    "user_id": user_id,
                                    "questionnaire_ids": questionnaire_ids,
                                    "sessions": len(sessions),
                                    "exercise_count": exercise_count,
                                    "title": training_program.get("title", "N/A")
                                }
                                
                                self.log_result("CASE 1 - Initial Plan", True, 
                                              f"✅ Initial plan created successfully: is_evolutionary={is_evolutionary}, sessions={len(sessions)}, exercises={exercise_count}, title='{training_program.get('title', 'N/A')}'")
                                return True
                            else:
                                self.log_result("CASE 1 - Initial Plan", False, 
                                              f"Invalid exercise structure: valid={valid_structure}, exercise_count={exercise_count}")
                        else:
                            self.log_result("CASE 1 - Initial Plan", False, 
                                          "Training program missing sessions or empty sessions")
                    else:
                        self.log_result("CASE 1 - Initial Plan", False, 
                                      f"Expected is_evolutionary=False for initial plan, got {is_evolutionary}")
                else:
                    self.log_result("CASE 1 - Initial Plan", False, 
                                  "Response missing required fields", data)
            else:
                self.log_result("CASE 1 - Initial Plan", False, 
                              f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("CASE 1 - Initial Plan", False, f"Exception: {str(e)}")
        
        return False

    def get_latest_plan_id(self, user_id):
        """Get the latest training plan ID for a user from database"""
        try:
            import subprocess
            
            # Query MongoDB to get the latest plan
            cmd = f'mongosh edn360_app --eval "db.training_plans_v2.findOne({{user_id: \\"{user_id}\\"}}, {{_id: 1, created_at: 1}}, {{sort: {{created_at: -1}}}})._id" --quiet'
            
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                output = result.stdout.strip()
                if output and output != "null":
                    # Extract ObjectId
                    if "ObjectId(" in output:
                        plan_id = output.split("ObjectId(")[1].split(")")[0].strip("'\"")
                        return plan_id
                    else:
                        return output.strip("'\"")
            
            return None
        except Exception as e:
            print(f"Error getting latest plan ID: {e}")
            return None

    def case_2_first_evolution(self):
        """
        CASE 2: Primer Seguimiento (Primera Evolución)
        Request: user_id + questionnaire_ids: ["edn360_inicial_jorge2", "edn360_seg1_jorge2"] + previous_training_plan_id
        Expected: is_evolutionary: true, STATE with previous_plans: [Plan 1], last_plan: Plan 1
        """
        if not self.admin_token or not hasattr(self, 'plan_1_info'):
            self.log_result("CASE 2 - First Evolution", False, "No admin token or Plan 1 info available")
            return False
            
        user_id = "1764168881795908"
        questionnaire_ids = ["edn360_inicial_jorge2", "edn360_seg1_jorge2"]
        
        # Get the latest plan ID from database
        previous_training_plan_id = self.get_latest_plan_id(user_id)
        if not previous_training_plan_id:
            self.log_result("CASE 2 - First Evolution", False, "Could not retrieve Plan 1 ID from database")
            return False
        
        url = f"{BACKEND_URL}/training-plan"
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        payload = {
            "user_id": user_id,
            "questionnaire_ids": questionnaire_ids,
            "previous_training_plan_id": previous_training_plan_id
        }
        
        try:
            print(f"\n🧪 CASE 2: Primer Seguimiento (Primera Evolución)")
            print(f"   User ID: {user_id}")
            print(f"   Questionnaire IDs: {questionnaire_ids}")
            print(f"   Previous Plan ID: {previous_training_plan_id}")
            print(f"   Expected: is_evolutionary=true, has previous plans")
            
            response = requests.post(url, json=payload, headers=headers, timeout=120)
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                if "client_training_program_enriched" in data and "is_evolutionary" in data:
                    is_evolutionary = data["is_evolutionary"]
                    training_program = data["client_training_program_enriched"]
                    
                    # For evolution plan, should be True
                    if is_evolutionary:
                        # Verify training program structure
                        if "sessions" in training_program and len(training_program["sessions"]) > 0:
                            sessions = training_program["sessions"]
                            
                            # Compare with Plan 1 to verify evolution
                            plan_1_sessions = self.plan_1_info["sessions"]
                            plan_1_exercises = self.plan_1_info["exercise_count"]
                            
                            # Count exercises in Plan 2
                            exercise_count = 0
                            for session in sessions:
                                for block in session.get("blocks", []):
                                    exercise_count += len(block.get("exercises", []))
                            
                            # Store plan info for next case
                            self.plan_2_info = {
                                "user_id": user_id,
                                "questionnaire_ids": questionnaire_ids,
                                "previous_plan_id": previous_training_plan_id,
                                "sessions": len(sessions),
                                "exercise_count": exercise_count,
                                "title": training_program.get("title", "N/A")
                            }
                            
                            self.log_result("CASE 2 - First Evolution", True, 
                                          f"✅ First evolution successful: is_evolutionary={is_evolutionary}, sessions={len(sessions)}, exercises={exercise_count}, title='{training_program.get('title', 'N/A')}'. Progression from Plan 1: {plan_1_sessions}→{len(sessions)} sessions, {plan_1_exercises}→{exercise_count} exercises")
                            return True
                        else:
                            self.log_result("CASE 2 - First Evolution", False, 
                                          "Training program missing sessions or empty sessions")
                    else:
                        self.log_result("CASE 2 - First Evolution", False, 
                                      f"Expected is_evolutionary=True for evolution plan, got {is_evolutionary}")
                else:
                    self.log_result("CASE 2 - First Evolution", False, 
                                  "Response missing required fields", data)
            else:
                self.log_result("CASE 2 - First Evolution", False, 
                              f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("CASE 2 - First Evolution", False, f"Exception: {str(e)}")
        
        return False

    def case_3_second_evolution(self):
        """
        CASE 3: Segundo Seguimiento (Segunda Evolución)
        Request: user_id + questionnaire_ids: ["edn360_inicial_jorge2", "edn360_seg2_jorge2"] + previous_training_plan_id (Plan 2)
        Expected: is_evolutionary: true, STATE with previous_plans: [Plan 1, Plan 2], last_plan: Plan 2
        """
        if not self.admin_token or not hasattr(self, 'plan_2_info'):
            self.log_result("CASE 3 - Second Evolution", False, "No admin token or Plan 2 info available")
            return False
            
        user_id = "1764168881795908"
        questionnaire_ids = ["edn360_inicial_jorge2", "edn360_seg2_jorge2"]
        
        # Get the latest plan ID from database (should be Plan 2)
        previous_training_plan_id = self.get_latest_plan_id(user_id)
        if not previous_training_plan_id:
            self.log_result("CASE 3 - Second Evolution", False, "Could not retrieve Plan 2 ID from database")
            return False
        
        url = f"{BACKEND_URL}/training-plan"
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        payload = {
            "user_id": user_id,
            "questionnaire_ids": questionnaire_ids,
            "previous_training_plan_id": previous_training_plan_id
        }
        
        try:
            print(f"\n🧪 CASE 3: Segundo Seguimiento (Segunda Evolución)")
            print(f"   User ID: {user_id}")
            print(f"   Questionnaire IDs: {questionnaire_ids}")
            print(f"   Previous Plan ID: {previous_training_plan_id}")
            print(f"   Expected: is_evolutionary=true, has 2 previous plans")
            
            response = requests.post(url, json=payload, headers=headers, timeout=120)
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                if "client_training_program_enriched" in data and "is_evolutionary" in data:
                    is_evolutionary = data["is_evolutionary"]
                    training_program = data["client_training_program_enriched"]
                    
                    # For evolution plan, should be True
                    if is_evolutionary:
                        # Verify training program structure
                        if "sessions" in training_program and len(training_program["sessions"]) > 0:
                            sessions = training_program["sessions"]
                            
                            # Count exercises in Plan 3
                            exercise_count = 0
                            for session in sessions:
                                for block in session.get("blocks", []):
                                    exercise_count += len(block.get("exercises", []))
                            
                            # Compare progression across all plans
                            plan_1_sessions = self.plan_1_info["sessions"]
                            plan_1_exercises = self.plan_1_info["exercise_count"]
                            plan_2_sessions = self.plan_2_info["sessions"]
                            plan_2_exercises = self.plan_2_info["exercise_count"]
                            
                            # Store plan info
                            self.plan_3_info = {
                                "user_id": user_id,
                                "questionnaire_ids": questionnaire_ids,
                                "previous_plan_id": previous_training_plan_id,
                                "sessions": len(sessions),
                                "exercise_count": exercise_count,
                                "title": training_program.get("title", "N/A")
                            }
                            
                            self.log_result("CASE 3 - Second Evolution", True, 
                                          f"✅ Second evolution successful: is_evolutionary={is_evolutionary}, sessions={len(sessions)}, exercises={exercise_count}, title='{training_program.get('title', 'N/A')}'. Full progression: Plan1({plan_1_sessions}s,{plan_1_exercises}e) → Plan2({plan_2_sessions}s,{plan_2_exercises}e) → Plan3({len(sessions)}s,{exercise_count}e)")
                            return True
                        else:
                            self.log_result("CASE 3 - Second Evolution", False, 
                                          "Training program missing sessions or empty sessions")
                    else:
                        self.log_result("CASE 3 - Second Evolution", False, 
                                      f"Expected is_evolutionary=True for evolution plan, got {is_evolutionary}")
                else:
                    self.log_result("CASE 3 - Second Evolution", False, 
                                  "Response missing required fields", data)
            else:
                self.log_result("CASE 3 - Second Evolution", False, 
                              f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("CASE 3 - Second Evolution", False, f"Exception: {str(e)}")
        
        return False

    def verify_database_progression(self):
        """Verify database shows correct progression of plans"""
        try:
            import subprocess
            
            user_id = "1764168881795908"
            
            # Query all plans for the user
            cmd = f'mongosh edn360_app --eval "db.training_plans_v2.find({{user_id: \\"{user_id}\\"}}, {{_id: 1, created_at: 1, is_evolutionary: 1, questionnaire_submission_id: 1}}).sort({{created_at: 1}})" --quiet'
            
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                output = result.stdout.strip()
                if output and output != "null":
                    # Count plans
                    plan_count = output.count('"user_id"')
                    
                    if plan_count >= 3:
                        self.log_result("Database Progression Verification", True, 
                                      f"✅ Database shows correct progression: {plan_count} plans created for user {user_id}")
                        return True
                    else:
                        self.log_result("Database Progression Verification", False, 
                                      f"Expected at least 3 plans, found {plan_count}")
                else:
                    self.log_result("Database Progression Verification", False, 
                                  "No plans found in database")
            else:
                self.log_result("Database Progression Verification", False, 
                              f"Database query failed: {result.stderr}")
        except Exception as e:
            self.log_result("Database Progression Verification", False, f"Exception: {str(e)}")
        
        return False

    def generate_report(self):
        """Generate comprehensive E2E test report"""
        try:
            os.makedirs("/app/docs", exist_ok=True)
            
            report_content = f"""# EDN360 - Tests E2E - Workflow Evolutivo
## Usuario: Jorge2 (1764168881795908)
## Fecha: {datetime.now().isoformat()}

### RESUMEN EJECUTIVO
- **Total Tests:** {len(self.results)}
- **Exitosos:** {len([r for r in self.results if r['success']])}
- **Fallidos:** {len([r for r in self.results if not r['success']])}

### CASO 1: Plan Inicial
#### Request Body
```json
{{
  "user_id": "1764168881795908",
  "questionnaire_ids": ["edn360_inicial_jorge2"]
}}
```

#### Resultado
"""
            
            # Add Case 1 results
            case_1_result = next((r for r in self.results if "CASE 1" in r["test"]), None)
            if case_1_result:
                report_content += f"**Estado:** {'✅ EXITOSO' if case_1_result['success'] else '❌ FALLIDO'}\n"
                report_content += f"**Mensaje:** {case_1_result['message']}\n\n"
                
                if hasattr(self, 'plan_1_info'):
                    report_content += f"""#### Análisis Plan 1
- **Título:** {self.plan_1_info['title']}
- **Sesiones:** {self.plan_1_info['sessions']}
- **Ejercicios totales:** {self.plan_1_info['exercise_count']}
- **Tipo:** Inicial (is_evolutionary=false)

"""

            # Add Case 2 results
            report_content += """### CASO 2: Primera Evolución
#### Request Body
```json
{
  "user_id": "1764168881795908",
  "questionnaire_ids": ["edn360_inicial_jorge2", "edn360_seg1_jorge2"],
  "previous_training_plan_id": "PLAN_1_ID"
}
```

#### Resultado
"""
            
            case_2_result = next((r for r in self.results if "CASE 2" in r["test"]), None)
            if case_2_result:
                report_content += f"**Estado:** {'✅ EXITOSO' if case_2_result['success'] else '❌ FALLIDO'}\n"
                report_content += f"**Mensaje:** {case_2_result['message']}\n\n"
                
                if hasattr(self, 'plan_2_info'):
                    report_content += f"""#### Análisis Plan 2
- **Título:** {self.plan_2_info['title']}
- **Sesiones:** {self.plan_2_info['sessions']}
- **Ejercicios totales:** {self.plan_2_info['exercise_count']}
- **Tipo:** Evolutivo (is_evolutionary=true)
- **Plan previo usado:** {self.plan_2_info['previous_plan_id']}

"""

            # Add Case 3 results
            report_content += """### CASO 3: Segunda Evolución
#### Request Body
```json
{
  "user_id": "1764168881795908",
  "questionnaire_ids": ["edn360_inicial_jorge2", "edn360_seg2_jorge2"],
  "previous_training_plan_id": "PLAN_2_ID"
}
```

#### Resultado
"""
            
            case_3_result = next((r for r in self.results if "CASE 3" in r["test"]), None)
            if case_3_result:
                report_content += f"**Estado:** {'✅ EXITOSO' if case_3_result['success'] else '❌ FALLIDO'}\n"
                report_content += f"**Mensaje:** {case_3_result['message']}\n\n"
                
                if hasattr(self, 'plan_3_info'):
                    report_content += f"""#### Análisis Plan 3
- **Título:** {self.plan_3_info['title']}
- **Sesiones:** {self.plan_3_info['sessions']}
- **Ejercicios totales:** {self.plan_3_info['exercise_count']}
- **Tipo:** Evolutivo (is_evolutionary=true)
- **Plan previo usado:** {self.plan_3_info['previous_plan_id']}

"""

            # Add progression analysis
            if hasattr(self, 'plan_1_info') and hasattr(self, 'plan_2_info') and hasattr(self, 'plan_3_info'):
                report_content += f"""### ANÁLISIS DE PROGRESIÓN GLOBAL

#### Comparativa de Volumen/Intensidad
| Plan | Sesiones | Ejercicios | Título |
|------|----------|------------|--------|
| Plan 1 | {self.plan_1_info['sessions']} | {self.plan_1_info['exercise_count']} | {self.plan_1_info['title']} |
| Plan 2 | {self.plan_2_info['sessions']} | {self.plan_2_info['exercise_count']} | {self.plan_2_info['title']} |
| Plan 3 | {self.plan_3_info['sessions']} | {self.plan_3_info['exercise_count']} | {self.plan_3_info['title']} |

#### Efectividad del Flujo Evolutivo
- **Progresión de sesiones:** {self.plan_1_info['sessions']} → {self.plan_2_info['sessions']} → {self.plan_3_info['sessions']}
- **Progresión de ejercicios:** {self.plan_1_info['exercise_count']} → {self.plan_2_info['exercise_count']} → {self.plan_3_info['exercise_count']}
- **Estado evolutivo:** Plan 1 (inicial) → Plan 2 (evolutivo) → Plan 3 (evolutivo)

"""

            # Add conclusions
            report_content += """### CONCLUSIONES

#### Verificaciones Críticas
"""
            
            # Check critical verifications
            verifications = [
                ("✅" if any("CASE 1" in r["test"] and r["success"] for r in self.results) else "❌", "Plan inicial generado correctamente (is_evolutionary=false)"),
                ("✅" if any("CASE 2" in r["test"] and r["success"] for r in self.results) else "❌", "Primera evolución generada correctamente (is_evolutionary=true)"),
                ("✅" if any("CASE 3" in r["test"] and r["success"] for r in self.results) else "❌", "Segunda evolución generada correctamente (is_evolutionary=true)"),
                ("✅" if any("Database" in r["test"] and r["success"] for r in self.results) else "❌", "Progresión guardada correctamente en base de datos"),
            ]
            
            for status, description in verifications:
                report_content += f"- {status} {description}\n"

            # Add detailed test results
            report_content += f"""

### RESULTADOS DETALLADOS DE TESTS

"""
            
            for result in self.results:
                status = "✅ EXITOSO" if result["success"] else "❌ FALLIDO"
                report_content += f"""#### {result['test']}
- **Estado:** {status}
- **Mensaje:** {result['message']}
- **Timestamp:** {result['timestamp']}

"""

            # Write report
            with open("/app/docs/EDN360_TRAINING_E2E_TESTS_JORGE2.md", "w", encoding="utf-8") as f:
                f.write(report_content)
            
            self.log_result("Generate E2E Report", True, "Report generated successfully at /app/docs/EDN360_TRAINING_E2E_TESTS_JORGE2.md")
            return True
            
        except Exception as e:
            self.log_result("Generate E2E Report", False, f"Exception: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all E2E tests in sequence"""
        print("🚀 Starting EDN360 E2E Testing for Jorge2 Evolutionary Workflow")
        print("=" * 80)
        
        # Step 1: Admin login
        if not self.admin_login():
            print("❌ Admin login failed, cannot continue")
            return False
        
        # Step 2: Case 1 - Initial Plan
        if not self.case_1_initial_plan():
            print("❌ Case 1 failed, cannot continue to Case 2")
            return False
        
        # Wait a bit between cases
        time.sleep(2)
        
        # Step 3: Case 2 - First Evolution
        if not self.case_2_first_evolution():
            print("❌ Case 2 failed, cannot continue to Case 3")
            return False
        
        # Wait a bit between cases
        time.sleep(2)
        
        # Step 4: Case 3 - Second Evolution
        if not self.case_3_second_evolution():
            print("❌ Case 3 failed")
            return False
        
        # Step 5: Verify database progression
        self.verify_database_progression()
        
        # Step 6: Generate comprehensive report
        self.generate_report()
        
        # Summary
        successful_tests = len([r for r in self.results if r['success']])
        total_tests = len(self.results)
        
        print("\n" + "=" * 80)
        print(f"🏁 EDN360 E2E Testing Complete: {successful_tests}/{total_tests} tests passed")
        
        if successful_tests == total_tests:
            print("✅ All tests passed! Evolutionary workflow is working correctly.")
            return True
        else:
            print("❌ Some tests failed. Check the detailed report for issues.")
            return False

def main():
    """Main execution function"""
    tester = EDN360E2ETester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ EDN360 E2E Testing completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ EDN360 E2E Testing completed with failures!")
        sys.exit(1)

if __name__ == "__main__":
    main()