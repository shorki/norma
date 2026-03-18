import streamlit as st
from utils.helpers import load_history, clear_history, shorten_text
from utils.styles import apply_global_styles

st.set_page_config(page_title="Historial | Consultador", page_icon="⚖️", layout="wide")
apply_global_styles()

st.markdown('<div class="section-title">Historial</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-subtitle">Consultas guardadas y respuestas generadas por la aplicación.</div>',
    unsafe_allow_html=True
)

history = load_history()

top1, top2 = st.columns([4, 1])
with top1:
    st.markdown(
        f"""
        <div class="result-card">
            <h4 style="margin-top:0;">Consultas registradas</h4>
            <p>Actualmente hay <strong>{len(history)}</strong> consulta(s) guardada(s).</p>
        </div>
        """,
        unsafe_allow_html=True
    )
with top2:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Limpiar historial", use_container_width=True):
        clear_history()
        st.success("Historial eliminado.")
        st.rerun()

if not history:
    st.info("No hay consultas guardadas todavía.")
else:
    for i, item in enumerate(history, start=1):
        with st.expander(f"{i}. {item['fecha']} · {shorten_text(item['consulta'], 80)}"):
            st.markdown(
                f"""
                <div class="result-card">
                    <p><strong>Consulta:</strong><br>{item['consulta']}</p>
                    <p><strong>Tipo de salida:</strong> {item.get('tipo_salida', 'No definido')}</p>
                    <p><strong>Documentos usados:</strong> {", ".join(item.get("documentos", []))}</p>
                    <p><strong>Respuesta:</strong><br>{item.get('respuesta', '')}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

            fragmentos = item.get("fragmentos", [])
            if fragmentos:
                st.markdown("#### Fragmentos encontrados")
                for frag in fragmentos:
                    st.markdown(
                        f"""
                        <div class="fragment-card">
                            <div class="success-pill">{frag["documento"]}</div>
                            <p class="small-muted" style="margin-top:10px;">
                                Fragmento #{frag["fragmento"]} · Score: {frag["score"]}
                            </p>
                            <p style="margin-top:10px;">{frag["texto"]}</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )