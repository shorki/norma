import streamlit as st
from utils.styles import apply_global_styles
from utils.document_storage import (
    upload_file_to_supabase,
    create_document_record,
    list_documents_from_supabase,
)
from utils.supabase_store import get_supabase_client

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
    st.write(f"Archivos seleccionados: {len(uploaded_files)}")
    for f in uploaded_files:
        st.write(f"- {f.name}")

    if st.button("Guardar en la nube", use_container_width=True):
        st.warning("Botón presionado. Iniciando subida...")
        saved = 0

        for uploaded_file in uploaded_files:
            try:
                st.write(f"Procesando: {uploaded_file.name}")

                storage_path = upload_file_to_supabase(uploaded_file)
                st.write(f"Subido a Storage con path: {storage_path}")

                record = create_document_record(uploaded_file.name, storage_path)
                st.write(f"Registro creado en DB: {record['id']}")

                saved += 1
                st.success(f"{uploaded_file.name} subido correctamente.")

            except Exception as e:
                st.error(f"Error subiendo {uploaded_file.name}: {e}")

        st.info(f"Resumen: {saved} archivo(s) subido(s).")

st.markdown("### Documentos almacenados")

try:
    documents = list_documents_from_supabase()
    st.write(f"Cantidad en base: {len(documents)}")
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

st.markdown("### Verificación de Storage")

if st.button("Listar archivos del bucket", use_container_width=True):
    try:
        supabase = get_supabase_client(use_service_role=True)
        files = supabase.storage.from_("documentos").list()

        st.write("Contenido del bucket:")
        st.write(files)

        if not files:
            st.warning("El bucket existe, pero no tiene archivos visibles.")
    except Exception as e:
        st.error(f"Error listando bucket: {e}")