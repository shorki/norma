import hashlib
import streamlit as st
from utils.helpers import load_config, save_history_entry, current_datetime_str
from utils.document_storage import list_documents_from_supabase, download_file_bytes_from_supabase
from utils.lector_pdf import read_document_bytes
from utils.vector_store import semantic_search
from utils.buscador import generate_answer
from utils.audio_transcription import transcribe_audio_bytes
from utils.styles import apply_global_styles

st.set_page_config(page_title="consultar | norma", page_icon="⚖️", layout="wide")
apply_global_styles()

st.markdown('<div class="section-title">consultar</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-subtitle">Realizá consultas jurídicas por escrito o por voz sobre la normativa cargada e indexada.</div>',
    unsafe_allow_html=True
)

config = load_config()

try:
    documents = list_documents_from_supabase()
except Exception as e:
    documents = []
    st.error(f"No se pudieron cargar los documentos: {e}")

indexed_docs = [doc for doc in documents if doc.get("estado") == "indexado"]

if not indexed_docs:
    st.warning("Todavía no hay documentos indexados en la biblioteca.")
    st.stop()

if "consulta_texto" not in st.session_state:
    st.session_state["consulta_texto"] = ""

if "ultimo_audio_hash" not in st.session_state:
    st.session_state["ultimo_audio_hash"] = ""

if "transcripcion_voz" not in st.session_state:
    st.session_state["transcripcion_voz"] = ""


def render_professional_output(answer_text, relevant_fragments):
    docs_used = sorted(list({frag["document_name"] for frag in relevant_fragments})) if relevant_fragments else []

    st.markdown('<div class="legal-output-card">', unsafe_allow_html=True)

    st.markdown(
        """
        <div class="legal-header-row">
            <div class="legal-badge">INFORME</div>
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
                <div class="legal-section-title">Normativa consultada</div>
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
        "La presente respuesta constituye apoyo de análisis jurídico y no sustituye una revisión profesional del caso concreto."
    )

    st.markdown("</div>", unsafe_allow_html=True)


doc_options = {f'{doc["nombre"]} ({doc["estado"]})': doc for doc in indexed_docs}

st.markdown("### Consulta")

voice_col, text_col = st.columns([1, 1.4])

with voice_col:
    st.markdown("#### Consulta por voz")
    audio_value = st.audio_input("Grabá tu consulta")

    if audio_value is not None:
        st.audio(audio_value)

        try:
            audio_bytes = audio_value.read()
            audio_hash = hashlib.md5(audio_bytes).hexdigest()

            if audio_hash != st.session_state["ultimo_audio_hash"]:
                transcript = transcribe_audio_bytes(
                    audio_bytes=audio_bytes,
                    filename="consulta.wav",
                    mime_type="audio/wav"
                )

                st.session_state["ultimo_audio_hash"] = audio_hash
                st.session_state["transcripcion_voz"] = transcript
                st.session_state["consulta_texto"] = transcript
                st.rerun()

        except Exception as e:
            st.error(f"No se pudo transcribir el audio: {e}")

with text_col:
    st.markdown("#### Consulta escrita")
    st.text_area(
        "Consulta",
        key="consulta_texto",
        placeholder="Ejemplo: si el poder no aclara cómo actúan dos apoderados, cómo deben actuar",
        height=180
    )

    if st.session_state.get("transcripcion_voz"):
        st.caption("La consulta fue cargada desde audio. Podés editarla antes de consultar.")

st.markdown("### Parámetros")

param_col1, param_col2 = st.columns([1.2, 0.8])

with param_col1:
    selected_labels = st.multiselect(
        "Documentos",
        options=list(doc_options.keys()),
        default=list(doc_options.keys())
    )

with param_col2:
    output_type = st.selectbox(
        "Tipo de salida",
        [
            "Respuesta directa",
            "Marco conceptual",
            "Resumen",
            "Puntos clave"
        ]
    )

    use_ai = st.toggle("Usar IA", value=True)

search_button = st.button("Consultar", use_container_width=True)

if search_button:
    query = st.session_state.get("consulta_texto", "").strip()

    if not query:
        st.error("Ingresá o grabá una consulta.")
        st.stop()

    if not selected_labels:
        st.error("Seleccioná al menos un documento.")
        st.stop()

    selected_docs = [doc_options[label] for label in selected_labels]
    selected_doc_ids = [doc["id"] for doc in selected_docs]

    with st.spinner("Procesando consulta..."):
        docs_data = []

        for doc in selected_docs:
            try:
                file_bytes = download_file_bytes_from_supabase(doc["storage_path"])
                text = read_document_bytes(file_bytes, doc["nombre"])

                docs_data.append({
                    "name": doc["nombre"],
                    "full_text": text,
                    "fragments": []
                })
            except Exception:
                pass

        relevant_fragments = semantic_search(
            query=query,
            selected_doc_ids=selected_doc_ids,
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