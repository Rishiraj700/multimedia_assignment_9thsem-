"""Image enhancement utilities using Pillow filters and adjustments."""

from pathlib import Path
from typing import Any

from PIL import Image, ImageEnhance, ImageFilter

from .file_utils import validate_file


def enhance_image(
    input_path: str | Path,
    output_path: str | Path | None = None,
    *,
    brightness: float = 1.0,
    contrast: float = 1.0,
    color: float = 1.0,
    sharpness: float = 1.0,
    denoise: bool = False,
) -> dict[str, Any]:
    """Apply brightness, contrast, saturation, sharpness, and optional median denoising."""
    src = validate_file(input_path)

    for param_name, param_val in (
        ("brightness", brightness),
        ("contrast", contrast),
        ("color", color),
        ("sharpness", sharpness),
    ):
        if param_val < 0:
            raise ValueError(f"{param_name} factor must be non-negative, got {param_val}")

    dest = (
        Path(output_path).expanduser().resolve()
        if output_path
        else src.with_name(f"{src.stem}_enhanced{src.suffix}")
    )
    dest.parent.mkdir(parents=True, exist_ok=True)

    with Image.open(src) as img:
        working = img.convert("RGB") if img.mode not in ("RGB", "RGBA") else img.copy()

        if brightness != 1.0:
            working = ImageEnhance.Brightness(working).enhance(brightness)
        if contrast != 1.0:
            working = ImageEnhance.Contrast(working).enhance(contrast)
        if color != 1.0:
            working = ImageEnhance.Color(working).enhance(color)
        if sharpness != 1.0:
            working = ImageEnhance.Sharpness(working).enhance(sharpness)
        if denoise:
            working = working.filter(ImageFilter.MedianFilter(size=3))

        if dest.suffix.lower() in (".jpg", ".jpeg") and working.mode == "RGBA":
            working = working.convert("RGB")

        working.save(dest)

    return {
        "Input File": str(src),
        "Output File": str(dest),
        "Operations Applied": {
            "Brightness": brightness,
            "Contrast": contrast,
            "Color": color,
            "Sharpness": sharpness,
            "Denoise": denoise,
        },
        "Status": "Success",
    }
