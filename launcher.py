"""Launcher ligero para empaquetar la app con PyInstaller.

Este script carga .env si existe y arranca Streamlit programáticamente.
Al usar PyInstaller se recomienda generar un paquete --onedir y distribuir la carpeta.
"""
import os
import sys
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

def main():
    # Asegura que app.py esté junto al launcher en tiempo de ejecución
    app_path = os.path.join(os.path.dirname(__file__), "app.py")
    if not os.path.exists(app_path):
        # Si no existe, quizá se ejecuta desde el código fuente en repo raíz
        app_path = os.path.join(os.getcwd(), "app.py")

    sys.argv = ["streamlit", "run", app_path]
    try:
        # Import interno de Streamlit CLI
        from streamlit.web import cli as stcli
        sys.exit(stcli.main())
    except Exception as e:
        print("Error al iniciar Streamlit:", e)
        raise

if __name__ == "__main__":
    main()
