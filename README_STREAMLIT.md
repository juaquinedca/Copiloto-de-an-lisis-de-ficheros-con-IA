Pasos rápidos para publicar en GitHub y desplegar en Streamlit Cloud

1) Preparar el repositorio (local):

```bash
cd "C:/Users/juaqu/Desktop/proyecto lanchain/analizar_datos_ia"
# Inicializar git si aún no está
git init
git add .
git commit -m "Initial commit: Analizador de datos IA"
# Crear repo en GitHub y añadir remote (reemplaza URL)
git remote add origin https://github.com/tu_usuario/tu_repo.git
git branch -M main
git push -u origin main
```

2) En GitHub:
- Asegúrate de que `.env` está en `.gitignore` (ya lo está).
- Revisa que no hayas comiteado claves en el historial (si las tienes, usa `git filter-repo` o reescribe historial).

3) Desplegar en Streamlit Community Cloud:
- Ve a https://share.streamlit.io y conecta tu cuenta de GitHub.
- Elige el repositorio y la rama `main`.
- En Settings → Secrets, añade `GROQ_API_KEY` con tu clave.
- Despliega; la app quedará disponible vía URL pública.

4) Notas útiles:
- Streamlit busca `requirements.txt` en la raíz para instalar dependencias.
- Si usas la versión `requirements_clean.txt`, renombra o reemplaza el archivo a `requirements.txt` antes de hacer push.

5) Comandos locales para probar antes de push:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

Si quieres, puedo:
- Reescribir directamente `requirements.txt` en el repo (necesito permiso para editar archivos aquí).  
- Crear un commit local y darte comandos para push.  
- Preparar el repo para Streamlit (opcional: archivo `.streamlit/config.toml`).
