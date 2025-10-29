#!/bin/bash
source venv/bin/activate
uvicorn main:app --log-level info > server.log
