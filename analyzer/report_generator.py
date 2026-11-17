"""Report formatting and persistence in JSON and plain-text formats."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _format_text_lines(data: dict[str, Any], indent: int = 0) -> list[str]:
    lines: list[str] = []
    prefix = "  " * indent
    for key, value in data.items():
        if isinstance(value, dict):
            lines.append(f"{prefix}{key}:")
            lines.extend(_format_text_lines(value, indent + 1))
        else:
            lines.append(f"{prefix}{key}: {value}")
    return lines


def save_report(
    report_data: dict[str, Any],
    output_dir: str | Path = "reports",
    *,
    report_format: str = "json",
    base_name: str = "report",
    print_console: bool = True,
) -> list[Path]:
    """Print the report summary and write it to disk as JSON, TXT, or both."""
    target_dir = Path(output_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    payload = {
        "Generated At (UTC)": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        **report_data,
    }

    if print_console:
        banner = "=" * 50
        print(f"\n{banner}")
        print("MULTIMEDIA ANALYSIS REPORT")
        print(banner)
        print(json.dumps(payload, indent=4))

    saved_paths: list[Path] = []
    fmt = report_format.lower().strip()

    if fmt in ("json", "both"):
        json_path = target_dir / f"{base_name}.json"
        json_path.write_text(json.dumps(payload, indent=4) + "\n", encoding="utf-8")
        saved_paths.append(json_path)

    if fmt in ("txt", "both"):
        txt_path = target_dir / f"{base_name}.txt"
        lines = [
            "MULTIMEDIA ANALYSIS REPORT",
            "=" * 50,
            *_format_text_lines(payload),
        ]
        txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        saved_paths.append(txt_path)

    if print_console and saved_paths:
        for saved in saved_paths:
            print(f"Report saved to: {saved}")

    return saved_paths
