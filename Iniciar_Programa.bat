@echo off
rem Iniciar_Programa.bat
rem Crea/activa un entorno virtual, instala dependencias y lanza la app Streamlit

:: Verificar Python
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
  echo Python no instalado o no en PATH. Instala Python 3.11+ y reintenta.
  pause
  exit /b 1
)

:: Crear venv si no existe
if not exist ".venv\Scripts\activate" (
  echo Creando entorno virtual en .venv ...
  python -m venv .venv
)

:: Activar venv
call .venv\Scripts\activate

:: Actualizar pip e instalar dependencias
python -m pip install --upgrade pip
if exist requirements.txt (
  echo Instalando dependencias desde requirements.txt ...
  pip install -r requirements.txt
) else (
  echo No se encontro requirements.txt. Omite la instalacion de dependencias.
)

:: Crear .env si el usuario lo desea
if not exist .env (
  echo.
  set /p CREARENV="¿Deseas crear un archivo .env y añadir GROQ_API_KEY ahora? (s/N): "
  if /I "%CREARENV%"=="s" (
    set /p KEY="Introduce tu GROQ_API_KEY: "
    if defined KEY (
      echo GROQ_API_KEY=%KEY%> .env
      echo .env creado.
    ) else (
      echo No se ingreso clave. Puedes crear .env manualmente luego.
    )
  )
)

echo Iniciando la aplicacion Streamlit...
streamlit run app.py

pause
