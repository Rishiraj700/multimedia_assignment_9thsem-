"""Audio file properties and tag inspection using Mutagen."""

from pathlib import Path
from typing import Any

import mutagen

from .file_utils import format_file_size


def _format_duration(seconds: float) -> str:
    minutes, secs = divmod(seconds, 60)
    if minutes >= 1:
        return f"{seconds:.2f} s ({int(minutes)}m {secs:.1f}s)"
    return f"{seconds:.2f} s"


def analyze_audio(file_path: str | Path) -> dict[str, Any]:
    """Extract duration, sample rate, channels, bitrate, and metadata tags from an audio file."""
    path = Path(file_path)
    report: dict[str, Any] = {
        "File Name": path.name,
        "File Size": format_file_size(path.stat().st_size),
    }

    try:
        audio = mutagen.File(path)
        if audio is None:
            report["Error"] = "Unsupported or unreadable audio format."
            return report

        info = getattr(audio, "info", None)
        if info is not None:
            channels = getattr(info, "channels", None)
            sample_rate = getattr(info, "sample_rate", None)
            bitrate = getattr(info, "bitrate", None)
            length = getattr(info, "length", None)

            report["Audio Format"] = type(audio).__name__
            report["Channels"] = str(channels) if channels is not None else "Unknown"
            report["Sample Rate"] = f"{sample_rate} Hz" if sample_rate else "Unknown"
            report["Bitrate"] = f"{bitrate // 1000} kbps" if bitrate else "Unknown"
            report["Duration"] = _format_duration(float(length)) if length is not None else "Unknown"

        tags = getattr(audio, "tags", None)
        if tags:
            parsed_tags: dict[str, str] = {}
            for key, value in tags.items():
                text_value = str(value).strip()
                if len(text_value) > 200:
                    text_value = f"{text_value[:197]}..."
                parsed_tags[str(key)] = text_value
            if parsed_tags:
                report["Metadata Tags"] = parsed_tags
    except Exception as exc:
        report["Error"] = f"Failed to analyze audio: {exc}"

    return report
