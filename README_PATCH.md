# Analizador de Datos con IA

Versión lista para publicar: instrucciones, despliegue en Streamlit Cloud y notas de seguridad.

## Requisitos
- Python 3.11
- GROQ_API_KEY (clave de la API usada por `langchain_groq`)

## Instalación local (rápida)
1. Renombrar `requirements_clean.txt` a `requirements.txt` o copiar su contenido:

```powershell
cp requirements_clean.txt requirements.txt
```

2. Crear entorno e instalar:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

3. Ejecutar:

```powershell
streamlit run app.py
# o
python run_app.py
```

## Despliegue en Streamlit Cloud (gratuito para demos)
1. Subir el repo a GitHub.
2. Entrar en https://share.streamlit.io y conectar tu cuenta de GitHub.
3. Seleccionar el repositorio y la rama `main`.
4. En Settings → Secrets, añadir `GROQ_API_KEY`.
5. Desplegar y abrir la URL pública.

## Notas de seguridad
- Nunca subas `.env` ni claves en el repo. `.gitignore` ya incluye `.env`.
- El agente ejecuta código Python dinámico. Ejecuta la app en entornos controlados para evitar riesgos con datos o código malicioso.

## Licencia
Proyecto bajo MIT License (archivo `LICENSE`).

---
Si quieres, puedo ahora:
- Reemplazar `requirements.txt` con la versión limpia y hacer commit localmente.
- Ejecutar los comandos git para inicializar y empujar al remoto (necesito la URL del repo que crees en GitHub).
- Preparar el despliegue en Streamlit (te guío en la conexión y secreto).
