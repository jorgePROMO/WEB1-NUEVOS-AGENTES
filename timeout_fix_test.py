#!/usr/bin/env python3
"""
EDN360 Timeout Fix Validation Test
Single E2E test for Jorge2 to validate the timeout fix implementation
"""

import requests
import json
import sys
import os
from datetime import datetime

# Backend URL from frontend/.env
BACKEND_URL = "https://workout-forge-6.preview.emergentagent.com/api"

class TimeoutFixTester:
    def __init__(self):
        self.admin_token = None
        
    def log_result(self, test_name, success, message, response_data=None):
        """Log test result"""
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

    def test_timeout_fix_validation_jorge2(self):
        """
        TIMEOUT FIX VALIDATION - Single E2E Test for Jorge2
        
        Tests the fixed timeout implementation with ONE scenario:
        - User: Jorge2 (ID: 1764168881795908)
        - Questionnaire: 1764713509409284
        - Endpoint: POST /api/training-plan
        - Expected: HTTP 200, full response, no timeout
        """
        if not self.admin_token:
            self.log_result("Timeout Fix Validation - Jorge2", False, "No admin token available")
            return False
            
        # Specific test data from review request
        user_id = "1764168881795908"
        current_questionnaire_id = "1764713509409284"
        
        url = f"{BACKEND_URL}/training-plan"
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        payload = {
            "user_id": user_id,
            "questionnaire_ids": [current_questionnaire_id]
        }
        
        try:
            print(f"\n🎯 TIMEOUT FIX VALIDATION - Single E2E Test")
            print(f"   User: Jorge2 (ID: {user_id})")
            print(f"   Questionnaire: {current_questionnaire_id}")
            print(f"   Testing timeout fix implementation...")
            
            start_time = datetime.now()
            
            # Extended timeout for workflow completion (5 minutes as per review request)
            response = requests.post(url, json=payload, headers=headers, timeout=300)
            
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            print(f"   Execution time: {execution_time:.2f} seconds")
            
            if response.status_code == 200:
                data = response.json()
                
                # Critical checks from review request
                if "client_training_program_enriched" in data:
                    training_program = data["client_training_program_enriched"]
                    
                    # Check sessions array exists
                    if "sessions" in training_program and len(training_program["sessions"]) > 0:
                        sessions = training_program["sessions"]
                        
                        # Check exercises have required fields
                        exercises_valid = True
                        exercise_count = 0
                        sample_exercises = []
                        
                        for session in sessions:
                            for block in session.get("blocks", []):
                                for exercise in block.get("exercises", []):
                                    exercise_count += 1
                                    
                                    # Store first 2 exercises as samples
                                    if len(sample_exercises) < 2:
                                        sample_exercises.append({
                                            "name": exercise.get("name", "N/A"),
                                            "db_id": exercise.get("db_id", "N/A"),
                                            "video_url": exercise.get("video_url", "N/A")
                                        })
                                    
                                    # Check required fields
                                    if not all(field in exercise for field in ["db_id", "name", "video_url"]):
                                        exercises_valid = False
                        
                        if exercises_valid and exercise_count > 0:
                            # SUCCESS - Create validation document
                            validation_doc = f"""# EDN360 TIMEOUT FIX VALIDATION

## Test Execution Summary
- **Timestamp**: {start_time.isoformat()}
- **User**: Jorge2 (ID: {user_id})
- **Questionnaire**: {current_questionnaire_id}
- **HTTP Status**: 200 OK
- **Execution Time**: {execution_time:.2f} seconds
- **Workflow Status**: ✅ COMPLETED SUCCESSFULLY

## Response Analysis
- **Sessions Count**: {len(sessions)}
- **Total Exercises**: {exercise_count}
- **Exercises Enriched**: ✅ All exercises have db_id, name, video_url
- **Response Size**: {len(str(data))} characters

## Sample Exercise Data
{json.dumps(sample_exercises, indent=2)}

## Validation Results
✅ HTTP 200 received
✅ Full client_training_program_enriched in response  
✅ No timeout errors (completed in {execution_time:.2f}s < 300s limit)
✅ All exercises enriched with database data
✅ Workflow executed successfully without hanging

## Conclusion
The timeout fix implementation is **WORKING CORRECTLY**. The EDN360 workflow now completes successfully for Jorge2 without the previous E7.5 hanging issue.
"""
                            
                            # Write validation document
                            try:
                                import os
                                os.makedirs("/app/docs", exist_ok=True)
                                with open("/app/docs/EDN360_TIMEOUT_FIX_VALIDATION.md", "w") as f:
                                    f.write(validation_doc)
                                
                                self.log_result("Timeout Fix Validation - Jorge2", True, 
                                              f"✅ TIMEOUT FIX SUCCESSFUL: HTTP 200, {len(sessions)} sessions, {exercise_count} exercises, {execution_time:.2f}s execution time. Validation doc created.")
                                return True
                            except Exception as doc_error:
                                self.log_result("Timeout Fix Validation - Jorge2", True, 
                                              f"✅ TIMEOUT FIX SUCCESSFUL: HTTP 200, {len(sessions)} sessions, {exercise_count} exercises, {execution_time:.2f}s execution time. Doc creation failed: {doc_error}")
                                return True
                        else:
                            self.log_result("Timeout Fix Validation - Jorge2", False, 
                                          f"Exercises not properly enriched: valid={exercises_valid}, count={exercise_count}")
                    else:
                        self.log_result("Timeout Fix Validation - Jorge2", False, 
                                      "Response missing sessions array or empty sessions")
                else:
                    self.log_result("Timeout Fix Validation - Jorge2", False, 
                                  "Response missing client_training_program_enriched")
            elif response.status_code in [500, 502]:
                # Capture error details for timeout issues
                error_text = response.text
                self.log_result("Timeout Fix Validation - Jorge2", False, 
                              f"❌ TIMEOUT/SERVER ERROR: HTTP {response.status_code} after {execution_time:.2f}s. Error: {error_text[:200]}...")
            else:
                self.log_result("Timeout Fix Validation - Jorge2", False, 
                              f"HTTP {response.status_code} after {execution_time:.2f}s", response.text)
        except requests.exceptions.Timeout:
            self.log_result("Timeout Fix Validation - Jorge2", False, 
                          f"❌ REQUEST TIMEOUT: Workflow did not complete within 300 seconds")
        except Exception as e:
            self.log_result("Timeout Fix Validation - Jorge2", False, f"Exception: {str(e)}")
        
        return False

    def run_test(self):
        """Run the single timeout fix validation test"""
        print("🎯 EDN360 TIMEOUT FIX VALIDATION TEST")
        print(f"Backend URL: {BACKEND_URL}")
        print("=" * 60)
        
        # Step 1: Admin login
        if not self.admin_login():
            print("❌ Cannot proceed without admin login")
            return False
        
        # Step 2: Run timeout fix validation
        success = self.test_timeout_fix_validation_jorge2()
        
        print("\n" + "=" * 60)
        if success:
            print("🎉 TIMEOUT FIX VALIDATION: SUCCESS")
            print("✅ The EDN360 workflow timeout fix is working correctly!")
        else:
            print("💥 TIMEOUT FIX VALIDATION: FAILED")
            print("❌ The timeout fix needs further investigation")
        
        return success

if __name__ == "__main__":
    tester = TimeoutFixTester()
    success = tester.run_test()
    sys.exit(0 if success else 1)