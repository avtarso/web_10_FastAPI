#!/bin/bash
alembic revision --autogenerate -m "Create table contacts"
alembic upgrade head
python seed.py
kill -9 $(lsof -t -i:8000)
uvicorn main_simple:app

