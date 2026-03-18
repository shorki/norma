import streamlit as st
from utils.helpers import load_config, save_config
from utils.styles import apply_global_styles

st.set_page_config(page_title="Configuración | Consultador", page_icon="⚖️", layout="wide")
apply_global_styles()

st.markdown('<div class="section-title">Configuración</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-subtitle">Definí parámetros generales para orientar las respuestas de la aplicación.</div>',
    unsafe_allow_html=True
)

config = load_config()

with st.form("config_form"):
    col1, col2 = st.columns(2)

    with col1:
        jurisdiccion = st.selectbox(
            "Jurisdicción",
            ["Uruguay", "Argentina", "Chile", "España", "Otra"],
            index=["Uruguay", "Argentina", "Chile", "España", "Otra"].index(config.get("jurisdiccion", "Uruguay"))
        )

        materia = st.selectbox(
            "Materia",
            ["General", "Civil", "Penal", "Laboral", "Comercial", "Notarial", "Familia", "Administrativo"],
            index=["General", "Civil", "Penal", "Laboral", "Comercial", "Notarial", "Familia", "Administrativo"].index(
                config.get("materia", "General")
            ) if config.get("materia", "General") in ["General", "Civil", "Penal", "Laboral", "Comercial", "Notarial", "Familia", "Administrativo"] else 0
        )

    with col2:
        estilo = st.selectbox(
            "Estilo de redacción",
            ["Claro y profesional", "Más técnico", "Más resumido", "Más explicativo"],
            index=["Claro y profesional", "Más técnico", "Más resumido", "Más explicativo"].index(
                config.get("estilo", "Claro y profesional")
            ) if config.get("estilo", "Claro y profesional") in ["Claro y profesional", "Más técnico", "Más resumido", "Más explicativo"] else 0
        )

    submitted = st.form_submit_button("Guardar configuración", use_container_width=True)

    if submitted:
        new_config = {
            "jurisdiccion": jurisdiccion,
            "materia": materia,
            "estilo": estilo
        }
        save_config(new_config)
        st.success("Configuración guardada correctamente.")

st.markdown("### Vista actual")
current = load_config()

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(
        f"""
        <div class="metric-box">
            <div class="small-muted">Jurisdicción</div>
            <h2>{current["jurisdiccion"]}</h2>
        </div>
        """,
        unsafe_allow_html=True
    )
with col2:
    st.markdown(
        f"""
        <div class="metric-box">
            <div class="small-muted">Materia</div>
            <h2>{current["materia"]}</h2>
        </div>
        """,
        unsafe_allow_html=True
    )
with col3:
    st.markdown(
        f"""
        <div class="metric-box">
            <div class="small-muted">Estilo</div>
            <h2>{current["estilo"]}</h2>
        </div>
        """,
        unsafe_allow_html=True
    )