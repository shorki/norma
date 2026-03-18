import streamlit as st
from utils.styles import apply_global_styles
from utils.document_storage import (
    upload_file_to_supabase,
    create_document_record,
    list_documents_from_supabase,
    list_bucket_files,
    delete_document_from_supabase,
)

st.set_page_config(page_title="Biblioteca | Norma", page_icon="⚖️", layout="wide")
apply_global_styles()

st.markdown('<div class="section-title">Biblioteca</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-subtitle">Subí, administrá y depurá documentos jurídicos almacenados en la nube.</div>',
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
        col1, col2 = st.columns([6, 1.2])

        with col1:
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

        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Eliminar", key=f"delete_{doc['id']}", use_container_width=True):
                try:
                    result = delete_document_from_supabase(
                        document_id=doc["id"],
                        storage_path=doc.get("storage_path")
                    )

                    if result["storage_deleted"]:
                        st.success("Documento eliminado de Storage y base.")
                    else:
                        st.warning("Se eliminó el registro de la base. El archivo no existía en Storage o no pudo borrarse.")

                    st.rerun()

                except Exception as e:
                    st.error(f"No se pudo eliminar el documento: {e}")

st.markdown("### Archivos visibles en el bucket")

if st.button("Actualizar vista del bucket", use_container_width=True):
    st.rerun()

try:
    files = list_bucket_files()
except Exception as e:
    files = []
    st.error(f"No se pudieron listar archivos del bucket: {e}")

if not files:
    st.info("El bucket no tiene archivos visibles.")
else:
    for file in files:
        name = file.get("name", "Sin nombre")
        metadata = file.get("metadata", {})
        size = metadata.get("size")
        st.markdown(
            f"""
            <div class="doc-card">
                <h4 style="margin-top:0; margin-bottom:8px;">{name}</h4>
                <p class="small-muted">Tamaño: {size if size is not None else "No disponible"}</p>
            </div>
            """,
            unsafe_allow_html=True
        )