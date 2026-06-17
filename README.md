# 🤖 Asistente de Análisis de Datos — Demo

Código de demostración: una interfaz de análisis de datos construida con Streamlit que facilita la exploración rápida de datasets (CSV, Excel, JSON) y la generación de insights.

Breve descripción:
- Interfaz con previsualización del `DataFrame`, KPIs y gráficos de calidad de datos.
- Herramientas para resumen estadístico, gráficos y ejecución segura de pequeñas consultas en Python sobre los datos.

Tecnologías principales: Python 3.11, Streamlit, Pandas, Matplotlib, Seaborn.

## Ejemplo (capturas)
Incluye varias capturas en `imagenes/` que muestran la carga de datos, KPIs, insights y visualizaciones.

## Estado del proyecto

Este repositorio se publica como una demostración del código fuente y de las ideas de diseño implementadas. No se distribuye un binario oficial (.exe) desde este repositorio; la forma recomendada de ejecución es clonar el proyecto y ejecutar la aplicación localmente siguiendo la sección "Cómo descargar y ejecutar localmente".

## Contribuciones

Se aceptan contribuciones que mejoren la claridad del código, la documentación o la experiencia de usuario. Para contribuir:

- Abre un issue describiendo la mejora o el bug.
- Crea un branch con un PR que incluya cambios pequeños y revisables.

Por favor añade pruebas o instrucciones reproduceibles para cambios funcionales importantes.

## Licencia

Salvo indicación contraria en un fichero `LICENSE`, este repositorio se comparte con fines demostrativos. Si deseas una licencia explícita (por ejemplo MIT), indícamelo y puedo añadirla.

## Contacto

Para preguntas técnicas o soporte relacionado con este repositorio, abre un issue en GitHub.

---

Gracias por revisar el proyecto. Si quieres que incluya un conjunto de datos de ejemplo o instrucciones adicionales para despliegue, dime y lo añado.

## Cómo descargar y ejecutar localmente (resumen rápido)

1) Clona el repositorio y crea un entorno virtual:

```powershell
git clone https://github.com/juaquinedca/Copiloto-de-an-lisis-de-ficheros-con-IA.git
cd Copiloto-de-an-lisis-de-ficheros-con-IA
python -m venv .venv
.\.venv\Scripts\Activate.ps1   # Windows PowerShell
```

2) Instala dependencias y (opcional) crea `.env`:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
echo GROQ_API_KEY=tu_clave_aqui > .env    # opcional: para funcionalidades LLM
```

3) Ejecuta la demo:

```powershell
streamlit run app.py
```

Alternativa de doble click (Windows): usa `Iniciar_Programa.bat` — el script crea/activa `.venv` e instala dependencias si no existen.

### Estado y alcance

- Propósito: demo del código y patrones de diseño para análisis de datos con Streamlit. No se distribuye ni se soporta un ejecutable empaquetado.
- Responsabilidad: esta entrega incluye solo el código fuente y documentación mínima; si deseas que prepare builds o paquetes instalables, podemos hacerlo como tarea separada.

### Contacto y contribuciones

Si deseas mejorar el proyecto, abre un issue o crea un PR. Para cambios grandes o despliegue, preferimos propuestas pequeñas y pruebas que permitan validar el comportamiento.

---

Gracias por revisar el proyecto. Si quieres que incluya un dataset de ejemplo o instrucciones de despliegue adicionales, me indicas y lo preparo.

