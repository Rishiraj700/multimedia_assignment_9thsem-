"""Unit and integration tests for the Multimedia Analyzer toolkit."""

import json
import math
import shutil
import struct
import subprocess
import tempfile
import unittest
import wave
from pathlib import Path

from PIL import Image

from analyzer import (
    analyze_audio,
    analyze_image,
    analyze_video,
    enhance_image,
    format_file_size,
    identify_media_type,
    save_report,
)
from main import run_cli


def _create_sample_image(path: Path) -> None:
    img = Image.new("RGB", (160, 120), color=(45, 110, 180))
    img.save(path, format="JPEG", dpi=(96, 96))


def _create_sample_wav(path: Path, duration_sec: float = 0.5, sample_rate: int = 16000) -> None:
    n_samples = int(duration_sec * sample_rate)
    with wave.open(str(path), "w") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        frames = bytearray()
        for i in range(n_samples):
            val = int(12000 * math.sin(2 * math.pi * 440.0 * i / sample_rate))
            frames.extend(struct.pack("<h", val))
        wav.writeframes(bytes(frames))


class TestMultimediaAnalyzer(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = Path(tempfile.mkdtemp(prefix="mm_analyzer_test_"))

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_file_utils(self) -> None:
        self.assertEqual(identify_media_type("photo.JPG"), "IMAGE")
        self.assertEqual(identify_media_type("track.mp3"), "AUDIO")
        self.assertEqual(identify_media_type("clip.mp4"), "VIDEO")
        self.assertEqual(identify_media_type("notes.txt"), "UNKNOWN")
        self.assertEqual(format_file_size(512), "512 B")
        self.assertEqual(format_file_size(2048), "2.00 KB")

    def test_image_analysis_and_enhancement(self) -> None:
        img_path = self.tmp_dir / "sample.jpg"
        _create_sample_image(img_path)

        report = analyze_image(img_path)
        self.assertEqual(report["File Format"], "JPEG")
        self.assertEqual(report["Width"], "160 px")
        self.assertEqual(report["Height"], "120 px")
        self.assertEqual(report["Color Mode"], "RGB")

        out_path = self.tmp_dir / "enhanced.jpg"
        enh = enhance_image(
            img_path,
            output_path=out_path,
            brightness=1.2,
            contrast=1.1,
            color=1.1,
            sharpness=1.2,
            denoise=True,
        )
        self.assertEqual(enh["Status"], "Success")
        self.assertTrue(out_path.exists())

    def test_audio_analysis(self) -> None:
        wav_path = self.tmp_dir / "tone.wav"
        _create_sample_wav(wav_path)

        report = analyze_audio(wav_path)
        self.assertEqual(report["Channels"], "1")
        self.assertEqual(report["Sample Rate"], "16000 Hz")
        self.assertIn("0.50 s", report["Duration"])

    @unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "FFmpeg/FFprobe not installed")
    def test_video_analysis(self) -> None:
        vid_path = self.tmp_dir / "clip.mp4"
        cmd = [
            "ffmpeg",
            "-y",
            "-f",
            "lavfi",
            "-i",
            "color=c=blue:s=160x120:d=1",
            "-f",
            "lavfi",
            "-i",
            "sine=frequency=440:duration=1",
            "-c:v",
            "libx264",
            "-c:a",
            "aac",
            "-shortest",
            str(vid_path),
        ]
        subprocess.run(cmd, check=True, capture_output=True)

        report = analyze_video(vid_path)
        self.assertNotIn("Error", report)
        self.assertEqual(report["Video Stream"]["Resolution"], "160x120")
        self.assertEqual(report["Video Stream"]["Codec"], "h264")
        self.assertEqual(report["Audio Stream"]["Codec"], "aac")

    def test_cli_and_report_formats(self) -> None:
        img_path = self.tmp_dir / "cli_sample.jpg"
        _create_sample_image(img_path)
        report_dir = self.tmp_dir / "reports"

        exit_code = run_cli([str(img_path), "--output-dir", str(report_dir), "--format", "both"])
        self.assertEqual(exit_code, 0)

        json_report = report_dir / "cli_sample_report.json"
        txt_report = report_dir / "cli_sample_report.txt"
        self.assertTrue(json_report.exists())
        self.assertTrue(txt_report.exists())

        loaded = json.loads(json_report.read_text(encoding="utf-8"))
        self.assertEqual(loaded["File Type Identified"], "IMAGE")

    def test_save_report(self) -> None:
        saved = save_report({"Status": "OK"}, output_dir=self.tmp_dir, report_format="json", print_console=False)
        self.assertEqual(len(saved), 1)
        self.assertTrue(saved[0].exists())


if __name__ == "__main__":
    unittest.main()
