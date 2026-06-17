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
```powershell
streamlit run app.py
```

## Quick start (ejecución con un solo click o comando)

Para que cualquiera descargue y ejecute la aplicación con el mínimo esfuerzo, he añadido lanzadores para los sistemas más comunes.

- Windows (doble click): ejecuta `Iniciar_Programa.bat`. Este script crea/activa un entorno virtual `.venv`, instala `requirements.txt`, opcionalmente crea un `.env` con `GROQ_API_KEY` y lanza Streamlit.

- PowerShell (ejecución recomendada si se requiere permisos): ejecuta `Iniciar_Programa.ps1` desde PowerShell:
	```powershell
	Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
	.\Iniciar_Programa.ps1
	```

- macOS / Linux: ejecuta el script `run.sh`:
	```bash
	chmod +x run.sh
	./run.sh
	```

Notas:
- Requiere Python 3.11+ instalado en el sistema.
- No subas tu `.env` al repositorio; el script pregunta si deseas crearlo localmente.
- Para una demo pública inmediata, también puedes desplegar el repo en Streamlit Cloud conectando tu cuenta de GitHub.

## Capturas de pantalla

Las siguientes imágenes muestran la interfaz y las funcionalidades principales en el mismo orden en que se navega la aplicación.

### 1) Carga y configuración / Vista previa y KPIs
![Carga y configuración](imagenes/imag_1.png)
Pantalla inicial con el panel lateral donde se cargan los archivos (CSV, Excel, JSON), botón para resetear la sesión y pequeñas indicaciones de uso.
Previsualización de las primeras filas del `DataFrame` y tarjetas KPI que muestran total de filas, columnas, porcentaje de datos completos y duplicados.

### 2) Calidad de datos (% nulos)
![Vista previa del dataset](imagenes/imag_2.png)
Gráfico horizontal que presenta el porcentaje de valores nulos por columna, con líneas de referencia para alertar (5% y 20%).
Gráfico tipo donut que resume la proporción de columnas numéricas, de texto y de fecha.

### 3) Insights automáticos con IA
![Insights con IA](imagenes/imag_3.png)
Sección que muestra los 3 hallazgos automáticos generados por el modelo, pensados para ser breves y accionables.

### 4) Reportes automáticos
![Reportes automáticos](imagenes/imag_4.png)
Herramientas para generar resúmenes de información general y estadísticas descriptivas; posibilidad de descargar los reportes en PDF.


### 5) Consultas y visualizaciones
![Consultas y visualizaciones](imagenes/imag_6.png)
Panel para hacer consultas en lenguaje natural

![Consultas y visualizaciones](imagenes/imag_7.png)
El agente puede ejecutar código Python internamente y generar visualizaciones que se renderizan en la interfaz.

