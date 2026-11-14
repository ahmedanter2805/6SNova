@echo off
title AURA - Planetary Climate Intelligence SaaS Platform
echo ============================================================
echo   AURA // Planetary Climate Intelligence Platform
echo   NASA Space Apps Challenge 2026 | Enterprise SaaS
echo ============================================================
echo Starting local server on http://localhost:8000 ...
start http://localhost:8000
python run_server.py
pause
