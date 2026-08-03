#transient‑detection.v0.py

import soundfile as sf
import numpy as np
import csv

# ============================================================
# USER SETTINGS
# ============================================================

WAV_PATH = r"X:\Reaper\Project\Path\Stem-Track-000.wav"
CSV_PATH = r"X:\Blender\Project\Path\ExportedData\transient_data\Stem-Track-000_Transients.csv"

FRAME_MS = 5          # analysis hop size
WINDOW_MS = 10        # energy window
THRESH_DB = -25       # transient threshold (dB)
HYSTERESIS_DB = -35   # fall-back threshold for end of transient

MIN_GAP_MS = 40       # minimum time between kicks (avoid double triggers)

# ============================================================
# HELPERS
# ============================================================

def lin2db(x):
    if x <= 1e-12:
        return -150.0
    return 20 * np.log10(x)

def energy_db(samples):
    if len(samples) == 0:
        return -150.0
    rms = np.sqrt(np.mean(samples**2))
    return lin2db(rms)

# ============================================================
# MAIN
# ============================================================

def detect_transients(wav_path, csv_path):
    audio, sr = sf.read(wav_path)

    # mono mix if stereo
    if audio.ndim > 1:
        audio = np.mean(audio, axis=1)

    hop = int(sr * (FRAME_MS / 1000.0))
    win = int(sr * (WINDOW_MS / 1000.0))
    min_gap = int(sr * (MIN_GAP_MS / 1000.0))

    energy_curve = []
    positions = []

    # compute energy envelope
    for i in range(0, len(audio), hop):
        start = i
        end = min(i + win, len(audio))
        e = energy_db(audio[start:end])
        energy_curve.append(e)
        positions.append(start)

    # transient detection
    transients = []
    last_hit_sample = -999999

    in_transient = False
    transient_start = None

    for idx, e in enumerate(energy_curve):
        sample_pos = positions[idx]

        # start transient
        if not in_transient and e > THRESH_DB and (sample_pos - last_hit_sample) > min_gap:
            in_transient = True
            transient_start = sample_pos

        # end transient
        elif in_transient and e < HYSTERESIS_DB:
            in_transient = False
            transient_end = sample_pos

            duration_sec = (transient_end - transient_start) / sr
            timestamp_sec = transient_start / sr

            transients.append({
                "index": len(transients),
                "timestamp": timestamp_sec,
                "sample": transient_start,
                "duration": duration_sec,
                "peak": float(np.max(np.abs(audio[transient_start:transient_end])))
            })

            last_hit_sample = transient_start

    # write CSV
    with open(csv_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["index", "timestamp_sec", "sample_index", "duration_sec", "peak"])
        for t in transients:
            w.writerow([t["index"], t["timestamp"], t["sample"], t["duration"], t["peak"]])

    print(f"Detected {len(transients)} kick transients → {csv_path}")


# ============================================================
# RUN
# ============================================================

detect_transients(WAV_PATH, CSV_PATH)
