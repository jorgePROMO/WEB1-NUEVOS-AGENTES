#!/usr/bin/env python3
"""
EDN360 Single Scenario Test - Test one scenario with detailed logging
"""

import requests
import json
import sys
import os
from datetime import datetime

# Use local backend for testing
BACKEND_URL = "http://localhost:8001/api"

def test_single_scenario():
    """Test a single training plan scenario"""
    
    # Admin login
    url = f"{BACKEND_URL}/auth/login"
    params = {
        "email": "ecjtrainer@gmail.com",
        "password": "jorge3007"
    }
    
    try:
        response = requests.post(url, params=params, timeout=10)
        if response.status_code != 200:
            print(f"❌ Admin login failed: {response.status_code}")
            return False
        
        admin_token = response.json()["token"]
        print("✅ Admin login successful")
        
    except Exception as e:
        print(f"❌ Admin login exception: {e}")
        return False
    
    # Test training plan generation
    user_id = "1764168881795908"
    questionnaire_id = "1764713509409284"
    
    url = f"{BACKEND_URL}/training-plan"
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    request_body = {
        "user_id": user_id,
        "questionnaire_ids": [questionnaire_id],
        "previous_training_plan_id": None
    }
    
    print(f"\n🎯 Testing Training Plan Generation")
    print(f"   User ID: {user_id}")
    print(f"   Questionnaire ID: {questionnaire_id}")
    print(f"   Request Body: {json.dumps(request_body, indent=2)}")
    
    try:
        print("   Making API call with 60 second timeout...")
        response = requests.post(url, json=request_body, headers=headers, timeout=60)
        
        print(f"   Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if "client_training_program_enriched" in data:
                training_program = data["client_training_program_enriched"]
                is_evolutionary = data.get("is_evolutionary", False)
                sessions = training_program.get("sessions", [])
                
                print(f"✅ SUCCESS!")
                print(f"   Is Evolutionary: {is_evolutionary}")
                print(f"   Sessions: {len(sessions)}")
                print(f"   Title: {training_program.get('title', 'N/A')}")
                
                # Count exercises
                total_exercises = 0
                for session in sessions:
                    blocks = session.get("blocks", [])
                    for block in blocks:
                        exercises = block.get("exercises", [])
                        total_exercises += len(exercises)
                
                print(f"   Total Exercises: {total_exercises}")
                
                return True
            else:
                print(f"❌ Invalid response structure")
                print(f"   Response keys: {list(data.keys())}")
                return False
        
        elif response.status_code == 500:
            print(f"❌ Server error (500)")
            try:
                error_data = response.json()
                print(f"   Error: {error_data}")
            except:
                print(f"   Raw error: {response.text}")
            return False
        
        else:
            print(f"❌ HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    
    except requests.exceptions.Timeout:
        print("❌ Request timed out after 60 seconds")
        print("   This indicates the microservice workflow is hanging")
        return False
    
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def capture_logs_after_test():
    """Capture logs after test execution"""
    try:
        import subprocess
        
        print("\n📋 Capturing Backend Logs...")
        cmd = "tail -n 20 /var/log/supervisor/backend.*.log"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("Backend logs:")
            for line in result.stdout.strip().split('\n')[-10:]:
                print(f"   {line}")
        
        print("\n📋 Capturing Microservice Logs...")
        cmd = "tail -n 20 /var/log/supervisor/edn360-workflow-service.*.log"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("Microservice logs:")
            for line in result.stdout.strip().split('\n')[-10:]:
                print(f"   {line}")
        
    except Exception as e:
        print(f"❌ Log capture exception: {e}")

def main():
    """Main test execution"""
    print("🧪 EDN360 Single Scenario Test")
    print("=" * 40)
    
    success = test_single_scenario()
    
    # Always capture logs
    capture_logs_after_test()
    
    print(f"\n📊 RESULT: {'✅ SUCCESS' if success else '❌ FAILED'}")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)