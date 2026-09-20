# Timecode Speech-to-Text (STT) Processing Tool

Welcome to the **Timecode STT Processor**, a Python-based utility engineered to convert spoken audio files into precision-timed, word-by-word transcription logs saved directly into a structured CSV format. 

This script is specifically tuned to catch fast-paced, mumbled, or quiet vocals—making it an ideal companion pipeline for automated audio-reactive shaders, lyric videos, music visualizers, or subtitle synchronization.

---

## Layman's Manual: What Does This Script Do?

Imagine you have a recording of someone talking or singing quickly, and you want a computer to look at that audio and tell you the exact millisecond every single word starts and stops. That is precisely what this script achieves!

1. **Reads Your Audio:** It points to your designated audio recording file on your computer.
2. **Cleans & Prepares It:** If the audio is recorded in stereo (two separate channels), it flattens it down to mono and standardizes its sample rate so the artificial intelligence can process it cleanly.
3. **Listens with AI:** It utilizes OpenAI's powerful **Whisper** speech recognition engine. We’ve custom-tuned its sensitivity settings so it doesn't accidentally skip over mumbled words, quiet beginnings, or rapid-fire speaking styles.
4. **Logs the Data:** It extracts the exact start time and duration for every individual word spoken and writes them neatly into a spreadsheet-ready `.csv` file containing three columns: `start`, `duration`, and `text`.

---

## Dependency Requirements, Creators, & Usage

To run this script successfully, you need Python installed along with a few external libraries. Below is the breakdown of each dependency, who created them, and why they are essential to this specific pipeline:

### 1. `openai-whisper`
* **Creator:** OpenAI (released as open-source in 2022).
* **What it is:** A general-purpose speech recognition model trained on a massive dataset of diverse audio capable of multilingual speech recognition and translation.
* **Why it is used here:** It serves as the core intelligence of the script. The code invokes `model.transcribe()` with specialized flags (`word_timestamps=True`, `no_speech_threshold=0.3`, `temperature=0.0`) to force Whisper to break output down into individual words and catch low-volume or rapid speech that standard tools drop.

### 2. `soundfile`
* **Creator:** Bastian Bechtold (built as a Python wrapper around the `libsndfile` C library, originally created by Erik de Castro Lopo).
* **What it is:** A fast, reliable library for reading and writing sound files natively.
* **Why it is used here:** Handled via the custom `load_audio_direct` function, `soundfile` allows the script to read raw audio data straight from disk efficiently without heavy auxiliary codecs.

### 3. `numpy`
* **Creator:** Travis Oliphant (originally created in 2005 by building upon older libraries like Numeric and Numarray).
* **What it is:** The fundamental package for scientific computing and array manipulation in Python, supporting large multi-dimensional matrices and mathematical functions.
* **Why it is used here:** Used to manipulate the raw audio waveforms loaded by `soundfile`. Specifically, it handles stereo-to-mono downmixing (`np.mean`) and linear interpolation (`np.interp`) to resample audio data to match the strict $16\text{kHz}$ input format expected by Whisper.

### 4. `os` & `csv` (Python Standard Libraries)
* **Creator:** Python Core Development Team.
* **What it is:** Built-in Python modules for interacting with operating system file paths and parsing/writing Comma-Separated Values files.
* **Why it is used here:** `os` verifies if your input audio paths exist, while `csv` handles the creation and sequential row-appending of your word-timing logs.

---

## 🚀 Getting Started & Installation Instructions

Follow these step-by-step instructions to get the script running on your machine, even if you are new to Python.

### Prerequisites
* Ensure you have **Python 3.8+** installed on your system.
* You will also need **FFmpeg** installed and added to your system path, as OpenAI's Whisper relies on it to process audio files.

### Step 1: Install Required Dependencies
Open your terminal or command prompt and install the necessary Python libraries using `pip`:
```bash
pip install openai-whisper soundfile numpy
```

### Step 2: Configure Your File Paths
Open `timecode-STT.v2.py` in any text editor and update the configuration variables at the top of the file to point to your actual local file locations:
```python
# Configuration Paths
AUDIO_PATH = r"C:\Your\Path\To\Audio-2-STT.wav"
CSV_PATH = r"C:\Your\Path\To\Save\Audio_Transcription.csv"
```

### Step 3: Run the Script
Execute the script from your terminal:
```bash
python timecode-STT.v2.py
```

---

## Advanced Parameter Tuning Reference

If you want to experiment with performance or accuracy, look inside the `transcribe_and_update_csv` function:

* **`model_size`**: Defaults to `"small"`. You can change this to `"tiny"`, `"base"`, `"medium"`, or `"large"` depending on your hardware capabilities and accuracy needs.
* **`no_speech_threshold=0.3`**: Lowered from the default to ensure quieter or mumbled vocal starts are captured instead of filtered out as silence.
* **`compression_ratio_threshold=2.6`**: Prevents the algorithm from falsely discarding fast, repeating phrasing blocks.
* **`duration` floor (`max(end_time - start_time, 0.35)`)**: Ensures ultra-fast words hold a minimum duration threshold of $0.35$ seconds, preventing visual glitches if mapped directly to shader animations.
