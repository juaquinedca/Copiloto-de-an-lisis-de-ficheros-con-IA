<# Iniciar_Programa.ps1
   Lanzador PowerShell: crea/activa venv, instala dependencias y lanza Streamlit.
   Ejecutar desde PowerShell: .\Iniciar_Programa.ps1 (puede pedir permiso de ejecución).
#>
try {
    $null = Get-Command python -ErrorAction Stop
} catch {
    Write-Host "Python no está instalado o no está en PATH. Instala Python 3.11+" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path ".venv\Scripts\Activate.ps1")) {
    Write-Host "Creando entorno virtual .venv ..."
    python -m venv .venv
}

Write-Host "Activando entorno virtual..."
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned -Force | Out-Null
. .\.venv\Scripts\Activate.ps1

Write-Host "Actualizando pip e instalando dependencias (si es necesario)..."
python -m pip install --upgrade pip
if (Test-Path "requirements.txt") {
    pip install -r requirements.txt
} else {
    Write-Host "No se encontró requirements.txt. Omite instalación." -ForegroundColor Yellow
}

if (-not (Test-Path ".env")) {
    $resp = Read-Host "¿Deseas crear un archivo .env con GROQ_API_KEY ahora? (s/N)"
    if ($resp -and $resp.ToLower().StartsWith('s')) {
        $key = Read-Host "Introduce tu GROQ_API_KEY (no se subirá al repo)"
        if ($key) { "GROQ_API_KEY=$key" | Out-File -Encoding utf8 .env; Write-Host ".env creado." }
    }
}

Write-Host "Iniciando Streamlit..."
streamlit run app.py
