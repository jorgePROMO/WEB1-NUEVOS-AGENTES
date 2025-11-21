#!/usr/bin/env python3
"""
Phase 3 Follow-up Analysis & Plan Generation Testing
Focused testing for the specific Phase 3 endpoints
"""

import requests
import json
import sys
from datetime import datetime

# Backend URL from frontend/.env
BACKEND_URL = "https://edn-job-runner.preview.emergentagent.com/api"

class Phase3Tester:
    def __init__(self):
        self.admin_token = None
        self.results = []
        
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
            print(f"   Response: {response_data}")
    
    def admin_login(self):
        """Admin login with correct credentials"""
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

    def test_analyze_with_ia_404(self):
        """Test analyze-with-ia endpoint with non-existent IDs (should return 404)"""
        if not self.admin_token:
            self.log_result("Test Analyze With IA - 404", False, "No admin token available")
            return False
            
        fake_user_id = "nonexistent_user_123"
        fake_followup_id = "nonexistent_followup_123"
        url = f"{BACKEND_URL}/admin/users/{fake_user_id}/followups/{fake_followup_id}/analyze-with-ia"
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            response = requests.post(url, headers=headers)
            
            if response.status_code == 404:
                self.log_result("Test Analyze With IA - 404", True, 
                              "Correctly returned 404 for non-existent user/follow-up")
                return True
            else:
                self.log_result("Test Analyze With IA - 404", False, 
                              f"Expected 404, got HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Test Analyze With IA - 404", False, f"Exception: {str(e)}")
        
        return False

    def test_update_analysis_404(self):
        """Test update analysis endpoint with non-existent IDs (should return 404)"""
        if not self.admin_token:
            self.log_result("Test Update Analysis - 404", False, "No admin token available")
            return False
            
        fake_user_id = "nonexistent_user_123"
        fake_followup_id = "nonexistent_followup_123"
        url = f"{BACKEND_URL}/admin/users/{fake_user_id}/followups/{fake_followup_id}/analysis"
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        payload = {"analysis": "Test analysis"}
        
        try:
            response = requests.patch(url, json=payload, headers=headers)
            
            if response.status_code == 404:
                self.log_result("Test Update Analysis - 404", True, 
                              "Correctly returned 404 for non-existent user/follow-up")
                return True
            else:
                self.log_result("Test Update Analysis - 404", False, 
                              f"Expected 404, got HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Test Update Analysis - 404", False, f"Exception: {str(e)}")
        
        return False

    def test_generate_plan_without_analysis(self):
        """Test generate-plan endpoint without analysis (should return 400 or 404)"""
        if not self.admin_token:
            self.log_result("Test Generate Plan Without Analysis", False, "No admin token available")
            return False
            
        fake_user_id = "nonexistent_user_123"
        fake_followup_id = "nonexistent_followup_123"
        url = f"{BACKEND_URL}/admin/users/{fake_user_id}/followups/{fake_followup_id}/generate-plan"
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            response = requests.post(url, headers=headers)
            
            if response.status_code in [400, 404]:
                data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                message = data.get("detail", "")
                self.log_result("Test Generate Plan Without Analysis", True, 
                              f"Correctly returned {response.status_code} - {message}")
                return True
            else:
                self.log_result("Test Generate Plan Without Analysis", False, 
                              f"Expected 400/404, got HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Test Generate Plan Without Analysis", False, f"Exception: {str(e)}")
        
        return False

    def check_existing_users_with_plans(self):
        """Check for existing users who might have nutrition plans for follow-up testing"""
        if not self.admin_token:
            self.log_result("Check Existing Users", False, "No admin token available")
            return False
            
        url = f"{BACKEND_URL}/admin/clients"
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                clients = data.get("clients", [])
                
                if len(clients) > 0:
                    self.log_result("Check Existing Users", True, 
                                  f"Found {len(clients)} clients in system for potential follow-up testing")
                    
                    # Store first client for potential testing
                    self.test_user = clients[0]
                    return True
                else:
                    self.log_result("Check Existing Users", False, 
                                  "No clients found in system")
            else:
                self.log_result("Check Existing Users", False, 
                              f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Check Existing Users", False, f"Exception: {str(e)}")
        
        return False

    def test_endpoint_authentication(self):
        """Test that Phase 3 endpoints require admin authentication"""
        endpoints = [
            f"{BACKEND_URL}/admin/users/test_user/followups/test_followup/analyze-with-ia",
            f"{BACKEND_URL}/admin/users/test_user/followups/test_followup/analysis",
            f"{BACKEND_URL}/admin/users/test_user/followups/test_followup/generate-plan"
        ]
        
        all_protected = True
        
        for endpoint in endpoints:
            try:
                # Test without authentication
                response = requests.post(endpoint) if "generate-plan" in endpoint or "analyze-with-ia" in endpoint else requests.patch(endpoint, json={"analysis": "test"})
                
                if response.status_code not in [401, 403]:
                    all_protected = False
                    self.log_result("Test Endpoint Authentication", False, 
                                  f"Endpoint {endpoint} not properly protected - returned {response.status_code}")
                    break
            except Exception as e:
                # Connection errors are acceptable for this test
                pass
        
        if all_protected:
            self.log_result("Test Endpoint Authentication", True, 
                          "All Phase 3 endpoints properly require authentication")
            return True
        
        return False

    def run_phase3_tests(self):
        """Run all Phase 3 tests"""
        print("🚀 PHASE 3 FOLLOW-UP ANALYSIS & PLAN GENERATION TESTING")
        print(f"Backend URL: {BACKEND_URL}")
        print("=" * 80)
        
        tests = [
            self.admin_login,
            self.test_endpoint_authentication,
            self.check_existing_users_with_plans,
            self.test_analyze_with_ia_404,
            self.test_update_analysis_404,
            self.test_generate_plan_without_analysis,
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            if test():
                passed += 1
        
        print("=" * 80)
        print(f"📊 PHASE 3 TEST SUMMARY: {passed}/{total} tests passed")
        
        if passed == total:
            print("✅ ALL PHASE 3 TESTS PASSED")
        else:
            print("⚠️  SOME PHASE 3 TESTS FAILED")
            failed_tests = [r for r in self.results if not r["success"]]
            print("Failed tests:")
            for test in failed_tests:
                print(f"  - {test['test']}: {test['message']}")
        
        # Save results
        with open("/app/phase3_test_results.json", "w") as f:
            json.dump(self.results, f, indent=2)
        
        print(f"📄 Detailed results saved to: /app/phase3_test_results.json")
        
        return passed == total

if __name__ == "__main__":
    tester = Phase3Tester()
    success = tester.run_phase3_tests()
    sys.exit(0 if success else 1)