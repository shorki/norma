import streamlit as st
from utils.styles import apply_global_styles
from utils.document_storage import (
    upload_file_to_supabase,
    create_document_record,
    list_documents_from_supabase,
    delete_document_from_supabase,
    update_document_status,
    download_file_bytes_from_supabase,
)
from utils.lector_pdf import read_document_bytes
from utils.vector_store import index_document_in_supabase

st.set_page_config(page_title="biblioteca | norma", page_icon="⚖️", layout="wide")
apply_global_styles()

st.markdown('<div class="section-title">biblioteca</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-subtitle">Subí, indexá y administrá documentos jurídicos almacenados en la nube.</div>',
    unsafe_allow_html=True
)

st.markdown("### Subir e indexar documentos")
uploaded_files = st.file_uploader(
    "Podés subir PDF, DOCX o TXT",
    type=["pdf", "docx", "txt"],
    accept_multiple_files=True
)

if uploaded_files:
    if st.button("Subir e indexar", use_container_width=True):
        processed = 0

        for uploaded_file in uploaded_files:
            document_id = None
            try:
                storage_path = upload_file_to_supabase(uploaded_file)
                record = create_document_record(uploaded_file.name, storage_path)
                document_id = record["id"]

                file_bytes = download_file_bytes_from_supabase(storage_path)
                text = read_document_bytes(file_bytes, uploaded_file.name)

                if not text.strip():
                    update_document_status(document_id, "error", "No se pudo extraer texto del documento.")
                    st.error(f"{uploaded_file.name}: no se pudo extraer texto.")
                    continue

                chunks_count = index_document_in_supabase(document_id, text)
                update_document_status(document_id, "indexado", None)

                processed += 1
                st.success(f"{uploaded_file.name} subido e indexado correctamente ({chunks_count} fragmentos internos).")

            except Exception as e:
                if document_id:
                    try:
                        update_document_status(document_id, "error", str(e))
                    except Exception:
                        pass
                st.error(f"Error procesando {uploaded_file.name}: {e}")

        st.info(f"Resumen: {processed} documento(s) subido(s) e indexado(s).")
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
        col1, col2 = st.columns([6, 1.3])

        estado = doc.get("estado", "subido")
        error_message = doc.get("error_message")

        with col1:
            extra = ""
            if estado == "indexado":
                badge = '<span class="success-pill">Indexado</span>'
            elif estado == "error":
                badge = '<span class="danger-pill">Error</span>'
                if error_message:
                    extra = f'<p class="small-muted">Detalle: {error_message}</p>'
            else:
                badge = '<span class="warning-pill">Subido</span>'

            st.markdown(
                f"""
                <div class="doc-card">
                    <h4 style="margin-top:0; margin-bottom:8px;">{doc["nombre"]}</h4>
                    <p class="small-muted">{badge}</p>
                    <p class="small-muted">Creado en: {doc["creado_en"]}</p>
                    {extra}
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
                        st.success("Documento eliminado.")
                    else:
                        st.warning("Se eliminó el registro. El archivo no existía en storage o no pudo borrarse.")

                    st.rerun()

                except Exception as e:
                    st.error(f"No se pudo eliminar el documento: {e}")