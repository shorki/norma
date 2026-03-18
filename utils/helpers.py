import json
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DOCS_DIR = os.path.join(DATA_DIR, "documentos")
HISTORY_DIR = os.path.join(DATA_DIR, "historial")
CONFIG_DIR = os.path.join(DATA_DIR, "config")
HISTORY_FILE = os.path.join(HISTORY_DIR, "consultas.json")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")


def ensure_directories():
    os.makedirs(DOCS_DIR, exist_ok=True)
    os.makedirs(HISTORY_DIR, exist_ok=True)
    os.makedirs(CONFIG_DIR, exist_ok=True)

    if not os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)

    if not os.path.exists(CONFIG_FILE):
        default_config = {
            "jurisdiccion": "Uruguay",
            "materia": "General",
            "estilo": "Claro y profesional"
        }
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(default_config, f, ensure_ascii=False, indent=2)


def load_config():
    ensure_directories()
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_config(config):
    ensure_directories()
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def save_uploaded_file(uploaded_file):
    ensure_directories()
    file_path = os.path.join(DOCS_DIR, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path


def list_documents():
    ensure_directories()
    files = []
    for name in os.listdir(DOCS_DIR):
        full_path = os.path.join(DOCS_DIR, name)
        if os.path.isfile(full_path):
            stats = os.stat(full_path)
            files.append({
                "name": name,
                "path": full_path,
                "size_kb": round(stats.st_size / 1024, 2),
                "modified": datetime.fromtimestamp(stats.st_mtime).strftime("%d/%m/%Y %H:%M")
            })
    files.sort(key=lambda x: x["name"].lower())
    return files


def delete_document(filename):
    file_path = os.path.join(DOCS_DIR, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        return True
    return False


def load_history():
    ensure_directories()
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_history_entry(entry):
    ensure_directories()
    history = load_history()
    history.insert(0, entry)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def clear_history():
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=2)


def current_datetime_str():
    return datetime.now().strftime("%d/%m/%Y %H:%M")


def shorten_text(text, max_len=220):
    if not text:
        return ""
    text = text.strip().replace("\n", " ")
    return text[:max_len] + "..." if len(text) > max_len else text