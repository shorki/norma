import uuid
from utils.supabase_store import get_supabase_client


BUCKET_NAME = "documentos"


def upload_file_to_supabase(uploaded_file):
    supabase = get_supabase_client(use_service_role=True)

    unique_name = f"{uuid.uuid4()}_{uploaded_file.name}"
    storage_path = f"documentos/{unique_name}"

    file_bytes = uploaded_file.getvalue()

    supabase.storage.from_(BUCKET_NAME).upload(
        path=storage_path,
        file=file_bytes,
        file_options={
            "content-type": uploaded_file.type or "application/octet-stream"
        }
    )

    return storage_path


def create_document_record(nombre, storage_path):
    supabase = get_supabase_client(use_service_role=True)

    result = supabase.table("documentos").insert({
        "nombre": nombre,
        "storage_path": storage_path
    }).execute()

    return result.data[0]


def list_documents_from_supabase():
    supabase = get_supabase_client(use_service_role=True)
    result = supabase.table("documentos").select("*").order("creado_en", desc=True).execute()
    return result.data or []