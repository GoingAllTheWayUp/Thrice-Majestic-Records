#!/usr/bin/env python3
# ============================================================
# VOCAL LEVELER — UNIFIED ADAPTIVE ANALYZER v7.0
# High-performance streaming & downsampled vocal analyzer
# ============================================================

import os
import csv
import math
import time
import numpy as np
import soundfile as sf
import pyloudnorm as pyln
from scipy.signal import resample_poly

# ------------------------------------------------------------
# USER SETTINGS (TUNE TO TASTE)
# ------------------------------------------------------------
WAV_INPUT_PATH   = r"X:/AudioProject/Vocal/Stem/_Vocal.STEM_[B].wav"
CSV_OUTPUT_PATH  = WAV_INPUT_PATH + "-v7.0-ANALYSIS.csv"

TARGET_SR        = 48000    # Analysis sample rate (Fast Mode downsampling)
STEP_MS          = 10.0     # Hop size / envelope point spacing (ms)
RMS_WINDOW_MS    = 50.0     # Centered RMS window (ms)
M_LUFS_WINDOW_MS = 400.0    # Centered Momentary LUFS window (ms)
ST_LUFS_WINDOW_MS= 3000.0   # Centered Short-Term LUFS window (ms)

TARGET_LUFS      = -18.0    # Target loudness ceiling
MAX_BOOST_DB     = +6.0     # Maximum upward gain ceiling
MAX_CUT_DB       = -6.0     # Maximum downward gain ceiling

SILENCE_RMS_DB   = -50.0    # Below this: zero boost, allow cuts
BREATH_RMS_DB    = -40.0    # Between silence & breath: heavy attenuation of boost

CF_TARGET_DB     = 12.0     # Desired crest factor threshold
CF_HARD_DB       = 24.0     # Crest factor limit for max downward cut
CF_BOOST_LOW_DB  = 10.0     # Full upward boost allowed below this
CF_BOOST_HIGH_DB = 18.0     # Upward boost smoothly suppressed above this

SMOOTHING_ALPHA  = 0.3      # One-pole IIR musical glide smoothing (0 = none, 1 = max)
EPSILON          = 1e-12

# ------------------------------------------------------------
# HELPERS
# ------------------------------------------------------------
def dbfs(x):
    return 20.0 * math.log10(max(x, EPSILON))

def clamp(x, lo, hi):
    return max(lo, min(hi, x))

def linear_map(x, x0, x1, y0, y1):
    if x1 == x0:
        return y0
    t = (x - x0) / (x1 - x0)
    return y0 + t * (y1 - y0)

def window_indices(center_s, win_s, sr, n_samples):
    half = win_s * 0.5
    start_s = max(0.0, center_s - half)
    end_s   = min(center_s + half, n_samples / sr)
    s0 = int(round(start_s * sr))
    s1 = int(round(end_s   * sr))
    if s1 <= s0:
        s1 = min(s0 + 1, n_samples)
    return s0, s1

def safe_lufs(meter, audio_seg):
    if len(audio_seg) < meter.block_size:
        return -150.0
    try:
        return float(meter.integrated_loudness(audio_seg))
    except Exception:
        return -150.0

# ------------------------------------------------------------
# MAIN ANALYSIS PIPELINE
# ------------------------------------------------------------
def analyze_vocal():
    print("==================================================")
    print(" VOCAL LEVELER — UNIFIED ADAPTIVE ANALYZER v7.0")
    print("==================================================")
    
    if not os.path.exists(WAV_INPUT_PATH):
        print(f"ERROR: Input file not found -> {WAV_INPUT_PATH}")
        return

    info = sf.info(WAV_INPUT_PATH)
    orig_sr = info.samplerate
    n_samples_orig = info.frames
    duration_s = info.duration

    print(f"Loading WAV: {os.path.basename(WAV_INPUT_PATH)}")
    print(f"  Original SR: {orig_sr} Hz | Duration: {duration_s:.2f}s | Frames: {n_samples_orig}")

    # Streaming load into memory safely in 1s chunks
    t_load = time.time()
    audio = np.zeros(n_samples_orig, dtype=np.float32)
    block_size = int(orig_sr * 1.0)
    write_pos = 0

    with sf.SoundFile(WAV_INPUT_PATH) as f:
        chunk_idx = 0
        total_chunks = math.ceil(n_samples_orig / block_size)
        while write_pos < n_samples_orig:
            chunk_idx += 1
            block = f.read(block_size, dtype='float32')
            if len(block) == 0:
                break
            if block.ndim > 1:
                block = np.mean(block, axis=1) # Mono sum
            end_pos = write_pos + len(block)
            audio[write_pos:end_pos] = block
            write_pos = end_pos
            print(f"  [Chunk {chunk_idx}/{total_chunks}] Loaded {write_pos}/{n_samples_orig} samples ({(write_pos/n_samples_orig)*100:.1f}%)")

    print(f"  WAV fully streamed in {time.time() - t_load:.2f}s")

    # Polyphase Downsampling (Fast Mode)
    print(f"Downsampling to {TARGET_SR} Hz analysis rate...")
    t_ds = time.time()
    audio_ds = resample_poly(audio, TARGET_SR, orig_sr)
    sr = TARGET_SR
    n_samples = len(audio_ds)
    length_s = n_samples / sr
    print(f"  Downsample complete in {time.time() - t_ds:.2f}s | New frames: {n_samples}")

    meter = pyln.Meter(sr)
    step_s = STEP_MS * 0.001
    rms_win_s = RMS_WINDOW_MS * 0.001
    m_win_s   = M_LUFS_WINDOW_MS * 0.001
    st_win_s  = ST_LUFS_WINDOW_MS * 0.001

    rows = []
    integrated_buffer = []
    prev_gain_db = 0.0

    t = 0.0
    frame_index = 0
    total_frames = int(length_s / step_s)
    t_start_analysis = time.time()

    print("Starting windowed adaptive analysis...")
    while t < length_s:
        frame_index += 1
        if frame_index % 300 == 0:
            elapsed = time.time() - t_start_analysis
            fps = frame_index / elapsed if elapsed > 0 else 1.0
            eta = (total_frames - frame_index) / fps
            print(f"  Frame {frame_index}/{total_frames} ({(frame_index/total_frames)*100:.1f}%) | FPS: {fps:.1f} | ETA: {eta/60:.1f} min")

        # Get window boundaries
        s0_rms, s1_rms = window_indices(t, rms_win_s, sr, n_samples)
        s0_m,   s1_m   = window_indices(t, m_win_s,   sr, n_samples)
        s0_st,  s1_st  = window_indices(t, st_win_s,  sr, n_samples)

        # RMS & Peak calculation
        seg_rms = audio_ds[s0_rms:s1_rms]
        rms_val = float(np.sqrt(np.mean(seg_rms**2) + EPSILON))
        peak_val = float(np.max(np.abs(seg_rms)) + EPSILON)

        rms_db = dbfs(rms_val)
        peak_db = dbfs(peak_val)
        cf_db = peak_db - rms_db

        # LUFS measurements
        m_lufs  = safe_lufs(meter, audio_ds[s0_m:s1_m])
        if m_lufs <= -149.0: m_lufs = rms_db
        
        st_lufs = safe_lufs(meter, audio_ds[s0_st:s1_st])
        if st_lufs <= -149.0: st_lufs = m_lufs

        # Running integrated LUFS buffer accumulation
        integrated_buffer.extend(seg_rms.tolist())
        try:
            int_lufs = float(meter.integrated_loudness(np.array(integrated_buffer)))
        except Exception:
            int_lufs = m_lufs

        # ====================================================
        # ADAPTIVE GAIN COMPUTATION ENGINE
        # ====================================================
        # 1. Base upward boost from momentary LUFS difference
        loudness_diff = TARGET_LUFS - m_lufs
        base_boost = clamp(loudness_diff, 0.0, MAX_BOOST_DB)

        # 2. Base downward cut from crest factor (transient protection)
        if cf_db <= CF_TARGET_DB:
            base_cut = 0.0
        elif cf_db >= CF_HARD_DB:
            base_cut = abs(MAX_CUT_DB)
        else:
            base_cut = linear_map(cf_db, CF_TARGET_DB, CF_HARD_DB, 0.0, abs(MAX_CUT_DB))

        # 3. Adaptive boost reduction on highly transient frames
        if cf_db <= CF_BOOST_LOW_DB:
            boost_factor = 1.0
        elif cf_db >= CF_BOOST_HIGH_DB:
            boost_factor = 0.0
        else:
            boost_factor = linear_map(cf_db, CF_BOOST_LOW_DB, CF_BOOST_HIGH_DB, 1.0, 0.0)

        adaptive_max_boost = MAX_BOOST_DB * boost_factor
        boost_db = clamp(base_boost, 0.0, adaptive_max_boost)

        # 4. Gating (Silence & Breath protection)
        if rms_db < SILENCE_RMS_DB:
            boost_db = 0.0
        elif rms_db < BREATH_RMS_DB:
            boost_db *= 0.25

        # 5. Combine and Clamp Gain
        gain_raw = clamp(boost_db - base_cut, MAX_CUT_DB, MAX_BOOST_DB)

        # 6. One-pole IIR Smoothing (Musical Glide)
        gain_db = (1.0 - SMOOTHING_ALPHA) * gain_raw + SMOOTHING_ALPHA * prev_gain_db
        prev_gain_db = gain_db

        rows.append([
            f"{t:.6f}", f"{t:.6f}", str(s0_rms), str(s1_rms),
            f"{rms_db:.3f}", f"{peak_db:.3f}", f"{m_lufs:.3f}",
            f"{st_lufs:.3f}", f"{int_lufs:.3f}", f"{gain_db:.3f}", f"{cf_db:.3f}"
        ])

        t += step_s

    # Write CSV Output
    os.makedirs(os.path.dirname(CSV_OUTPUT_PATH), exist_ok=True)
    print(f"Writing CSV export -> {CSV_OUTPUT_PATH}")

    with open(CSV_OUTPUT_PATH, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            "project_time", "local_time", "sample_start", "sample_end",
            "RMS_dBFS", "Peak_dBFS", "M_LUFS", "ST_LUFS", "Int_LUFS",
            "Gain_dB", "CrestFactor_dB"
        ])
        w.writerow(["t_proj", "t_loc", "s_start", "s_end", "r", "p", "m", "st", "i", "g", "cf"])
        for row in rows:
            w.writerow(row)

    print("==================================================")
    print(f" ANALYSIS COMPLETE — Wrote {len(rows)} frames")
    print(f" Total execution time: {time.time() - t_load:.2f} seconds")
    print("==================================================")

if __name__ == "__main__":
    analyze_vocal()