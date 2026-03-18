import os
from io import BytesIO
from openai import OpenAI


def transcribe_audio_bytes(audio_bytes: bytes, filename: str = "consulta.wav", mime_type: str = "audio/wav") -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Falta la variable de entorno OPENAI_API_KEY.")

    client = OpenAI(api_key=api_key)

    audio_file = BytesIO(audio_bytes)
    audio_file.name = filename

    transcription = client.audio.transcriptions.create(
        model="gpt-4o-mini-transcribe",
        file=audio_file,
    )

    text = getattr(transcription, "text", "") or ""
    return text.strip()