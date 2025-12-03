#!/usr/bin/env python3
"""
EDN360 E2E Testing - 3 Scenario Evolutionary Flow
Tests the complete evolutionary training plan generation flow for user Jorge2
"""

import requests
import json
import sys
import os
import time
from datetime import datetime

# Backend URL from frontend/.env
BACKEND_URL = "https://edn360-audit.preview.emergentagent.com/api"

class EDN360E2ETester:
    def __init__(self):
        self.admin_token = None
        self.test_results = []
        self.jorge2_user_id = "1764168881795908"
        self.captured_data = {
            "scenario_1": {},
            "scenario_2": {},
            "scenario_3": {}
        }
        
    def log_result(self, test_name, success, message, response_data=None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        if response_data and not success:
            print(f"   Response: {response_data}")
    
    def admin_login(self):
        """Admin login for testing"""
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
    
    def check_user_exists(self):
        """Check if Jorge2 user exists"""
        if not self.admin_token:
            self.log_result("Check User Exists", False, "No admin token available")
            return False
            
        url = f"{BACKEND_URL}/admin/clients/{self.jorge2_user_id}"
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                user = data.get("user", {})
                self.log_result("Check User Exists", True, 
                              f"Jorge2 user found: {user.get('name', 'N/A')} ({user.get('email', 'N/A')})")
                return True
            elif response.status_code == 404:
                self.log_result("Check User Exists", False, 
                              f"Jorge2 user {self.jorge2_user_id} not found")
                return False
            else:
                self.log_result("Check User Exists", False, 
                              f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Check User Exists", False, f"Exception: {str(e)}")
        
        return False
    
    def check_microservice_health(self):
        """Check EDN360 microservice health"""
        try:
            health_url = "http://localhost:4000/health"
            response = requests.get(health_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") in ["healthy", "ok"]:
                    self.log_result("Microservice Health", True, 
                                  f"EDN360 microservice healthy: {data}")
                    return True
                else:
                    self.log_result("Microservice Health", False, 
                                  f"Microservice not healthy: {data}")
            else:
                self.log_result("Microservice Health", False, 
                              f"Health check failed: HTTP {response.status_code}")
        except Exception as e:
            self.log_result("Microservice Health", False, f"Exception: {str(e)}")
        
        return False
    
    def execute_training_plan_scenario(self, scenario_name, scenario_number):
        """Execute a training plan generation scenario"""
        if not self.admin_token:
            self.log_result(f"Execute {scenario_name}", False, "No admin token available")
            return False
            
        url = f"{BACKEND_URL}/training-plan"
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        # Use existing questionnaire ID for Jorge2
        questionnaire_id = "1764713509409284"
        
        # Prepare request body
        request_body = {
            "user_id": self.jorge2_user_id,
            "questionnaire_ids": [questionnaire_id],
            "previous_training_plan_id": None  # Let system determine evolution
        }
        
        try:
            print(f"\n🎯 EXECUTING {scenario_name.upper()}")
            print(f"   User ID: {self.jorge2_user_id}")
            print(f"   Questionnaire ID: {questionnaire_id}")
            print(f"   Request Body: {json.dumps(request_body, indent=2)}")
            
            # Capture request body
            scenario_key = f"scenario_{scenario_number}"
            self.captured_data[scenario_key]["request_body"] = request_body
            
            # Make the API call with extended timeout
            response = requests.post(url, json=request_body, headers=headers, timeout=180)
            
            print(f"   Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Capture final response
                self.captured_data[scenario_key]["final_response"] = data
                
                # Validate response structure
                if "client_training_program_enriched" in data:
                    training_program = data["client_training_program_enriched"]
                    is_evolutionary = data.get("is_evolutionary", False)
                    
                    # Validate sessions structure
                    sessions = training_program.get("sessions", [])
                    if sessions and len(sessions) > 0:
                        # Check exercise structure
                        total_exercises = 0
                        all_have_db_id = True
                        all_have_video_url = True
                        
                        for session in sessions:
                            blocks = session.get("blocks", [])
                            for block in blocks:
                                exercises = block.get("exercises", [])
                                total_exercises += len(exercises)
                                
                                for exercise in exercises:
                                    if not exercise.get("db_id"):
                                        all_have_db_id = False
                                    if not exercise.get("video_url"):
                                        all_have_video_url = False
                        
                        self.log_result(f"Execute {scenario_name}", True, 
                                      f"✅ SUCCESS: Sessions={len(sessions)}, Exercises={total_exercises}, "
                                      f"Has db_id={all_have_db_id}, Has video_url={all_have_video_url}, "
                                      f"Is_evolutionary={is_evolutionary}")
                        
                        # Store validation results
                        self.captured_data[scenario_key]["validation_results"] = {
                            "http_status": response.status_code,
                            "number_of_sessions": len(sessions),
                            "total_exercises": total_exercises,
                            "all_exercises_have_db_id": all_have_db_id,
                            "all_exercises_have_video_url": all_have_video_url,
                            "is_evolutionary": is_evolutionary
                        }
                        
                        return True
                    else:
                        self.log_result(f"Execute {scenario_name}", False, 
                                      "Training program has no sessions")
                else:
                    self.log_result(f"Execute {scenario_name}", False, 
                                  "Response missing client_training_program_enriched", data)
            else:
                error_data = response.text
                try:
                    error_json = response.json()
                    error_data = error_json
                except:
                    pass
                
                self.log_result(f"Execute {scenario_name}", False, 
                              f"HTTP {response.status_code}", error_data)
                
                # Store error response
                self.captured_data[scenario_key]["error_response"] = {
                    "status_code": response.status_code,
                    "error_data": error_data
                }
        
        except Exception as e:
            self.log_result(f"Execute {scenario_name}", False, f"Exception: {str(e)}")
            self.captured_data[scenario_key]["exception"] = str(e)
        
        return False
    
    def capture_backend_logs(self):
        """Capture backend logs for STATE object construction"""
        try:
            import subprocess
            
            # Get recent backend logs
            cmd = "tail -n 100 /var/log/supervisor/backend.*.log | grep -E '(STATE construido|Cuestionarios recuperados|Planes previos recuperados|Objeto STATE construido)'"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0 and result.stdout.strip():
                logs = result.stdout.strip()
                self.log_result("Capture Backend Logs", True, 
                              f"Backend logs captured: {len(logs.split('\n'))} relevant lines")
                
                # Store logs in captured data
                for scenario_key in self.captured_data.keys():
                    self.captured_data[scenario_key]["backend_logs"] = logs
                
                return logs
            else:
                self.log_result("Capture Backend Logs", False, 
                              "No relevant backend logs found")
                return None
        except Exception as e:
            self.log_result("Capture Backend Logs", False, f"Exception: {str(e)}")
            return None
    
    def capture_microservice_logs(self):
        """Capture microservice logs for workflow execution"""
        try:
            import subprocess
            
            # Get recent microservice logs
            cmd = "tail -n 100 /var/log/supervisor/edn360-workflow-service.*.log"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0 and result.stdout.strip():
                logs = result.stdout.strip()
                self.log_result("Capture Microservice Logs", True, 
                              f"Microservice logs captured: {len(logs.split('\n'))} lines")
                return logs
            else:
                self.log_result("Capture Microservice Logs", False, 
                              "No microservice logs found")
                return None
        except Exception as e:
            self.log_result("Capture Microservice Logs", False, f"Exception: {str(e)}")
            return None
    
    def create_documentation(self):
        """Create comprehensive documentation of test results"""
        try:
            # Ensure docs directory exists
            os.makedirs("/app/docs", exist_ok=True)
            
            doc_content = f"""# EDN360 E2E Testing Results - Jorge2 User
            
## Test Execution Summary
- **User ID**: {self.jorge2_user_id}
- **Test Date**: {datetime.now().isoformat()}
- **Total Scenarios**: 3
- **Backend URL**: {BACKEND_URL}

## Test Results Overview
"""
            
            # Add scenario results
            for i, scenario_key in enumerate(["scenario_1", "scenario_2", "scenario_3"], 1):
                scenario_name = f"Scenario {i}"
                if scenario_key == "scenario_1":
                    scenario_name += ": INITIAL PLAN (No History)"
                elif scenario_key == "scenario_2":
                    scenario_name += ": FIRST FOLLOW-UP (With Initial Plan)"
                else:
                    scenario_name += ": SECOND FOLLOW-UP (With Multiple Plans)"
                
                doc_content += f"""
## {scenario_name}

### Request Body
```json
{json.dumps(self.captured_data[scenario_key].get("request_body", {}), indent=2)}
```

### STATE Object
```
{self.captured_data[scenario_key].get("backend_logs", "Backend logs not captured")}
```

### Final Response
```json
{json.dumps(self.captured_data[scenario_key].get("final_response", {}), indent=2)}
```

### Validation Results
"""
                
                validation = self.captured_data[scenario_key].get("validation_results", {})
                if validation:
                    doc_content += f"""- HTTP Status: {validation.get('http_status', 'N/A')}
- Number of Sessions: {validation.get('number_of_sessions', 'N/A')}
- Total Exercises: {validation.get('total_exercises', 'N/A')}
- All exercises have db_id: {'Yes' if validation.get('all_exercises_have_db_id') else 'No'}
- All exercises have video_url: {'Yes' if validation.get('all_exercises_have_video_url') else 'No'}
- Is Evolutionary: {'Yes' if validation.get('is_evolutionary') else 'No'}
"""
                else:
                    doc_content += "- Test failed or incomplete\n"
                
                # Add error information if present
                if "error_response" in self.captured_data[scenario_key]:
                    error = self.captured_data[scenario_key]["error_response"]
                    doc_content += f"""
### Error Details
- Status Code: {error.get('status_code', 'N/A')}
- Error Data: {json.dumps(error.get('error_data', {}), indent=2)}
"""
                
                if "exception" in self.captured_data[scenario_key]:
                    doc_content += f"""
### Exception
```
{self.captured_data[scenario_key]['exception']}
```
"""
            
            # Add test summary
            doc_content += f"""
## Test Execution Log

"""
            for result in self.test_results:
                status = "✅" if result["success"] else "❌"
                doc_content += f"- {status} **{result['test']}**: {result['message']}\n"
            
            # Write documentation file
            doc_path = "/app/docs/EDN360_TRAINING_E2E_TESTS_JORGE2.md"
            with open(doc_path, "w", encoding="utf-8") as f:
                f.write(doc_content)
            
            self.log_result("Create Documentation", True, 
                          f"Documentation created at {doc_path}")
            return True
            
        except Exception as e:
            self.log_result("Create Documentation", False, f"Exception: {str(e)}")
            return False
    
    def run_comprehensive_test(self):
        """Run the complete E2E test suite"""
        print("🚀 Starting EDN360 E2E Testing - 3 Scenario Evolutionary Flow")
        print("=" * 70)
        
        # Setup Phase
        print("\n📋 SETUP PHASE")
        if not self.admin_login():
            return False
        
        if not self.check_user_exists():
            print("❌ Jorge2 user not found. Cannot proceed with testing.")
            return False
        
        if not self.check_microservice_health():
            print("⚠️  Microservice health check failed. Proceeding anyway...")
        
        # Execution Phase
        print("\n🎯 EXECUTION PHASE")
        
        # Scenario 1: Initial Plan (No History)
        self.execute_training_plan_scenario("Scenario 1 - Initial Plan", 1)
        time.sleep(2)  # Brief pause between scenarios
        
        # Scenario 2: First Follow-up (With Initial Plan)
        self.execute_training_plan_scenario("Scenario 2 - First Follow-up", 2)
        time.sleep(2)  # Brief pause between scenarios
        
        # Scenario 3: Second Follow-up (With Multiple Plans)
        self.execute_training_plan_scenario("Scenario 3 - Second Follow-up", 3)
        
        # Documentation Phase
        print("\n📝 DOCUMENTATION PHASE")
        self.capture_backend_logs()
        self.capture_microservice_logs()
        self.create_documentation()
        
        # Summary
        print("\n📊 TEST SUMMARY")
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        return failed_tests == 0

def main():
    """Main execution function"""
    tester = EDN360E2ETester()
    success = tester.run_comprehensive_test()
    
    if success:
        print("\n🎉 All tests passed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Check the logs above.")
        sys.exit(1)

if __name__ == "__main__":
    main()