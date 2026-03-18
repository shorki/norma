import streamlit as st
from utils.styles import apply_global_styles
from utils.document_storage import (
    upload_file_to_supabase,
    create_document_record,
    list_documents_from_supabase,
)

st.set_page_config(page_title="Biblioteca | Norma", page_icon="⚖️", layout="wide")
apply_global_styles()

st.markdown('<div class="section-title">Biblioteca</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-subtitle">Subí y almacená documentos jurídicos en la nube.</div>',
    unsafe_allow_html=True
)

st.markdown("### Subir documentos")
uploaded_files = st.file_uploader(
    "Podés subir PDF, DOCX o TXT",
    type=["pdf", "docx", "txt"],
    accept_multiple_files=True
)

if uploaded_files:
    if st.button("Guardar en la nube", use_container_width=True):
        saved = 0

        for uploaded_file in uploaded_files:
            try:
                storage_path = upload_file_to_supabase(uploaded_file)
                create_document_record(uploaded_file.name, storage_path)
                saved += 1
                st.success(f"{uploaded_file.name} subido correctamente.")
            except Exception as e:
                st.error(f"Error subiendo {uploaded_file.name}: {e}")

        st.info(f"Resumen: {saved} archivo(s) subido(s).")
        st.rerun()

st.markdown("### Documentos almacenados")

try:
    documents = list_documents_from_supabase()
except Exception as e:
    documents = []
    st.error(f"No se pudieron listar documentos desde Supabase: {e}")

if not documents:
    st.info("Todavía no hay documentos almacenados.")
else:
    for doc in documents:
        st.markdown(
            f"""
            <div class="doc-card">
                <h4 style="margin-top:0; margin-bottom:8px;">{doc["nombre"]}</h4>
                <p class="small-muted">Storage path: {doc["storage_path"]}</p>
                <p class="small-muted">Creado en: {doc["creado_en"]}</p>
            </div>
            """,
            unsafe_allow_html=True
        )