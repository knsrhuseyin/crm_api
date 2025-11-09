#!/bin/bash
git pull origin main
clear
source venv/bin/activate
uvicorn main:app --log-level info > server.log
