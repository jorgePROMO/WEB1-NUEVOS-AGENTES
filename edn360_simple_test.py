#!/usr/bin/env python3
"""
EDN360 Simple Test - Basic functionality verification
"""

import requests
import json
import sys
import os
from datetime import datetime

# Use local backend for testing
BACKEND_URL = "http://localhost:8001/api"

def test_admin_login():
    """Test admin login"""
    url = f"{BACKEND_URL}/auth/login"
    params = {
        "email": "ecjtrainer@gmail.com",
        "password": "jorge3007"
    }
    
    try:
        response = requests.post(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if "user" in data and "token" in data and data["user"].get("role") == "admin":
                print("✅ Admin login successful")
                return data["token"]
            else:
                print("❌ Admin login failed - invalid response")
                return None
        else:
            print(f"❌ Admin login failed - HTTP {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Admin login exception: {e}")
        return None

def test_user_exists(admin_token):
    """Test if Jorge2 user exists"""
    user_id = "1764168881795908"
    url = f"{BACKEND_URL}/admin/clients/{user_id}"
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            user = data.get("user", {})
            print(f"✅ Jorge2 user found: {user.get('name', 'N/A')} ({user.get('email', 'N/A')})")
            return True
        elif response.status_code == 404:
            print(f"❌ Jorge2 user {user_id} not found")
            return False
        else:
            print(f"❌ User check failed - HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ User check exception: {e}")
        return False

def test_microservice_health():
    """Test microservice health"""
    try:
        health_url = "http://localhost:4000/health"
        response = requests.get(health_url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status") in ["healthy", "ok"]:
                print(f"✅ Microservice healthy: {data}")
                return True
            else:
                print(f"❌ Microservice not healthy: {data}")
                return False
        else:
            print(f"❌ Microservice health check failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Microservice health check exception: {e}")
        return False

def test_training_plan_mock(admin_token):
    """Test mock training plan endpoint"""
    user_id = "1764168881795908"
    url = f"{BACKEND_URL}/training-plan/mock"
    headers = {"Authorization": f"Bearer {admin_token}"}
    payload = {"user_id": user_id}
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if "client_training_program_enriched" in data:
                training_program = data["client_training_program_enriched"]
                sessions = training_program.get("sessions", [])
                print(f"✅ Mock training plan works: {len(sessions)} sessions")
                return True
            else:
                print("❌ Mock training plan - invalid response structure")
                return False
        else:
            print(f"❌ Mock training plan failed - HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Mock training plan exception: {e}")
        return False

def capture_backend_state():
    """Capture current backend state from logs"""
    try:
        import subprocess
        
        # Get recent backend logs
        cmd = "tail -n 50 /var/log/supervisor/backend.*.log | grep -E '(STATE construido|Cuestionarios recuperados|Planes previos recuperados)'"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0 and result.stdout.strip():
            logs = result.stdout.strip()
            print(f"✅ Backend logs captured:")
            for line in logs.split('\n')[-5:]:  # Show last 5 relevant lines
                print(f"   {line}")
            return True
        else:
            print("❌ No relevant backend logs found")
            return False
    except Exception as e:
        print(f"❌ Backend logs exception: {e}")
        return False

def main():
    """Main test execution"""
    print("🧪 EDN360 Simple Test - Basic Functionality Verification")
    print("=" * 60)
    
    # Test admin login
    print("\n1. Testing Admin Login...")
    admin_token = test_admin_login()
    if not admin_token:
        print("❌ Cannot proceed without admin token")
        return False
    
    # Test user exists
    print("\n2. Testing Jorge2 User Exists...")
    if not test_user_exists(admin_token):
        print("❌ Cannot proceed without Jorge2 user")
        return False
    
    # Test microservice health
    print("\n3. Testing Microservice Health...")
    microservice_healthy = test_microservice_health()
    
    # Test mock endpoint
    print("\n4. Testing Mock Training Plan...")
    mock_works = test_training_plan_mock(admin_token)
    
    # Capture backend state
    print("\n5. Capturing Backend State...")
    capture_backend_state()
    
    # Summary
    print("\n📊 TEST SUMMARY")
    print(f"Admin Login: {'✅' if admin_token else '❌'}")
    print(f"Jorge2 User: ✅")
    print(f"Microservice: {'✅' if microservice_healthy else '❌'}")
    print(f"Mock Endpoint: {'✅' if mock_works else '❌'}")
    
    if admin_token and mock_works:
        print("\n✅ Basic functionality verified - System is ready for testing")
        return True
    else:
        print("\n❌ Some basic functionality issues detected")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)