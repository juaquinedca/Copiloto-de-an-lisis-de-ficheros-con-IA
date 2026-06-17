# 🤖 Asistente de Análisis de Datos con IA

Aplicación web interactiva construida con Streamlit que permite analizar datasets (CSV, Excel, JSON) usando agentes basados en LangChain + Groq.

## Características
- Dashboard automático: KPIs, % nulos, tipos de columnas.
- Insights generados con IA.
- Consultas en lenguaje natural que ejecutan código Python sobre el DataFrame.
- Visualizaciones dinámicas y exportación de reportes en PDF.

## Tecnologías
- Python 3.11
- Streamlit, Pandas, Matplotlib, Seaborn
- LangChain + Groq (requiere GROQ_API_KEY)

## Instalación (local)
`powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
`

Configura tu clave de Groq en un archivo .env en la raíz:
`
GROQ_API_KEY=tu_clave_aqui
`

Ejecuta la aplicación:
`powershell
streamlit run app.py
# o
python run_app.py
`

## Despliegue recomendado (Streamlit Cloud)
1. Sube este repositorio a GitHub.
2. Conecta el repo en https://share.streamlit.io.
3. En Settings → Secrets, añade GROQ_API_KEY.
4. Despliega la app (Streamlit instalará equirements.txt).

> Nota: He eliminado Dockerfile del repo para simplificar el despliegue por Streamlit y evitar peso adicional.

## Seguridad y advertencias
- No subas claves ni .env al repositorio (ya están en .gitignore).
- El agente ejecuta código Python dinámico; usa la app con datasets de confianza y en entornos controlados.

## Licencia
MIT. Ver archivo LICENSE.
