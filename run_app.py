import os
import webbrowser
import time

# Lanzador simple que inicia Streamlit y abre el navegador
os.system("streamlit run app.py &")
# Espera breve para que el servidor arranque
time.sleep(2)
webbrowser.open('http://localhost:8501')
