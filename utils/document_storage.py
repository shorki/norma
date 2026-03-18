import re
import uuid
import unicodedata
from utils.supabase_store import get_supabase_client


BUCKET_NAME = "documentos"


def sanitize_filename(filename: str) -> str:
    if "." in filename:
        name_part, extension = filename.rsplit(".", 1)
        extension = "." + extension.lower()
    else:
        name_part = filename
        extension = ""

    normalized = unicodedata.normalize("NFD", name_part)
    normalized = "".join(c for c in normalized if unicodedata.category(c) != "Mn")
    normalized = normalized.replace(" ", "_")
    normalized = re.sub(r"[^A-Za-z0-9_\-]", "", normalized)

    if not normalized:
        normalized = "documento"

    return normalized + extension


def upload_file_to_supabase(uploaded_file):
    supabase = get_supabase_client(use_service_role=True)

    safe_name = sanitize_filename(uploaded_file.name)
    unique_name = f"{uuid.uuid4()}_{safe_name}"
    storage_path = unique_name

    file_bytes = uploaded_file.getvalue()

    response = supabase.storage.from_(BUCKET_NAME).upload(
        path=storage_path,
        file=file_bytes,
        file_options={
            "content-type": uploaded_file.type or "application/octet-stream"
        }
    )

    if response is None:
        raise RuntimeError("Supabase no devolvió respuesta al subir el archivo.")

    return storage_path


def download_file_bytes_from_supabase(storage_path: str):
    supabase = get_supabase_client(use_service_role=True)
    return supabase.storage.from_(BUCKET_NAME).download(storage_path)


def create_document_record(nombre, storage_path):
    supabase = get_supabase_client(use_service_role=True)

    result = supabase.table("documentos").insert({
        "nombre": nombre,
        "storage_path": storage_path,
        "estado": "subido"
    }).execute()

    if not result.data:
        raise RuntimeError("No se pudo crear el registro del documento en la base.")

    return result.data[0]


def update_document_status(document_id, estado, error_message=None):
    supabase = get_supabase_client(use_service_role=True)

    payload = {
        "estado": estado,
        "error_message": error_message
    }

    result = supabase.table("documentos").update(payload).eq("id", document_id).execute()
    return result.data


def list_documents_from_supabase():
    supabase = get_supabase_client(use_service_role=True)
    result = supabase.table("documentos").select("*").order("creado_en", desc=True).execute()
    return result.data or []


def delete_document_from_supabase(document_id, storage_path=None):
    supabase = get_supabase_client(use_service_role=True)

    storage_deleted = False

    if storage_path:
        try:
            supabase.storage.from_(BUCKET_NAME).remove([storage_path])
            storage_deleted = True
        except Exception:
            storage_deleted = False

    db_result = supabase.table("documentos").delete().eq("id", document_id).execute()

    if not db_result.data:
        raise RuntimeError("No se pudo eliminar el registro del documento en la base.")

    return {
        "storage_deleted": storage_deleted,
        "db_deleted": True
    }