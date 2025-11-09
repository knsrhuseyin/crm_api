#!/bin/bash
git pull origin main
source venv/bin/activate
uvicorn main:app --log-level info > server.log
