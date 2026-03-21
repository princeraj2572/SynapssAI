#!/usr/bin/env python
"""Check backend API endpoints"""
import sys
sys.path.insert(0, '.')

from main import app

# Get all routes
routes = []
for route in app.routes:
    if hasattr(route, 'path') and hasattr(route, 'methods'):
        routes.append({
            'path': route.path,
            'methods': list(route.methods) if route.methods else []
        })

# Print summary
print('✓ Backend API loaded successfully')
print(f'  Title: {app.title}')
print(f'  Version: {app.version}')
print(f'  Routes: {len([r for r in routes if r["methods"]])}')
print()
print('API Endpoints:')
for r in sorted(routes, key=lambda x: x['path']):
    if r['methods']:
        methods = ','.join(sorted(r['methods']))
        print(f'  {methods:20} {r["path"]}')
