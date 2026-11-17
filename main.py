"""Command-line interface for the Multimedia Analyzer toolkit."""

import argparse
import sys
from pathlib import Path
from typing import Any

from analyzer import (
    analyze_audio,
    analyze_image,
    analyze_video,
    clone_voice,
    enhance_image,
    identify_media_type,
    save_report,
    validate_file,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="multimedia-analyzer",
        description="Analyze images, audio, and video files, enhance images, or clone voices.",
    )
    parser.add_argument("file", help="Path to the input image, audio, or video file")

    # Mode switches
    parser.add_argument(
        "--enhance",
        action="store_true",
        help="Enhance an image file using Pillow adjustments",
    )
    parser.add_argument(
        "--voice-clone",
        action="store_true",
        help="Clone a voice from a reference audio file and synthesize speech",
    )

    # Image enhancement options
    enhance_group = parser.add_argument_group("Image Enhancement Options")
    enhance_group.add_argument("--brightness", type=float, default=1.15, help="Brightness factor (default: 1.15)")
    enhance_group.add_argument("--contrast", type=float, default=1.1, help="Contrast factor (default: 1.1)")
    enhance_group.add_argument("--color", type=float, default=1.05, help="Color saturation factor (default: 1.05)")
    enhance_group.add_argument("--sharpness", type=float, default=1.1, help="Sharpness factor (default: 1.1)")
    enhance_group.add_argument("--denoise", action="store_true", help="Apply median filter denoising")
    enhance_group.add_argument("-o", "--output", help="Custom output file path for enhanced image or cloned audio")

    # Voice cloning options
    voice_group = parser.add_argument_group("Voice Cloning Options")
    voice_group.add_argument("--text", help="Target text to speak with the cloned voice")
    voice_group.add_argument("--ref-text", default="", help="Transcript of the reference audio (required for f5tts)")
    voice_group.add_argument(
        "--backend",
        choices=("f5tts", "elevenlabs"),
        default="f5tts",
        help="Voice cloning backend to use (default: f5tts)",
    )
    voice_group.add_argument("--model", default="F5TTS_v1_Base", help="F5-TTS model name (default: F5TTS_v1_Base)")

    # Report options
    report_group = parser.add_argument_group("Report Options")
    report_group.add_argument("--output-dir", default="reports", help="Directory to save reports (default: reports)")
    report_group.add_argument(
        "--format",
        choices=("json", "txt", "both"),
        default="json",
        help="Report output format (default: json)",
    )
    return parser


def run_cli(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        target_path = validate_file(args.file)
    except (FileNotFoundError, IsADirectoryError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    media_type = identify_media_type(target_path)
    report: dict[str, Any] = {"File Type Identified": media_type}

    if args.enhance:
        if media_type != "IMAGE":
            print(f"Error: --enhance requires an image file, got {media_type}.", file=sys.stderr)
            return 1
        try:
            report.update(analyze_image(target_path))
            report["Enhancement"] = enhance_image(
                target_path,
                output_path=args.output,
                brightness=args.brightness,
                contrast=args.contrast,
                color=args.color,
                sharpness=args.sharpness,
                denoise=args.denoise,
            )
        except Exception as exc:
            print(f"Error during image enhancement: {exc}", file=sys.stderr)
            return 1
        save_report(
            report,
            output_dir=args.output_dir,
            report_format=args.format,
            base_name=f"{Path(target_path).stem}_enhanced_report",
        )
        return 0

    if args.voice_clone:
        if media_type != "AUDIO":
            print(f"Error: --voice-clone requires an audio file, got {media_type}.", file=sys.stderr)
            return 1
        if not args.text:
            print("Error: --text is required when using --voice-clone.", file=sys.stderr)
            return 1
        try:
            report.update(analyze_audio(target_path))
            report["Voice Cloning"] = clone_voice(
                target_path,
                args.text,
                backend=args.backend,
                ref_text=args.ref_text,
                output_path=args.output,
                model=args.model,
            )
        except Exception as exc:
            print(f"Error during voice cloning: {exc}", file=sys.stderr)
            return 1
        save_report(
            report,
            output_dir=args.output_dir,
            report_format=args.format,
            base_name=f"{Path(target_path).stem}_voice_clone_report",
        )
        return 0

    if media_type == "IMAGE":
        report.update(analyze_image(target_path))
    elif media_type == "AUDIO":
        report.update(analyze_audio(target_path))
    elif media_type == "VIDEO":
        report.update(analyze_video(target_path))
    else:
        print(f"Error: Unsupported file format for '{target_path.name}'.", file=sys.stderr)
        return 1

    save_report(
        report,
        output_dir=args.output_dir,
        report_format=args.format,
        base_name=f"{Path(target_path).stem}_report",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(run_cli())
