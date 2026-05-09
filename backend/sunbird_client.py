"""
Thin wrapper around the Sunbird AI API endpoints.
Handles authentication, request formatting, and error handling.
"""
import os
import requests

BASE_URL = "https://api.sunbird.ai"

# TTS speaker IDs mapped to language names
SPEAKER_IDS = {
    "Luganda": 248,
    "Runyankole": 243,
    "Ateso": 242,
    "Lugbara": 245,
    "Acholi": 241,
}


def _auth_header() -> dict:
    token = os.environ.get("SUNBIRD_API_TOKEN", "")
    if not token:
        raise ValueError("SUNBIRD_API_TOKEN environment variable is not set.")
    return {"Authorization": f"Bearer {token}"}


def speech_to_text(audio_path: str) -> str:
    """
    Transcribe an audio file to text using Sunbird STT API.
    Returns the transcribed text.
    """
    url = f"{BASE_URL}/tasks/stt"
    headers = _auth_header()  # No Content-Type — requests sets multipart boundary

    with open(audio_path, "rb") as f:
        files = {"audio": f}
        response = requests.post(url, files=files, headers=headers, timeout=120)

    response.raise_for_status()
    data = response.json()
    output = data.get("output", {})
    return output.get("text", "")


def text_to_speech(text: str, language: str) -> str:
    """
    Convert text to speech using Sunbird TTS API.
    Returns the URL to the generated audio file.
    """
    speaker_id = SPEAKER_IDS.get(language)
    if speaker_id is None:
        raise ValueError(f"Unsupported language for TTS: {language}")

    url = f"{BASE_URL}/tasks/tts"
    headers = _auth_header()
    payload = {"text": text, "speaker_id": speaker_id}

    # The TTS endpoint accepts JSON (docs) but may also work with form data.
    # We try JSON first and fall back to form data on 5xx errors.
    try:
        response = requests.post(
            url, json=payload, headers={**headers, "Content-Type": "application/json"}, timeout=180
        )
        response.raise_for_status()
    except requests.HTTPError as exc:
        if exc.response.status_code >= 500:
            response = requests.post(url, data=payload, headers=headers, timeout=180)
            response.raise_for_status()
        else:
            raise

    data = response.json()
    output = data.get("output", {})
    return output.get("audio_url", "")


def summarize_text(text: str, model_type: str = "qwen", temperature: float = 0.3) -> str:
    """
    Summarize the provided text using Sunflower simple inference.
    """
    url = f"{BASE_URL}/tasks/sunflower_simple"
    headers = _auth_header()
    instruction = (
        "Please provide a concise summary (2-3 sentences) of the following text. "
        "Only return the summary without extra commentary.\n\n" + text
    )
    payload = {
        "instruction": instruction,
        "model_type": model_type,
        "temperature": str(temperature),
    }

    response = requests.post(url, data=payload, headers=headers, timeout=120)
    response.raise_for_status()
    data = response.json()
    return data.get("response", "").strip()


def translate_text(text: str, target_language: str, model_type: str = "qwen", temperature: float = 0.3) -> str:
    """
    Translate the provided text into the target Ugandan language using Sunflower simple inference.
    """
    url = f"{BASE_URL}/tasks/sunflower_simple"
    headers = _auth_header()
    instruction = (
        f"Translate the following text into {target_language}. "
        f"Only return the translation without extra commentary.\n\n" + text
    )
    payload = {
        "instruction": instruction,
        "model_type": model_type,
        "temperature": str(temperature),
    }

    response = requests.post(url, data=payload, headers=headers, timeout=120)
    response.raise_for_status()
    data = response.json()
    return data.get("response", "").strip()
