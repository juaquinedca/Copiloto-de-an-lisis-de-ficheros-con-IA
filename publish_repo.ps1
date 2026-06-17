# Script PowerShell para preparar y subir el repo a GitHub
# 1) Reemplaza la URL del remote por la de tu repo.
# 2) Ejecuta este script desde la carpeta del proyecto.

$remote = "https://github.com/TU_USUARIO/TU_REPO.git"

git init
git add .
git commit -m "Prepare repo for public release: cleaned requirements, license, docs"
git branch -M main
git remote add origin $remote
# Empuja al remoto (te pedirá credenciales si no usas SSH)
git push -u origin main

Write-Host "Push completo. Ahora conecta el repo en Streamlit Cloud y añade el secreto GROQ_API_KEY."
