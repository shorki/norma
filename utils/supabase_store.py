import os
from supabase import create_client


def get_supabase_client(use_service_role: bool = False):
    url = os.getenv("SUPABASE_URL")

    if use_service_role:
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    else:
        key = os.getenv("SUPABASE_ANON_KEY")

    if not url or not key:
        raise RuntimeError("Faltan credenciales de Supabase en variables de entorno.")

    return create_client(url, key)