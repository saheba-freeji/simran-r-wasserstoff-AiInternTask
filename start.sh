#!/bin/bash
cd backend && uvicorn app.main:app --reload & 
cd frontend && streamlit run app.py
