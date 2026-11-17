# Multimedia Analyzer

A Python CLI toolkit for analyzing images, audio, and video files, enhancing images, and cloning voices using either local **F5-TTS** or the **ElevenLabs** API.

## Features

- **Image Analysis (`analyzer/image_analyzer.py`)**
  - File name, human-readable size, format, dimensions, aspect ratio, DPI, color mode, and animation flag
  - EXIF metadata extraction (camera make/model, capture date, orientation, software, exposure, aperture, ISO)
- **Image Enhancement (`analyzer/image_enhancer.py`)**
  - Brightness, contrast, color saturation, sharpness adjustments, and optional median-filter denoising via Pillow
- **Audio Analysis (`analyzer/audio_analyzer.py`)**
  - Format detection, channels, sample rate, bitrate, duration, and ID3/container tags via Mutagen
- **Video Analysis (`analyzer/video_analyzer.py`)**
  - Container metadata, duration, video stream (codec, resolution, frame rate, bitrate, pixel format), and audio stream (codec, channels, sample rate, bitrate) via FFprobe
- **Voice Cloning (`analyzer/voice_cloner.py`)**
  - Supports local **F5-TTS** (`f5-tts_infer-cli`) and cloud **ElevenLabs** API (`ELEVENLABS_API_KEY`)
- **Report Generation (`analyzer/report_generator.py`)**
  - Prints formatted console output and saves structured `JSON` and/or `TXT` reports in `reports/`

## Project Structure

```text
multimedia_analyzer/
├── main.py                     # Unified CLI entry point
├── analyzer/
│   ├── __init__.py
│   ├── file_utils.py           # File validation, sizing, and type classification
│   ├── image_analyzer.py       # Pillow image & EXIF analyzer
│   ├── image_enhancer.py       # Pillow image enhancement pipeline
│   ├── audio_analyzer.py       # Mutagen audio analyzer
│   ├── video_analyzer.py       # FFprobe video/audio stream analyzer
│   ├── voice_cloner.py         # F5-TTS & ElevenLabs voice cloning wrapper
│   └── report_generator.py     # JSON / TXT report exporter
├── samples/                    # Sample image, audio, and video files
├── reports/                    # Generated analysis reports
├── tests/
│   └── test_analyzer.py        # Unit and integration tests
├── requirements.txt
└── README.md
```

## Setup

### 1. Clone the repository
```bash
git clone https://github.com/Rishiraj700/multimedia_assignment_9thsem-.git
cd multimedia_assignment_9thsem-
```

### 2. Install Python dependencies
```bash
pip install -r requirements.txt
```

For voice cloning, also install your preferred backend:
```bash
# Option A: Local F5-TTS
pip install f5-tts

# Option B: ElevenLabs API
pip install elevenlabs
```

### 3. Install FFmpeg (required for video analysis)
- **Windows:** `winget install Gyan.FFmpeg` (or `choco install ffmpeg`)
- **macOS:** `brew install ffmpeg`
- **Ubuntu/Debian:** `sudo apt-get install ffmpeg`

## Usage

### Analyze an image, audio, or video file
```bash
python main.py samples/sample_image.jpg
python main.py samples/sample_audio.wav
python main.py samples/sample_video.mp4
```

Export both JSON and TXT reports:
```bash
python main.py samples/sample_image.jpg --format both
```

### Enhance an image
```bash
python main.py samples/sample_image.jpg --enhance --brightness 1.2 --contrast 1.15 --sharpness 1.2 --denoise
```

### Clone a voice
Using local F5-TTS:
```bash
python main.py samples/sample_audio.wav --voice-clone \
  --backend f5tts \
  --ref-text "Exact transcript of the reference audio" \
  --text "Hello, this is my cloned voice."
```

Using ElevenLabs API:
```bash
# PowerShell
$env:ELEVENLABS_API_KEY="your-api-key-here"

python main.py samples/sample_audio.wav --voice-clone \
  --backend elevenlabs \
  --text "Hello, this is my cloned voice."
```

## Running Tests

```bash
python -m unittest discover -s tests -v
```
