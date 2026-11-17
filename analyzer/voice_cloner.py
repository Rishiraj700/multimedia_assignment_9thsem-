"""Voice cloning module supporting local F5-TTS CLI and ElevenLabs API."""

import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

from .file_utils import validate_file


def _clone_with_f5tts(
    ref_audio: Path,
    ref_text: str,
    gen_text: str,
    output_dir: Path,
    model: str = "F5TTS_v1_Base",
) -> dict[str, Any]:
    if shutil.which("f5-tts_infer-cli") is None:
        raise RuntimeError(
            "f5-tts_infer-cli not found in PATH. Install it with `pip install f5-tts`."
        )
    if not ref_text.strip():
        raise ValueError("Reference transcript (--ref-text) is required when using the f5tts backend.")

    output_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        "f5-tts_infer-cli",
        "--model",
        model,
        "--ref_audio",
        str(ref_audio),
        "--ref_text",
        ref_text,
        "--gen_text",
        gen_text,
        "--output_dir",
        str(output_dir),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(
            f"F5-TTS inference failed (exit code {result.returncode}): {result.stderr.strip()}"
        )

    return {
        "Backend": "F5-TTS",
        "Model": model,
        "Reference Audio": str(ref_audio),
        "Generated Text": gen_text,
        "Output Directory": str(output_dir),
        "Status": "Success",
    }


def _clone_with_elevenlabs(
    ref_audio: Path,
    gen_text: str,
    output_path: Path,
    voice_name: str = "ClonedVoice",
) -> dict[str, Any]:
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        raise RuntimeError(
            "ELEVENLABS_API_KEY environment variable is not set."
        )

    try:
        from elevenlabs.client import ElevenLabs
    except ImportError as exc:
        raise RuntimeError(
            "elevenlabs package is not installed. Install it with `pip install elevenlabs`."
        ) from exc

    client = ElevenLabs(api_key=api_key)
    with ref_audio.open("rb") as audio_file:
        voice = client.voices.ivc.create(name=voice_name, files=[audio_file])

    audio_stream = client.text_to_speech.convert(
        voice_id=voice.voice_id,
        text=gen_text,
        model_id="eleven_multilingual_v2",
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("wb") as out:
        for chunk in audio_stream:
            if chunk:
                out.write(chunk)

    return {
        "Backend": "ElevenLabs",
        "Voice ID": voice.voice_id,
        "Reference Audio": str(ref_audio),
        "Generated Text": gen_text,
        "Output File": str(output_path),
        "Status": "Success",
    }


def clone_voice(
    ref_audio: str | Path,
    gen_text: str,
    *,
    backend: str = "f5tts",
    ref_text: str = "",
    output_path: str | Path | None = None,
    model: str = "F5TTS_v1_Base",
) -> dict[str, Any]:
    """Clone a consented reference voice and synthesize speech from text."""
    src = validate_file(ref_audio)
    if not gen_text.strip():
        raise ValueError("Generated text (--text) cannot be empty.")

    selected = backend.lower().strip()
    if selected == "f5tts":
        out_dir = Path(output_path).parent if output_path else Path("reports") / "voice_output"
        return _clone_with_f5tts(src, ref_text, gen_text, out_dir, model=model)
    if selected == "elevenlabs":
        out_file = (
            Path(output_path).expanduser().resolve()
            if output_path
            else Path("reports") / f"{src.stem}_cloned.mp3"
        )
        return _clone_with_elevenlabs(src, gen_text, out_file)

    raise ValueError(f"Unsupported voice cloning backend '{backend}'. Choose 'f5tts' or 'elevenlabs'.")
