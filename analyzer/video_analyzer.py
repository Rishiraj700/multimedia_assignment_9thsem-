"""Video container and stream analysis powered by FFprobe."""

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

from .file_utils import format_file_size


def _parse_frame_rate(raw_rate: str | None) -> str:
    if not raw_rate or raw_rate == "0/0":
        return "Unknown"
    if "/" in raw_rate:
        num, den = raw_rate.split("/", maxsplit=1)
        try:
            fps = float(num) / float(den)
            return f"{fps:.2f} fps ({raw_rate})"
        except (ValueError, ZeroDivisionError):
            return raw_rate
    return raw_rate


def _probe_video(file_path: Path) -> dict[str, Any]:
    if shutil.which("ffprobe") is None:
        raise RuntimeError(
            "ffprobe executable not found in PATH. Install FFmpeg to enable video analysis."
        )

    cmd = [
        "ffprobe",
        "-v",
        "quiet",
        "-print_format",
        "json",
        "-show_format",
        "-show_streams",
        str(file_path),
    ]
    completed = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if completed.returncode != 0 or not completed.stdout.strip():
        stderr_msg = completed.stderr.strip() or "ffprobe returned empty output."
        raise RuntimeError(f"ffprobe failed: {stderr_msg}")
    return json.loads(completed.stdout)


def analyze_video(file_path: str | Path) -> dict[str, Any]:
    """Inspect video container format, duration, video stream, and audio stream details."""
    path = Path(file_path)
    report: dict[str, Any] = {
        "File Name": path.name,
        "File Size": format_file_size(path.stat().st_size),
    }

    try:
        probe_data = _probe_video(path)
    except Exception as exc:
        report["Error"] = str(exc)
        return report

    fmt = probe_data.get("format", {})
    streams = probe_data.get("streams", [])

    report["Container"] = fmt.get("format_long_name") or fmt.get("format_name") or "Unknown"
    duration_raw = fmt.get("duration")
    report["Duration"] = f"{float(duration_raw):.2f} s" if duration_raw else "Unknown"

    video_stream = next((s for s in streams if s.get("codec_type") == "video"), None)
    audio_stream = next((s for s in streams if s.get("codec_type") == "audio"), None)

    if video_stream:
        v_bitrate = video_stream.get("bit_rate")
        report["Video Stream"] = {
            "Codec": video_stream.get("codec_name", "Unknown"),
            "Resolution": f"{video_stream.get('width', 'Unknown')}x{video_stream.get('height', 'Unknown')}",
            "Frame Rate": _parse_frame_rate(video_stream.get("avg_frame_rate") or video_stream.get("r_frame_rate")),
            "Bitrate": f"{int(v_bitrate) // 1000} kbps" if v_bitrate else "Unknown",
            "Pixel Format": video_stream.get("pix_fmt", "Unknown"),
        }

    if audio_stream:
        a_bitrate = audio_stream.get("bit_rate")
        report["Audio Stream"] = {
            "Codec": audio_stream.get("codec_name", "Unknown"),
            "Channels": str(audio_stream.get("channels", "Unknown")),
            "Sample Rate": f"{audio_stream.get('sample_rate', 'Unknown')} Hz",
            "Bitrate": f"{int(a_bitrate) // 1000} kbps" if a_bitrate else "Unknown",
        }

    tags = fmt.get("tags")
    if tags:
        report["Container Metadata"] = {str(k): str(v) for k, v in tags.items()}

    return report
