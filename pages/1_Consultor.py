import streamlit as st
from utils.helpers import (
    list_documents,
    load_config,
    save_history_entry,
    current_datetime_str,
)
from utils.lector_pdf import read_document, split_into_fragments
from utils.vector_store import semantic_search
from utils.buscador import generate_answer
from utils.styles import apply_global_styles

st.set_page_config(page_title="Consultar | Norma", page_icon="⚖️", layout="wide")
apply_global_styles()

st.markdown('<div class="section-title">Consultar</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-subtitle">Realizá consultas jurídicas sobre la documentación cargada en Norma.</div>',
    unsafe_allow_html=True
)

documents = list_documents()
config = load_config()

if not documents:
    st.warning("Todavía no hay documentos cargados. Primero subí archivos en la sección Biblioteca.")
    st.stop()


def render_professional_output(answer_text, relevant_fragments):
    docs_used = sorted(list({frag["document_name"] for frag in relevant_fragments})) if relevant_fragments else []

    st.markdown('<div class="legal-output-card">', unsafe_allow_html=True)

    st.markdown(
        """
        <div class="legal-header-row">
            <div class="legal-badge">INFORME DE CONSULTA</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="legal-section">
            <div class="legal-section-title">Respuesta</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown(answer_text)

    if docs_used:
        st.markdown(
            """
            <div class="legal-section">
                <div class="legal-section-title">Base consultada</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        for doc in docs_used:
            st.markdown(f"- {doc}")

    st.markdown(
        """
        <div class="legal-section">
            <div class="legal-section-title">Observación</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.info(
        "La presente respuesta se basa en los documentos cargados en Norma y constituye apoyo de análisis, no sustituyendo una revisión profesional del caso concreto."
    )

    st.markdown("</div>", unsafe_allow_html=True)


col1, col2 = st.columns([1.15, 0.85])

with col1:
    query = st.text_area(
        "Consulta",
        placeholder="Ejemplo: si el poder no aclara cómo actúan dos apoderados, cómo deben actuar",
        height=180
    )

with col2:
    st.markdown("#### Parámetros")

    selected_docs = st.multiselect(
        "Documentos",
        options=[doc["name"] for doc in documents],
        default=[doc["name"] for doc in documents]
    )

    output_type = st.selectbox(
        "Tipo de salida",
        [
            "Respuesta directa",
            "Marco conceptual",
            "Resumen",
            "Puntos clave",
            "Búsqueda de fragmentos"
        ]
    )

    use_ai = st.toggle("Usar IA", value=True)

search_button = st.button("Consultar", use_container_width=True)

if search_button:
    if not query.strip():
        st.error("Ingresá una consulta.")
        st.stop()

    if not selected_docs:
        st.error("Seleccioná al menos un documento.")
        st.stop()

    with st.spinner("Procesando consulta..."):
        docs_data = []

        for doc in documents:
            if doc["name"] in selected_docs:
                text = read_document(doc["path"])
                fragments = split_into_fragments(text)

                docs_data.append({
                    "name": doc["name"],
                    "full_text": text,
                    "fragments": fragments
                })

        relevant_fragments = semantic_search(
            query=query,
            selected_docs=selected_docs,
            top_k=8
        )

        generated_text, answer_mode = generate_answer(
            query=query,
            relevant_fragments=relevant_fragments,
            config=config,
            output_type=output_type,
            use_ai=use_ai,
            documents_data=docs_data
        )

        save_history_entry({
            "fecha": current_datetime_str(),
            "consulta": query,
            "respuesta": generated_text
        })

    st.success("Consulta procesada")

    st.markdown("### Informe")
    render_professional_output(generated_text, relevant_fragments)

    st.markdown("### Fragmentos relevantes")
    for frag in relevant_fragments:
        st.markdown(
            f"""
            <div class="fragment-card">
                <div class="success-pill">{frag["document_name"]}</div>
                <p class="small-muted">
                    Chunk #{frag["fragment_number"]} | Relevancia: {frag["score"]}
                </p>
                <p>{frag["text"]}</p>
            </div>
            """,
            unsafe_allow_html=True
        )