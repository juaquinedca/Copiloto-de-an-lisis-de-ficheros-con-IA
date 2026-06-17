import streamlit as st
import pandas as pd
import os
import re
from io import BytesIO
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import create_tool_calling_agent, AgentExecutor
from herramientas import crear_herramientas, informacion_df_func, resumen_estadistico_func
from fpdf import FPDF

# ─── Carga de variables de entorno ────────────────────────────────────────────
load_dotenv()

# ─── Helper: Convertir Markdown a PDF ─────────────────────────────────────────
def markdown_a_pdf(texto_md: str, titulo: str = "Reporte") -> bytes:
    """Convierte un texto Markdown simple a bytes de PDF usando fpdf2."""
    pdf = FPDF()
    pdf.add_page()
    # Márgenes generosos: izq=20, arriba=20, der=20
    pdf.set_margins(20, 20, 20)
    pdf.set_auto_page_break(auto=True, margin=20)

    for linea in texto_md.split("\n"):
        # Limpiar símbolos Markdown del texto final
        linea_limpia = re.sub(r"[*_`#|]+", "", linea).strip()
        if not linea_limpia:
            pdf.ln(3)
            continue

        if linea.startswith(("## ", "### ", "#### ")):
            nivel = linea.count("#", 0, 5)
            size = max(11, 16 - nivel)
            pdf.set_font("Helvetica", style="B", size=size)
            pdf.set_x(pdf.l_margin)
            pdf.multi_cell(0, 8, linea_limpia)
            pdf.ln(1)
        elif linea.lstrip().startswith(("- ", "* ", "+ ")):
            pdf.set_font("Helvetica", size=10)
            # Indentación para bullets
            pdf.set_x(pdf.l_margin + 4)
            contenido = re.sub(r"^\s*[-*+]\s+", "", linea).strip()
            contenido = re.sub(r"[*_`#|]+", "", contenido).strip()
            pdf.multi_cell(pdf.epw - 4, 6, f"- {contenido}")
        else:
            pdf.set_font("Helvetica", size=10)
            pdf.set_x(pdf.l_margin)
            pdf.multi_cell(0, 6, linea_limpia)

    return bytes(pdf.output())

# ─── Configuración de la página ───────────────────────────────────────────────
st.set_page_config(
    page_title="Asistente de Análisis de Datos",
    layout="wide"
)

# ─── Sidebar: Configuración y Carga de Datos ──────────────────────────────────
with st.sidebar:
    st.title("Asistente de Análisis")
    
    st.info("""
    Este asistente utiliza Inteligencia Artificial para ayudarle a explorar, 
    analizar y visualizar datos de forma interactiva.
    """)
    
    st.markdown("### Carga de Datos")
    
    if "uploader_key" not in st.session_state:
        st.session_state["uploader_key"] = 0
        
    if st.button("🔄 Resetear / Empezar de cero", use_container_width=True):
        st.session_state["uploader_key"] += 1
        st.session_state.pop("nombre_archivo_actual", None)
        for key in ["reporte_general", "reporte_estadisticas", "ultima_respuesta_pregunta", "ultimo_grafico_img"]:
            st.session_state.pop(key, None)
        st.rerun()

    archivo_cargado = st.file_uploader(
        "Seleccione un archivo",
        type=["csv", "xlsx", "xls", "json"],
        label_visibility="collapsed",
        help="Soporta archivos CSV, Excel (XLSX, XLS) y JSON de hasta 500 MB",
        key=f"uploader_{st.session_state['uploader_key']}"
    )

# ─── Área Principal ───────────────────────────────────────────────────────────
st.title("Asistente de Análisis de Datos con IA")

if not archivo_cargado:
    st.markdown("""
    ### Bienvenido
    Para comenzar el análisis, por favor **suba un archivo** utilizando el panel lateral izquierdo.
    
    **Formatos soportados:** CSV, Excel (.xlsx, .xls) y JSON.
    
    **Funcionalidades disponibles:**
    - Generación de reportes automáticos (información general y estadísticas descriptivas).
    - Consultas interactivas en lenguaje natural sobre sus datos.
    - Generación de visualizaciones y gráficos automáticos.
    """)
    st.stop()

# ── 1. Carga del DataFrame ────────────────────────────────────────────────
try:
    if st.session_state.get("nombre_archivo_actual") != archivo_cargado.name:
        st.session_state["nombre_archivo_actual"] = archivo_cargado.name
        for key in ["reporte_general", "reporte_estadisticas",
                    "ultima_respuesta_pregunta", "ultimo_grafico_img"]:
            st.session_state.pop(key, None)

    nombre_archivo = archivo_cargado.name.lower()
    if nombre_archivo.endswith('.csv'):
        df = pd.read_csv(archivo_cargado)
    elif nombre_archivo.endswith(('.xlsx', '.xls')):
        df = pd.read_excel(archivo_cargado)
    elif nombre_archivo.endswith('.json'):
        df = pd.read_json(archivo_cargado)
    else:
        st.error("Formato de archivo no soportado.")
        st.stop()
        
    st.sidebar.success(f"Archivo cargado: {archivo_cargado.name}")
    st.sidebar.text(f"Dimensión: {df.shape[0]:,} filas × {df.shape[1]} columnas")

except Exception as e:
    st.error(f"Error al leer el archivo: {e}")
    st.stop()

# ── 2. Validar API Key ────────────────────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    try:
        # Fallback para Streamlit Community Cloud
        GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
    except Exception:
        GROQ_API_KEY = None

if not GROQ_API_KEY:
    st.error("No se encontró la variable GROQ_API_KEY en las variables de entorno o en st.secrets. Por favor, configúrala.")
    st.stop()

# ── 3. Instanciar LLM ─────────────────────────────────────────────────────
llm = ChatGroq(
    api_key=GROQ_API_KEY,
    model_name="llama-3.3-70b-versatile",
    temperature=0
)

# ── 4. Herramientas ───────────────────────────────────────────────────────
tools = crear_herramientas(df, llm)

# ── 5. Prompt ReAct ───────────────────────────────────────────────────────
# Representación segura de las primeras filas usando diccionarios para evitar cortes a la mitad de una cadena
try:
    df_head = str(df.head(2).to_dict(orient="records"))
except Exception:
    df_head = "Error al extraer muestra de datos."

prompt_tool_calling = ChatPromptTemplate.from_messages([
    ("system", """Eres un asistente de datos profesional que responde SIEMPRE en castellano (español).

Tienes acceso a un dataframe pandas llamado `df`.
Aquí están las primeras filas del DataFrame:
{df_head}

INSTRUCCIONES OBLIGATORIAS:
- Analiza la pregunta del usuario y utiliza las herramientas proporcionadas para encontrar la respuesta.
- Siempre agrega interpretación y contexto a tus respuestas finales.
- Calcula porcentajes cuando corresponda.
- Sé claro, profesional y usa un tono de consultor de datos."""),
    ("human", "{input}"),
    MessagesPlaceholder("agent_scratchpad"),
])

prompt_tool_calling = prompt_tool_calling.partial(df_head=df_head)

# ── 6. Agente ─────────────────────────────────────────────────────────────
agente = create_tool_calling_agent(llm=llm, tools=tools, prompt=prompt_tool_calling)
orquestador = AgentExecutor(
    agent=agente,
    tools=tools,
    verbose=True,
    max_iterations=6,
    max_execution_time=90,
    return_intermediate_steps=False
)

# ─── Creación de Pestañas ─────────────────────────────────────────────────
tab_datos, tab_reportes, tab_consultas, tab_graficos = st.tabs([
    "Visión General", 
    "Reportes Automáticos", 
    "Consultas", 
    "Visualizaciones"
])

with tab_datos:
    # ── KPI Cards ──────────────────────────────────────────────────────────
    total_filas = df.shape[0]
    total_cols = df.shape[1]
    total_celdas = total_filas * total_cols
    celdas_nulas = int(df.isnull().sum().sum())
    pct_completo = round((1 - celdas_nulas / total_celdas) * 100, 1) if total_celdas > 0 else 100.0
    duplicados = int(df.duplicated().sum())

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total de filas", f"{total_filas:,}")
    k2.metric("Total de columnas", f"{total_cols}")
    k3.metric("Datos completos", f"{pct_completo}%",
              delta=f"-{round(100 - pct_completo, 1)}% nulos" if pct_completo < 100 else "Sin nulos",
              delta_color="inverse")
    k4.metric("Filas duplicadas", f"{duplicados:,}",
              delta="Sin duplicados" if duplicados == 0 else f"{duplicados} a revisar",
              delta_color="normal" if duplicados == 0 else "inverse")

    st.markdown("---")

    # ── Vista previa del dataset ───────────────────────────────────────────
    st.markdown("#### Vista previa del dataset")
    col_prev, col_meta = st.columns([3, 1])

    with col_prev:
        st.dataframe(df.head(15), use_container_width=True)

    with col_meta:
        st.markdown("**Valores unicos por columna:**")
        unicos = df.nunique().reset_index()
        unicos.columns = ["Columna", "Unicos"]
        st.dataframe(unicos, use_container_width=True, hide_index=True)

    st.markdown("---")

    # ── Calidad de datos + Tipos de columnas ───────────────────────────────
    col_calidad, col_tipos = st.columns([3, 1])

    with col_calidad:
        st.markdown("#### Calidad de datos por columna (% nulos)")
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import seaborn as sns

        nulos_pct = (df.isnull().sum() / len(df) * 100).sort_values(ascending=True)
        colores = ["#ef4444" if v > 20 else "#f59e0b" if v > 5 else "#22c55e" for v in nulos_pct]

        fig_nulos, ax_nulos = plt.subplots(figsize=(8, max(3, len(df.columns) * 0.35)))
        ax_nulos.barh(nulos_pct.index, nulos_pct.values, color=colores)
        ax_nulos.set_xlabel("% Nulos", fontsize=9)
        ax_nulos.set_xlim(0, 100)
        ax_nulos.axvline(5, color="#f59e0b", linestyle="--", linewidth=0.8, alpha=0.7)
        ax_nulos.axvline(20, color="#ef4444", linestyle="--", linewidth=0.8, alpha=0.7)
        for i, (val, col_bar) in enumerate(zip(nulos_pct.values, colores)):
            if val > 0:
                ax_nulos.text(val + 0.5, i, f"{val:.1f}%", va="center", fontsize=7.5, color=col_bar)
        fig_nulos.patch.set_alpha(0)
        ax_nulos.patch.set_alpha(0)
        ax_nulos.tick_params(colors="white", labelsize=8)
        ax_nulos.xaxis.label.set_color("white")
        for spine in ax_nulos.spines.values():
            spine.set_visible(False)
        plt.tight_layout()
        st.pyplot(fig_nulos, use_container_width=True)
        plt.close(fig_nulos)

    with col_tipos:
        st.markdown("#### Tipos de columnas")
        tipo_counts = {
            "Numericas": len(df.select_dtypes(include="number").columns),
            "Texto": len(df.select_dtypes(include=["object", "category"]).columns),
            "Fechas": len(df.select_dtypes(include=["datetime", "datetimetz"]).columns),
        }
        tipo_counts = {k: v for k, v in tipo_counts.items() if v > 0}
        colors_donut = ["#6366f1", "#22c55e", "#f59e0b"]

        fig_donut, ax_donut = plt.subplots(figsize=(3.2, 3.2))
        wedges, texts, autotexts = ax_donut.pie(
            tipo_counts.values(),
            labels=tipo_counts.keys(),
            autopct="%1.0f%%",
            colors=colors_donut[:len(tipo_counts)],
            startangle=90,
            wedgeprops=dict(width=0.55),
        )
        for t in texts:
            t.set_color("white")
            t.set_fontsize(8)
        for at in autotexts:
            at.set_color("white")
            at.set_fontsize(8)
            at.set_fontweight("bold")
        fig_donut.patch.set_alpha(0)
        ax_donut.patch.set_alpha(0)
        plt.tight_layout()
        st.pyplot(fig_donut, use_container_width=True)
        plt.close(fig_donut)

        for tipo, cnt in tipo_counts.items():
            st.caption(f"**{tipo}:** {cnt} col.")

    st.markdown("---")

    # ── AI Quick Insights ──────────────────────────────────────────────────
    st.markdown("#### Insights Rapidos con IA")
    cache_key = f"insights_{archivo_cargado.name}"
    if cache_key not in st.session_state:
        if st.button("Generar insights automaticos del dataset", use_container_width=True):
            with st.spinner("La IA esta analizando tu dataset para darte los 3 hallazgos mas importantes..."):
                try:
                    from langchain.prompts import PromptTemplate
                    from langchain_core.output_parsers import StrOutputParser

                    stats_num = df.describe().transpose().to_string() if not df.select_dtypes(include="number").empty else "Sin columnas numericas"
                    nulos_info = df.isnull().sum()[df.isnull().sum() > 0].to_string() or "Sin valores nulos"
                    col_info = df.dtypes.to_string()

                    plantilla_insights = PromptTemplate(
                        template="""Eres un analista de datos experto. Analiza este dataset y proporciona EXACTAMENTE 3 hallazgos o insights clave, breves y concretos, en formato de lista numerada. Se directo y orientado a la accion. No uses mas de 2 lineas por insight. Responde en espanol.

Columnas y tipos:
{col_info}

Estadisticas numericas:
{stats_num}

Valores nulos:
{nulos_info}

Dimensiones: {shape} filas x {cols} columnas

Proporciona 3 insights claros y utiles:""",
                        input_variables=["col_info", "stats_num", "nulos_info", "shape", "cols"]
                    )
                    cadena = plantilla_insights | llm | StrOutputParser()
                    insights_text = cadena.invoke({
                        "col_info": col_info[:800],
                        "stats_num": stats_num[:1200],
                        "nulos_info": nulos_info[:400],
                        "shape": total_filas,
                        "cols": total_cols,
                    })
                    st.session_state[cache_key] = insights_text
                    st.rerun()
                except Exception as e:
                    st.error(f"Error generando insights: {e}")
    else:
        with st.container(border=True):
            st.markdown(st.session_state[cache_key])
        if st.button("Regenerar insights", key="regen_insights"):
            del st.session_state[cache_key]
            st.rerun()



with tab_reportes:
    st.markdown("### Generación de Reportes Automáticos")
    st.markdown("Utilice estas herramientas para obtener un resumen rápido de la estructura y estadísticas de sus datos.")
    
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Reporte de Informaciones Generales", use_container_width=True):
            with st.spinner("Procesando información general..."):
                try:
                    respuesta = informacion_df_func(
                        "Genera un reporte con información general de los datos.", df, llm
                    )
                    st.session_state["reporte_general"] = respuesta
                except Exception as e:
                    st.error(f"Error al generar el reporte: {e}")

        if "reporte_general" in st.session_state:
            with st.container(border=True):
                st.markdown(st.session_state["reporte_general"])
                try:
                    pdf_bytes = markdown_a_pdf(st.session_state["reporte_general"], "Reporte General")
                    st.download_button(
                        label="Descargar Reporte General (PDF)",
                        data=pdf_bytes,
                        file_name="reporte_informaciones_generales.pdf",
                        mime="application/pdf",
                        key="dl_reporte_general"
                    )
                except Exception as e:
                    st.warning(f"No se pudo generar el PDF: {e}")

    with col2:
        if st.button("Reporte de Estadísticas Descriptivas", use_container_width=True):
            with st.spinner("Procesando estadísticas descriptivas..."):
                try:
                    respuesta = resumen_estadistico_func(
                        "Genera un reporte de estadísticas descriptivas.", df, llm
                    )
                    st.session_state["reporte_estadisticas"] = respuesta
                except Exception as e:
                    st.error(f"Error al generar el reporte: {e}")

        if "reporte_estadisticas" in st.session_state:
            with st.container(border=True):
                st.markdown(st.session_state["reporte_estadisticas"])
                try:
                    pdf_bytes = markdown_a_pdf(st.session_state["reporte_estadisticas"], "Reporte Estadístico")
                    st.download_button(
                        label="Descargar Reporte Estadístico (PDF)",
                        data=pdf_bytes,
                        file_name="reporte_estadisticas_descriptivas.pdf",
                        mime="application/pdf",
                        key="dl_reporte_estadisticas"
                    )
                except Exception as e:
                    st.warning(f"No se pudo generar el PDF: {e}")

with tab_consultas:
    st.markdown("### Consultas en Lenguaje Natural")
    st.markdown("Realice preguntas específicas sobre su conjunto de datos. El agente escribirá y ejecutará código Python internamente para encontrar la respuesta exacta.")
    
    pregunta_sobre_datos = st.text_input(
        "Ingrese su consulta:",
        placeholder="Ejemplo: ¿Cuál es el promedio de la columna ventas por cada categoría?"
    )

    if st.button("Procesar consulta"):
        if not pregunta_sobre_datos.strip():
            st.warning("Por favor, ingrese una consulta válida.")
        else:
            with st.spinner("Analizando datos y procesando respuesta..."):
                try:
                    respuesta = orquestador.invoke({"input": pregunta_sobre_datos})
                    st.session_state["ultima_respuesta_pregunta"] = respuesta["output"]
                except Exception as e:
                    st.session_state["ultima_respuesta_pregunta"] = f"Error al procesar la pregunta: {e}"

    if "ultima_respuesta_pregunta" in st.session_state:
        st.info(st.session_state["ultima_respuesta_pregunta"])

with tab_graficos:
    st.markdown("### Generación de Visualizaciones")
    st.markdown("Describa el gráfico que necesita. El sistema determinará la mejor forma de visualizarlo.")
    
    pregunta_grafico = st.text_input(
        "Describa la visualización deseada:",
        placeholder="Ejemplo: Genera un gráfico de barras mostrando el total de ventas por región."
    )

    if st.button("Generar visualización"):
        if not pregunta_grafico.strip():
            st.warning("Por favor, describa la visualización que desea generar.")
        else:
            with st.spinner("Generando y renderizando gráfico..."):
                try:
                    orquestador.invoke({"input": pregunta_grafico})
                except Exception as e:
                    st.error(f"Error al generar el gráfico: {e}")

    if "ultimo_grafico_img" in st.session_state and st.session_state["ultimo_grafico_img"] is not None:
        with st.container(border=True):
            st.markdown("#### Visualización Resultante")
            st.image(st.session_state["ultimo_grafico_img"], use_container_width=True)