"""Image metadata and EXIF analysis powered by Pillow."""

from pathlib import Path
from typing import Any

from PIL import Image
from PIL.ExifTags import TAGS

from .file_utils import format_file_size

EXIF_FIELD_MAP = {
    "Make": "Camera Make",
    "Model": "Camera Model",
    "DateTime": "Date Taken",
    "DateTimeOriginal": "Date Originally Taken",
    "Orientation": "Orientation",
    "Software": "Software",
    "ExposureTime": "Exposure Time",
    "FNumber": "Aperture (F-Number)",
    "ISOSpeedRatings": "ISO",
}


def analyze_image(file_path: str | Path) -> dict[str, Any]:
    """Extract file properties, dimensions, color mode, and EXIF metadata from an image."""
    path = Path(file_path)
    report: dict[str, Any] = {
        "File Name": path.name,
        "File Size": format_file_size(path.stat().st_size),
    }

    try:
        with Image.open(path) as img:
            width, height = img.size
            dpi = img.info.get("dpi")
            report.update(
                {
                    "File Format": img.format or "Unknown",
                    "Width": f"{width} px",
                    "Height": f"{height} px",
                    "Aspect Ratio": f"{width / height:.2f}" if height else "Unknown",
                    "Resolution (DPI)": f"{dpi[0]} x {dpi[1]}" if isinstance(dpi, tuple) and len(dpi) >= 2 else "Unknown",
                    "Color Mode": img.mode,
                    "Animated": bool(getattr(img, "is_animated", False)),
                }
            )

            raw_exif = img.getexif()
            if raw_exif:
                exif_summary: dict[str, str] = {}
                for tag_id, value in raw_exif.items():
                    tag_name = TAGS.get(tag_id, str(tag_id))
                    if tag_name in EXIF_FIELD_MAP:
                        exif_summary[EXIF_FIELD_MAP[tag_name]] = str(value).strip()
                if exif_summary:
                    report["EXIF Metadata"] = exif_summary
    except Exception as exc:
        report["Error"] = f"Failed to analyze image: {exc}"

    return report
