import streamlit as st
from utils.helpers import ensure_directories, load_config
from utils.styles import apply_global_styles

st.set_page_config(
    page_title="Norma",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

ensure_directories()
config = load_config()
apply_global_styles()

st.markdown(
    """
    <div class="hero-card formal-hero">
        <div class="hero-badge">PLATAFORMA DOCUMENTAL JURÍDICA</div>
        <h1 class="hero-title">Norma</h1>
        <p class="hero-subtitle">
            Consulta normativa y análisis documental asistido por inteligencia artificial.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("### Visión general")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        """
        <div class="info-card formal-card">
            <h4>Consulta jurídica</h4>
            <p>Realizá preguntas y obtené respuestas fundamentadas en normativa y documentos.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        """
        <div class="info-card formal-card">
            <h4>Biblioteca</h4>
            <p>Centralizá códigos, leyes y doctrina en un único lugar para su consulta.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        f"""
        <div class="info-card formal-card">
            <h4>Configuración</h4>
            <p><strong>Jurisdicción:</strong> {config.get("jurisdiccion", "Uruguay")}<br>
            <strong>Materia:</strong> {config.get("materia", "General")}<br>
            <strong>Estilo:</strong> {config.get("estilo", "Claro y profesional")}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

st.info("Utilizá el menú lateral para navegar por los módulos de Norma.")