"""
Pipeline orchestration: STT -> Summarise -> Translate -> TTS
"""
import os
import tempfile
from typing import Optional, Tuple

from backend.sunbird_client import speech_to_text, text_to_speech, summarize_text, translate_text

# Supported target languages for translation
SUPPORTED_LANGUAGES = ["Luganda", "Runyankole", "Ateso", "Lugbara", "Acholi"]


def _get_audio_duration_seconds(audio_path: str) -> float:
    """
    Estimate audio duration in seconds.
    Tries mutagen first, then wave, then falls back to file-size heuristic.
    """
    try:
        from mutagen.mp3 import MP3
        audio = MP3(audio_path)
        return audio.info.length
    except Exception:
        pass

    try:
        import wave
        with wave.open(audio_path, "rb") as wf:
            frames = wf.getnframes()
            rate = wf.getframerate()
            return frames / float(rate)
    except Exception:
        pass

    # Fallback: assume ~1MB per minute for MP3 at 128kbps (~960KB/min)
    size_bytes = os.path.getsize(audio_path)
    estimated = (size_bytes / (128 * 1024 / 8))  # 128 kbps = 16 KB/s
    return estimated


def run_pipeline(
    input_mode: str,
    text_input: Optional[str],
    audio_input: Optional[str],
    target_language: str,
) -> Tuple[str, str, str, str, Optional[str]]:
    """
    Run the full pipeline based on user input.

    Args:
        input_mode: "text" or "audio"
        text_input: The text entered by the user (if mode is text)
        audio_input: The path to the uploaded audio file (if mode is audio)
        target_language: One of the supported languages

    Returns:
        Tuple of (original_text, transcript, summary, translation, audio_url)
        transcript is empty when input_mode is "text".
        audio_url may be None if TTS fails.
    """
    if target_language not in SUPPORTED_LANGUAGES:
        raise ValueError(
            f"Unsupported target language: {target_language}. "
            f"Choose from: {', '.join(SUPPORTED_LANGUAGES)}"
        )

    # Step 1: Determine original text and transcript
    if input_mode == "audio":
        if not audio_input:
            raise ValueError("Please upload an audio file.")

        duration = _get_audio_duration_seconds(audio_input)
        if duration > 300:
            raise ValueError(
                f"Audio file is too long ({duration:.0f} seconds). "
                "Maximum allowed duration is 5 minutes (300 seconds)."
            )

        transcript = speech_to_text(audio_input)
        original_text = transcript
    else:
        if not text_input or not text_input.strip():
            raise ValueError("Please enter some text.")
        original_text = text_input.strip()
        transcript = ""

    # Step 2: Summarise
    summary = summarize_text(original_text)

    # Step 3: Translate
    translation = translate_text(summary, target_language)

    # Step 4: Text-to-Speech
    audio_url = text_to_speech(translation, target_language)

    return original_text, transcript, summary, translation, audio_url
