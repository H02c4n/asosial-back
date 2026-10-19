#!/bin/bash
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "Test1234!"}' \
  | python -c "import sys, json; print(json.load(sys.stdin)['access'])")

wscat -c "ws://127.0.0.1:8000/ws/notifications/?token=$TOKEN"
