import io
import re
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Backend no interactivo — obligatorio para Streamlit
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.agents import Tool
from langchain_experimental.tools import PythonAstREPLTool


# ──────────────────────────────────────────────────────────────────────────────
# HERRAMIENTA 1: Informaciones Generales
# ──────────────────────────────────────────────────────────────────────────────
def informacion_df_func(pregunta: str, df: pd.DataFrame, llm: ChatGroq) -> str:
    shape = df.shape
    columns = df.dtypes.to_string()
    nulos = df.isnull().sum().to_string()

    # Comprobación de cadenas 'nan' sólo en columnas texto/categoría
    nans_str = pd.Series(0, index=df.columns)
    for col in df.select_dtypes(include=["object", "category"]).columns:
        nans_str[col] = df[col].astype(str).str.strip().str.lower().eq("nan").sum()
    
    # Truncado de seguridad para evitar Rate Limits (Max 1000 caracteres)
    def truncar(texto, limite=1000):
        return texto[:limite] + "... (truncado)" if len(texto) > limite else texto

    columns = truncar(columns)
    nulos = truncar(nulos)
    nans_str_str = truncar(nans_str.to_string())

    duplicados = int(df.duplicated().sum())

    plantilla = PromptTemplate(
        template="""
Eres un analista de datos encargado de presentar un resumen informativo sobre un **DataFrame** a partir de una {pregunta} hecha por el usuario.

A continuación, encontrarás la información general de la base de datos:

================= INFORMACIÓN DEL DATAFRAME =================
Dimensiones: {shape}

Columnas y tipos de datos:
{columns}

Valores nulos por columna:
{nulos}

Cadenas 'nan' por columna:
{nans_str}

Filas duplicadas: {duplicados}
============================================================

Con base en esta información, redacta un resumen claro y organizado que contenga:
1. Un título: ## Informe de información general sobre el dataset
2. La dimensión total del DataFrame;
3. La descripción de cada columna (incluyendo nombre, tipo de dato y qué representa);
4. Columnas con datos nulos o 'nan' y sus cantidades;
5. Existencia de duplicados;
6. Análisis sugeridos y tratamientos recomendados para limpiar estos datos.
""",
        input_variables=["pregunta", "shape", "columns", "nulos", "nans_str", "duplicados"]
    )

    cadena = plantilla | llm | StrOutputParser()
    return cadena.invoke({
        "pregunta": pregunta,
        "shape": str(shape),
        "columns": columns,
        "nulos": nulos,
        "nans_str": nans_str_str,
        "duplicados": duplicados,
    })


# ──────────────────────────────────────────────────────────────────────────────
# HERRAMIENTA 2: Resumen Estadístico
# ──────────────────────────────────────────────────────────────────────────────
def resumen_estadistico_func(pregunta: str, df: pd.DataFrame, llm: ChatGroq) -> str:
    columnas_numericas = df.select_dtypes(include="number")
    if columnas_numericas.empty:
        return (
            "El dataset no contiene columnas de tipo numérico para calcular estadísticas "
            "descriptivas. Por favor, realiza otro tipo de análisis."
        )

    resumen = columnas_numericas.describe().transpose().to_string()

    plantilla = PromptTemplate(
        template="""
Eres un analista de datos encargado de interpretar resultados estadísticos a partir de una {pregunta} del usuario.

================= ESTADÍSTICAS DESCRIPTIVAS =================
{resumen}
============================================================

Elabora un resumen explicativo claro destacando:
1. Un título: ## Informe de estadísticas descriptivas
2. Visión general de las estadísticas numéricas;
3. Comentarios de valor sobre cada columna analizada;
4. Identificación de outliers basados en mínimos/máximos;
5. Recomendaciones de próximos pasos en el análisis.
""",
        input_variables=["pregunta", "resumen"]
    )

    cadena = plantilla | llm | StrOutputParser()
    return cadena.invoke({"pregunta": pregunta, "resumen": resumen})


# ──────────────────────────────────────────────────────────────────────────────
# HERRAMIENTA 3: Generación de Gráficos
# ──────────────────────────────────────────────────────────────────────────────
def generar_grafico_func(pregunta: str, df: pd.DataFrame, llm: ChatGroq) -> str:
    columnas_info = "\n".join([f"- {col} ({dtype})" for col, dtype in df.dtypes.items()])
    
    try:
        # Muestra de 1 fila convertida a diccionario seguro, sin truncamiento destructivo
        muestra_str = str(df.head(1).to_dict(orient="records"))
    except Exception:
        muestra_str = "Error al obtener muestra"

    plantilla = PromptTemplate(
        template="""
Eres un especialista en visualización de datos. Tu tarea es generar **únicamente el código Python** para graficar con base en la solicitud del usuario.

## Solicitud del usuario:
"{pregunta}"

## Metadatos del DataFrame (variable llamada `df`):
{columnas}

## Muestra de los datos (3 primeras filas):
{muestra}

## Instrucciones obligatorias:
1. Usa `matplotlib.pyplot` (como `plt`) y `seaborn` (como `sns`).
2. Define el tema con `sns.set_theme()`.
3. Asegúrate de que todas las columnas mencionadas existan en el DataFrame `df`.
4. Elige el tipo de gráfico adecuado (histplot, countplot, barplot, scatterplot, lineplot).
5. Crea la figura con `fig, ax = plt.subplots(figsize=(9, 5))`.
6. Añade título y etiquetas apropiadas a los ejes.
7. Posiciona el título a la izquierda (`loc='left'`, `pad=20`, `fontsize=14`).
8. Quita los bordes superior y derecho con `sns.despine()`.
9. NO incluyas `plt.show()` ni `plt.close()`. Solo genera el código que construye el gráfico.
10. Usa `ax` como el objeto de ejes en todas las llamadas.
11. MUY IMPORTANTE: Siempre debes mostrar los valores numéricos exactos en el gráfico. Si es un gráfico de barras, utiliza `ax.bar_label(ax.containers[0], padding=3)` (o itera sobre `ax.containers`). Si es otro tipo de gráfico (líneas, puntos), añade texto en cada punto de datos para que el usuario pueda ver el número exacto sin tener que adivinar por el eje Y.

Devuelve ÚNICAMENTE el código Python, sin ningún texto adicional ni explicaciones.
""",
        input_variables=["pregunta", "columnas", "muestra"]
    )

    cadena = plantilla | llm | StrOutputParser()
    script_bruto = cadena.invoke({
        "pregunta": pregunta,
        "columnas": columnas_info,
        "muestra": muestra_str,
    })

    # Extracción robusta del bloque de código
    match = re.search(r"```python\s*(.*?)\s*```", script_bruto, re.DOTALL | re.IGNORECASE)
    script_limpio = (
        match.group(1).strip() if match
        else script_bruto.replace("```python", "").replace("```", "").strip()
    )

    # Cerrar cualquier figura anterior
    plt.close("all")

    # Crear figura y ejes frescos
    fig, ax = plt.subplots(figsize=(9, 5))

    exec_globals = {
        "df": df,
        "plt": plt,
        "sns": sns,
        "ax": ax,
        "fig": fig,
        "pd": pd,
    }

    try:
        exec(script_limpio, exec_globals)  # noqa: S102
        # Capturamos la figura que esté activa tras la ejecución
        fig_final = plt.gcf()
        
        # En lugar de guardar el objeto Figura (que se corrompe con re-ejecuciones), 
        # guardamos la imagen renderizada en un buffer seguro de memoria.
        import io
        buf = io.BytesIO()
        fig_final.savefig(buf, format="png", bbox_inches="tight", dpi=150)
        buf.seek(0)
        
        st.session_state["ultimo_grafico_img"] = buf
        plt.close("all") # Limpieza absoluta
        return "Gráfico generado y actualizado en la interfaz."
    except Exception as e:
        plt.close("all")
        return f"Error al generar el gráfico: {e}"


# ──────────────────────────────────────────────────────────────────────────────
# FUNCIÓN PÚBLICA: Crear lista de herramientas para el agente
# ──────────────────────────────────────────────────────────────────────────────
def crear_herramientas(df: pd.DataFrame, llm: ChatGroq):
    herramienta_generar_grafico = Tool(
        name="generar_grafico",
        func=lambda pregunta: generar_grafico_func(pregunta, df, llm),
        description=(
            "Úsala para crear, dibujar y mostrar visualizaciones o gráficos a partir "
            "de preguntas del usuario."
        ),
        return_direct=True,
    )

    herramienta_python = Tool(
        name="ejecutar_codigo_python",
        func=PythonAstREPLTool(locals={"df": df, "pd": pd}).run,
        description=(
            "Úsala para realizar cualquier consulta, cálculo específico, filtro o "
            "transformación de datos sobre el DataFrame `df` escribiendo código Python "
            "(por ejemplo: contar nulos, promedios, valores únicos, sumas, filtrados). "
            "NO uses esta herramienta para generar gráficos; para eso usa 'generar_grafico'."
        ),
        return_direct=False,
    )

    return [herramienta_generar_grafico, herramienta_python]