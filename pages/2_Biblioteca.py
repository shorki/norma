import streamlit as st
from utils.helpers import save_uploaded_file, list_documents, delete_document
from utils.styles import apply_global_styles
from utils.lector_pdf import read_document
from utils.vector_store import index_document, remove_document_from_index, get_indexed_stats

st.set_page_config(page_title="Biblioteca | Consultador", page_icon="⚖️", layout="wide")
apply_global_styles()

st.markdown('<div class="section-title">Biblioteca</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-subtitle">Subí, guardá e indexá documentos para que Consultador los entienda por significado y no solo por palabras.</div>',
    unsafe_allow_html=True
)

stats = get_indexed_stats()

top1, top2, top3 = st.columns(3)
with top1:
    st.markdown(
        f"""
        <div class="metric-box">
            <div class="small-muted">Documentos indexados</div>
            <h2>{stats["documents_indexed"]}</h2>
        </div>
        """,
        unsafe_allow_html=True
    )
with top2:
    st.markdown(
        f"""
        <div class="metric-box">
            <div class="small-muted">Chunks en Chroma</div>
            <h2>{stats["total_chunks"]}</h2>
        </div>
        """,
        unsafe_allow_html=True
    )
with top3:
    st.markdown(
        """
        <div class="metric-box">
            <div class="small-muted">Modo de búsqueda</div>
            <h2>Semántico</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("### Subir documentos")
uploaded_files = st.file_uploader(
    "Podés subir PDF, DOCX o TXT",
    type=["pdf", "docx", "txt"],
    accept_multiple_files=True
)

if uploaded_files:
    if st.button("Guardar e indexar archivos", use_container_width=True):
        saved = 0
        indexed = 0

        for uploaded_file in uploaded_files:
            file_path = save_uploaded_file(uploaded_file)
            saved += 1

            text = read_document(file_path)
            if text.strip():
                chunks = index_document(uploaded_file.name, text)
                if chunks > 0:
                    indexed += 1

        st.success(f"Se guardaron {saved} archivo(s) y se indexaron {indexed} correctamente.")
        st.rerun()

documents = list_documents()

st.markdown("### Documentos cargados")

if not documents:
    st.info("Todavía no hay documentos cargados.")
else:
    for doc in documents:
        c1, c2, c3 = st.columns([5, 1.3, 1])
        with c1:
            st.markdown(
                f"""
                <div class="doc-card">
                    <h4 style="margin-top:0; margin-bottom:8px;">{doc["name"]}</h4>
                    <p class="small-muted">Tamaño: {doc["size_kb"]} KB</p>
                    <p class="small-muted">Última modificación: {doc["modified"]}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

        with c2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Reindexar", key=f"reindex_{doc['name']}", use_container_width=True):
                text = read_document(doc["path"])
                if text.strip():
                    chunks = index_document(doc["name"], text)
                    st.success(f"Documento reindexado. Chunks generados: {chunks}")
                    st.rerun()
                else:
                    st.error("No se pudo extraer texto del documento.")

        with c3:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Eliminar", key=f"delete_{doc['name']}", use_container_width=True):
                ok = delete_document(doc["name"])
                remove_document_from_index(doc["name"])
                if ok:
                    st.success(f"Se eliminó {doc['name']}")
                    st.rerun()
                else:
                    st.error("No se pudo eliminar el archivo.")