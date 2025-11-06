#!/usr/bin/env python3
"""
Check available routes in the FastAPI app
"""

import sys
sys.path.append('/app/backend')

from server import app

print("Available routes:")
for route in app.routes:
    if hasattr(route, 'path') and hasattr(route, 'methods'):
        print(f"{list(route.methods)} {route.path}")