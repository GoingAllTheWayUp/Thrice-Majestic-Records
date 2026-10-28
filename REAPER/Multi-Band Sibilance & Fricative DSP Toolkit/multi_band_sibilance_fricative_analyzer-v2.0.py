#!/usr/bin/env python3
# ============================================================
# VOCAL LEVELER — MULTI-BAND SIBILANCE ANALYZER v2.0
# Includes Built-in Stem Telemetry Quantifier & Audit Report
# ============================================================

import os
import csv
import math
import time
import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfilt, resample_poly

# ------------------------------------------------------------
# USER SETTINGS
# ------------------------------------------------------------
WAV_INPUT_PATH   = r"X:\Music\Project\Vocal\Sibilance\_STEM_Track - [A].wav"
CSV_OUTPUT_PATH  = WAV_INPUT_PATH.replace(".wav", "-SIBILANCE-v2.0-ANALYSIS.csv")

TARGET_SR        = 48000    # Downsample rate for analysis speed
STEP_MS          = 10.0     # Hop size (ms)
RMS_WINDOW_MS    = 30.0     # Fast RMS window tailored for short consonant bursts (ms)

# Target threshold per band (dBFS) - Calibrated from audit data discovered on stem
# [DISCOVERED QUANTIFIER METRICS REF (Active Consonants > -90dBFS)]:
# - B1 (1.5k-2.5k Fricative F): Median ~-58.2 dB, 99th % ~-37.7 dB, Peak ~-29.8 dB
# - B2 (2.5k-4.5k Bite TPK)    : Median ~-56.4 dB, 99th % ~-32.4 dB, Peak ~-26.5 dB
# - B3 (4.5k-7k Sibil SZ)      : Median ~-56.1 dB, 99th % ~-32.4 dB, Peak ~-28.8 dB
# - B4 (7k-10k Sh Wide)        : Median ~-56.1 dB, 99th % ~-32.3 dB, Peak ~-29.3 dB
# - B5 (10k-14k High Sizzle)   : Median ~-56.5 dB, 99th % ~-36.7 dB, Peak ~-30.9 dB
# - B6 (14k-20k Air Glare)     : Median ~-59.9 dB, 99th % ~-44.0 dB, Peak ~-34.3 dB
TARGET_BAND_DB   = -34.0    
MAX_BOOST_DB     = +0.0     # Taming only
MAX_CUT_DB       = -12.0    # Absolute floor for attenuation

SMOOTHING_ALPHA  = 0.25     # One-pole IIR smoothing
EPSILON          = 1e-12

BANDS = [
    {"name": "B1_Fricative_F", "low": 1500,  "high": 2500},
    {"name": "B2_Bite_TPK",    "low": 2500,  "high": 4500},
    {"name": "B3_Sibil_SZ",    "low": 4500,  "high": 7000},
    {"name": "B4_Sh_Wide",     "low": 7000,  "high": 10000},
    {"name": "B5_High_Sizzle", "low": 10000, "high": 14000},
    {"name": "B6_Air_Glare",   "low": 14000, "high": 20000}
]

def dbfs(x):
    return 20.0 * math.log10(max(x, EPSILON))

def clamp(x, lo, hi):
    return max(lo, min(hi, x))

def design_bandpass_filter(low_hz, high_hz, sr, order=4):
    nyq = 0.5 * sr
    high_hz_clamped = min(high_hz, nyq - 100.0)
    low_hz_clamped = max(low_hz, 10.0)
    if high_hz_clamped <= low_hz_clamped:
        sos = butter(order, low_hz_clamped / nyq, btype='highpass', output='sos')
    else:
        sos = butter(order, [low_hz_clamped / nyq, high_hz_clamped / nyq], btype='bandpass', output='sos')
    return sos

def analyze_sibilance_stem():
    script_start_time = time.time()
    
    print("==================================================")
    print(" VOCAL LEVELER — MULTI-BAND SIBILANCE ANALYZER v2.0")
    print("==================================================")
    
    if not os.path.exists(WAV_INPUT_PATH):
        print(f"ERROR: Input file not found -> {WAV_INPUT_PATH}")
        return

    target_csv = os.path.normpath(CSV_OUTPUT_PATH)
    target_dir = os.path.dirname(target_csv)
    if target_dir and not os.path.exists(target_dir):
        os.makedirs(target_dir, exist_ok=True)

    print(f"Initializing Multi-Band CSV output -> {target_csv}")
    
    headers_human = ["project_time", "local_time", "sample_start", "sample_end", "Full_RMS_dBFS"]
    headers_machine = ["t_proj", "t_loc", "s_start", "s_end", "rms_full"]
    
    for b in BANDS:
        headers_human.extend([f"{b['name']}_RMS_dBFS", f"{b['name']}_Gain_dB"])
        headers_machine.extend([f"{b['name']}_r", f"{b['name']}_g"])

    try:
        with open(target_csv, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(headers_human)
            w.writerow(headers_machine)
    except Exception as e:
        print(f"CRITICAL ERROR: Could not create CSV file: {e}")
        return

    info = sf.info(WAV_INPUT_PATH)
    orig_sr = info.samplerate
    n_samples_orig = info.frames
    duration_s = info.duration

    print(f"Loading WAV: {os.path.basename(WAV_INPUT_PATH)}")
    print(f"  Original SR: {orig_sr} Hz | Duration: {duration_s:.2f}s | Frames: {n_samples_orig}")

    t_load = time.time()
    audio, _ = sf.read(WAV_INPUT_PATH, dtype='float32')
    if audio.ndim > 1:
        audio = np.mean(audio, axis=1)

    if orig_sr != TARGET_SR:
        print(f"Downsampling to {TARGET_SR} Hz analysis rate...")
        audio_ds = resample_poly(audio, TARGET_SR, orig_sr)
        sr = TARGET_SR
    else:
        audio_ds = audio
        sr = orig_sr

    n_samples = len(audio_ds)
    length_s = n_samples / sr

    print("Designing 6-Band Butterworth Filter Bank...")
    filter_soses = []
    filtered_bands_audio = []
    
    for b in BANDS:
        sos = design_bandpass_filter(b['low'], b['high'], sr)
        filter_soses.append(sos)
        band_audio = sosfilt(sos, audio_ds)
        filtered_bands_audio.append(band_audio)

    step_s = STEP_MS * 0.001
    rms_win_s = RMS_WINDOW_MS * 0.001
    half_win_s = rms_win_s * 0.5

    rows = []
    prev_band_gains = [0.0] * len(BANDS)
    band_raw_rms_values = {b['name']: [] for b in BANDS}

    t = 0.0
    frame_index = 0
    total_frames = int(length_s / step_s)
    t_start_analysis = time.time()

    print("Executing 6-band frame analysis & telemetry extraction...")
    while t < length_s:
        frame_index += 1
        if frame_index % 1000 == 0:
            print(f"  Progress: {(frame_index/total_frames)*100:.1f}%")

        start_s = max(0.0, t - half_win_s)
        end_s   = min(t + half_win_s, length_s)
        s0 = int(round(start_s * sr))
        s1 = int(round(end_s * sr))
        if s1 <= s0: s1 = min(s0 + 1, n_samples)

        seg_full = audio_ds[s0:s1]
        rms_full_val = float(np.sqrt(np.mean(seg_full**2) + EPSILON))
        rms_full_db = dbfs(rms_full_val)

        row = [f"{t:.6f}", f"{t:.6f}", str(s0), str(s1), f"{rms_full_db:.3f}"]

        for b_idx, b in enumerate(BANDS):
            seg_band = filtered_bands_audio[b_idx][s0:s1]
            rms_band_val = float(np.sqrt(np.mean(seg_band**2) + EPSILON))
            rms_band_db = dbfs(rms_band_val)

            band_raw_rms_values[b['name']].append(rms_band_db)

            diff = TARGET_BAND_DB - rms_band_db
            gain_raw = clamp(diff, MAX_CUT_DB, MAX_BOOST_DB)

            gain_db = (1.0 - SMOOTHING_ALPHA) * gain_raw + SMOOTHING_ALPHA * prev_band_gains[b_idx]
            prev_band_gains[b_idx] = gain_db

            row.extend([f"{rms_band_db:.3f}", f"{gain_db:.3f}"])

        rows.append(row)
        t += step_s

    print(f"Writing data rows to CSV -> {target_csv}")
    with open(target_csv, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        for r in rows:
            w.writerow(r)

    # Built-in Stem Quantifier Audit Report
    print("\n==================================================")
    print(" STEM TELEMETRY QUANTIFIER & AUDIT REPORT")
    print("==================================================")
    for b in BANDS:
        vals = np.array(band_raw_rms_values[b['name']])
        active_vals = vals[vals > -90.0] # Filter silence
        if len(active_vals) > 0:
            med = np.median(active_vals)
            p99 = np.percentile(active_vals, 99)
            pk = np.max(active_vals)
            print(f" [{b['name']}] ({b['low']}Hz-{b['high']}Hz)")
            print(f"   Active Median: {med:.2f} dB | 99th %: {p99:.2f} dB | Peak: {pk:.2f} dB")
        else:
            print(f" [{b['name']}]: No active frames detected.")
    print("==================================================")
    print(f" ANALYSIS COMPLETE | Total Time: {time.time() - script_start_time:.2f}s")
    print("==================================================\n")

if __name__ == "__main__":
    analyze_sibilance_stem()