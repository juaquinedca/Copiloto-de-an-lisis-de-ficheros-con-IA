@echo off
title Asistente de Analisis de Datos IA
echo =======================================================
echo Iniciando Asistente de Analisis de Datos con IA...
echo =======================================================
echo.

if not exist ".venv\Scripts\activate.bat" (
    echo [ERROR] No se encontro el entorno virtual en la carpeta .venv
    echo Por favor, asegurate de estar en la carpeta correcta.
    pause
    exit /b
)

call .venv\Scripts\activate
echo Entorno virtual activado. Iniciando servidor local...
echo (Se abrira una pestana en tu navegador web automaticamente)
echo.

streamlit run app.py

pause
