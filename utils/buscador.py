import os
import re
import unicodedata
from openai import OpenAI


def normalize_text(text):
    text = text.lower().strip()
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    return text


def build_basic_framework(query, relevant_fragments, config):
    if not relevant_fragments:
        return (
            "No se encontraron fragmentos relevantes para la consulta planteada. "
            "Probá con otra redacción o verificá que los documentos estén indexados."
        )

    jurisdiction = config.get("jurisdiccion", "Uruguay")
    materia = config.get("materia", "General")
    estilo = config.get("estilo", "Claro y profesional")

    docs_used = sorted(list({frag["document_name"] for frag in relevant_fragments}))

    response = f"""
**Análisis preliminar**

La consulta fue interpretada dentro del marco de **{materia}** para la jurisdicción de **{jurisdiction}**.

**Normativa consultada**
{chr(10).join([f"- {doc}" for doc in docs_used])}

**Observación**
La salida tiene un tono **{estilo.lower()}** y constituye apoyo de trabajo, no una conclusión jurídica definitiva.
    """.strip()

    return response


def build_context_for_llm(relevant_fragments):
    if not relevant_fragments:
        return ""

    blocks = []
    for frag in relevant_fragments:
        block = (
            f"[Documento: {frag['document_name']} | Fragmento: {frag['fragment_number']}]\n"
            f"{frag['text']}"
        )
        blocks.append(block)

    return "\n\n".join(blocks)


def is_article_count_question(query):
    q = normalize_text(query)
    patterns = [
        "cuantos articulos tiene",
        "cuantos articulos hay",
        "cantidad de articulos",
        "cuantos articulos contiene",
        "ultimo articulo",
        "articulo final",
        "hasta que articulo llega",
        "cual es el ultimo articulo",
        "hasta que articulo va",
        "cuantos articulos"
    ]
    return any(p in q for p in patterns)


def extract_real_article_numbers_from_full_text(text):
    if not text:
        return []

    lines = text.splitlines()
    numbers = []

    patterns = [
        r"^\s*art[íi]culo\s+(\d{1,4})\s*[\.\-—:]?\s*$",
        r"^\s*art[íi]culo\s+(\d{1,4})\b",
        r"^\s*art\.\s*(\d{1,4})\b",
        r"^\s*art\s+(\d{1,4})\b",
    ]

    for line in lines:
        clean = line.strip()
        if not clean:
            continue
        if len(clean) > 120:
            continue

        low = clean.lower()
        if "página" in low or "pagina" in low:
            continue

        for pattern in patterns:
            match = re.match(pattern, clean, flags=re.IGNORECASE)
            if match:
                try:
                    number = int(match.group(1))
                    if 1 <= number <= 1000:
                        numbers.append(number)
                except ValueError:
                    pass
                break

    return sorted(set(numbers))


def answer_article_count_from_documents(query, documents_data):
    if not is_article_count_question(query):
        return None, None

    best_doc = None
    best_numbers = []

    for doc in documents_data:
        full_text = doc.get("full_text", "") or ""
        numbers = extract_real_article_numbers_from_full_text(full_text)

        if len(numbers) > len(best_numbers):
            best_numbers = numbers
            best_doc = doc["name"]

    if not best_doc or not best_numbers:
        return (
            "No pude identificar con claridad la numeración de artículos en los documentos seleccionados.",
            "regla"
        )

    max_article = max(best_numbers)
    min_article = min(best_numbers)

    response = (
        f"En el documento **{best_doc}** detecté artículos desde el **{min_article}** "
        f"hasta el **{max_article}**."
    )

    if min_article == 1:
        response += f" Si la numeración es continua, el documento tendría **{max_article} artículos**."

    return response, "regla"


def ask_openai_with_context(query, relevant_fragments, config, output_type):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Falta la variable de entorno OPENAI_API_KEY.")

    if not relevant_fragments:
        return (
            "No encontré normativa suficiente para responder con fundamento. "
            "Probá reformular la consulta o verificá que los documentos estén indexados."
        )

    client = OpenAI(api_key=api_key)

    jurisdiction = config.get("jurisdiccion", "Uruguay")
    materia = config.get("materia", "General")
    estilo = config.get("estilo", "Claro y profesional")
    context_text = build_context_for_llm(relevant_fragments)

    system_prompt = f"""
Sos un asistente jurídico documental.
Respondé usando prioritariamente el contexto provisto.
No inventes artículos ni normas.
Escribí en español.
Jurisdicción preferente: {jurisdiction}.
Materia preferente: {materia}.
Estilo de redacción: {estilo}.

La respuesta debe verse profesional y clara.
Preferí una estructura ordenada, con lenguaje jurídico accesible.
    """.strip()

    user_prompt = f"""
Tipo de salida solicitado: {output_type}

Consulta:
{query}

Contexto documental:
{context_text}

Instrucciones:
- Respondé claro y profesional.
- Basate en los fragmentos recuperados.
- Si el contexto no alcanza, decilo expresamente.
- No muestres lenguaje técnico de sistemas.
- Si corresponde, citá de manera natural el documento consultado.
    """.strip()

    response = client.responses.create(
        model="gpt-5.4-mini",
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    return response.output_text.strip()


def generate_answer(query, relevant_fragments, config, output_type, use_ai=True, documents_data=None):
    if documents_data is None:
        documents_data = []

    special_answer, mode = answer_article_count_from_documents(query, documents_data)
    if special_answer:
        return special_answer, mode

    if use_ai:
        try:
            return ask_openai_with_context(query, relevant_fragments, config, output_type), "ia"
        except Exception as e:
            fallback = build_basic_framework(query, relevant_fragments, config)
            fallback += f"\n\n[Nota técnica: no se pudo usar la IA en esta consulta: {str(e)}]"
            return fallback, "fallback"

    return build_basic_framework(query, relevant_fragments, config), "basico"