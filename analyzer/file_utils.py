"""Utility helpers for file validation, sizing, and media type classification."""

from pathlib import Path

IMAGE_EXTENSIONS = frozenset({".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".tif", ".webp"})
AUDIO_EXTENSIONS = frozenset({".mp3", ".wav", ".flac", ".ogg", ".m4a", ".aac", ".opus"})
VIDEO_EXTENSIONS = frozenset({".mp4", ".mkv", ".avi", ".mov", ".webm", ".wmv", ".flv"})


def validate_file(file_path: str | Path) -> Path:
    """Resolve and verify that the target path exists and is a regular file."""
    path = Path(file_path).expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    if not path.is_file():
        raise IsADirectoryError(f"Expected a file, got a directory: {file_path}")
    return path


def format_file_size(num_bytes: int) -> str:
    """Convert a byte count into a human-readable string."""
    size = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024.0 or unit == "GB":
            return f"{size:.2f} {unit}" if unit != "B" else f"{int(size)} B"
        size /= 1024.0
    return f"{num_bytes} B"


def identify_media_type(file_path: str | Path) -> str:
    """Classify a file as IMAGE, AUDIO, VIDEO, or UNKNOWN based on its extension."""
    ext = Path(file_path).suffix.lower()
    if ext in IMAGE_EXTENSIONS:
        return "IMAGE"
    if ext in AUDIO_EXTENSIONS:
        return "AUDIO"
    if ext in VIDEO_EXTENSIONS:
        return "VIDEO"
    return "UNKNOWN"
