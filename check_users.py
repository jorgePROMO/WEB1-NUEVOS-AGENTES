#!/usr/bin/env python3
"""
Check users and nutrition plans in the system
"""

import requests
import json

# Backend URL
BACKEND_URL = "https://waitlistsys.preview.emergentagent.com/api"

# Admin login
login_response = requests.post(f"{BACKEND_URL}/auth/login", params={
    "email": "ecjtrainer@gmail.com",
    "password": "jorge3007"
})

if login_response.status_code == 200:
    admin_token = login_response.json()["token"]
    
    # Get all clients
    clients_response = requests.get(f"{BACKEND_URL}/admin/clients", 
                                  headers={"Authorization": f"Bearer {admin_token}"})
    
    if clients_response.status_code == 200:
        clients_data = clients_response.json()
        clients = clients_data.get("clients", [])
        
        print(f"Total clients: {len(clients)}")
        
        team_clients = [c for c in clients if c.get("subscription", {}).get("plan") == "team"]
        print(f"Team clients: {len(team_clients)}")
        
        for client in team_clients[:5]:  # Show first 5 team clients
            print(f"- {client.get('name', 'No name')} ({client.get('email')}) - ID: {client.get('id')}")
            if 'nutrition_plan' in client:
                print(f"  Has nutrition plan: {client['nutrition_plan']}")
            else:
                print(f"  No nutrition plan")
    else:
        print(f"Failed to get clients: {clients_response.status_code}")
else:
    print(f"Failed to login: {login_response.status_code}")