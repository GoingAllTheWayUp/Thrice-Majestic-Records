#!/usr/bin/env python3
# ============================================================
# VOCAL LEVELER — MULTI-BAND SIBILANCE RENDERER v2.1
# Reads multi-band telemetry CSV with pre-calibrated quantifier overrides
# ============================================================

import os
import time
import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfilt
from scipy.interpolate import interp1d

# ------------------------------------------------------------
# USER SETTINGS & PER-BAND OVERRIDES
# ------------------------------------------------------------
WAV_ORIGINAL_PATH = r"X:\Music\Project\Vocal\Sibilance\_STEM_Track - [A].wav"
CSV_INPUT_PATH    = WAV_ORIGINAL_PATH.replace(".wav", "-SIBILANCE-v2.0-ANALYSIS.csv")
WAV_OUTPUT_PATH   = WAV_ORIGINAL_PATH.replace(".wav", "-SIBILANCE-RENDERED-v2.0.wav")

CEILING_DBFS      = -0.5   # Safety peak limiter ceiling

BANDS = [
    {"name": "B1_Fricative_F", "low": 1500,  "high": 2500},
    {"name": "B2_Bite_TPK",    "low": 2500,  "high": 4500},
    {"name": "B3_Sibil_SZ",    "low": 4500,  "high": 7000},
    {"name": "B4_Sh_Wide",     "low": 7000,  "high": 10000},
    {"name": "B5_High_Sizzle", "low": 10000, "high": 14000},
    {"name": "B6_Air_Glare",   "low": 14000, "high": 20000}
]

# ============================================================
# POST-ANALYSIS PER-BAND OVERRIDES (Pre-calibrated via Quantifier)
# ============================================================
BAND_SCALES = {
    "B1_Fricative_F": 0.6,   # Smooth F/Th fricatives gently
    "B2_Bite_TPK":    0.7,   # Tame sharp T/P/K clicks
    "B3_Sibil_SZ":    1.0,   # Full strength control on S/Z whistles
    "B4_Sh_Wide":     0.8,   # Controlled Sh/Ch diffusion
    "B5_High_Sizzle": 0.6,   # Soft control on top sizzle
    "B6_Air_Glare":   0.0    # 0.0 = Keep air completely untouched
}

BAND_MAX_CUTS = {
    "B1_Fricative_F": -4.0,
    "B2_Bite_TPK":    -5.0,
    "B3_Sibil_SZ":    -8.0,
    "B4_Sh_Wide":     -6.0,
    "B5_High_Sizzle": -4.0,
    "B6_Air_Glare":   0.0
}

def design_bandpass_filter(low_hz, high_hz, sr, order=4):
    nyq = 0.5 * sr
    high_hz_clamped = min(high_hz, nyq - 100.0)
    low_hz_clamped = max(low_hz, 10.0)
    if high_hz_clamped <= low_hz_clamped:
        sos = butter(order, low_hz_clamped / nyq, btype='highpass', output='sos')
    else:
        sos = butter(order, [low_hz_clamped / nyq, high_hz_clamped / nyq], btype='bandpass', output='sos')
    return sos

def render_sibilance_stem():
    t0 = time.time()
    print("==================================================")
    print(" VOCAL LEVELER — MULTI-BAND SIBILANCE RENDERER v2.0")
    print("==================================================")

    if not os.path.exists(WAV_ORIGINAL_PATH) or not os.path.exists(CSV_INPUT_PATH):
        print("ERROR: Missing original WAV or analysis CSV file.")
        return

    orig_audio, orig_sr = sf.read(WAV_ORIGINAL_PATH, dtype='float32')
    is_stereo = orig_audio.ndim > 1
    orig_mono = np.mean(orig_audio, axis=1) if is_stereo else orig_audio
    n_samples = len(orig_mono)

    times = []
    band_gains_db = {b['name']: [] for b in BANDS}

    with open(CSV_INPUT_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines[2:]:
        parts = [p.strip() for p in line.strip().split(",")]
        if len(parts) >= 5 + (len(BANDS) * 2):
            try:
                t_proj = float(parts[0])
                times.append(t_proj)
                for idx, b in enumerate(BANDS):
                    gain_col_idx = 5 + (idx * 2) + 1
                    raw_gain_db = float(parts[gain_col_idx])

                    scale = BAND_SCALES.get(b['name'], 1.0)
                    max_cut = abs(BAND_MAX_CUTS.get(b['name'], 12.0))
                    
                    final_gain_db = max(-max_cut, min(0.0, raw_gain_db * scale))
                    band_gains_db[b['name']].append(final_gain_db)
            except ValueError:
                continue

    if not times:
        print("ERROR: Failed to parse CSV control points.")
        return

    orig_times = np.arange(n_samples, dtype=np.float64) / orig_sr
    processed_bands_sum = np.zeros(n_samples, dtype=np.float32)

    print("Applying multi-band sample-accurate gain curves...")
    for b in BANDS:
        b_name = b['name']
        sos = design_bandpass_filter(b['low'], b['high'], orig_sr)
        band_audio = sosfilt(sos, orig_mono)

        gains_list = band_gains_db[b_name]
        interpolator = interp1d(times, gains_list, kind='linear', bounds_error=False, fill_value=(gains_list[0], gains_list[-1]))
        sample_gain_db = interpolator(orig_times)
        sample_gain_lin = 10.0 ** (sample_gain_db / 20.0)

        processed_bands_sum += (band_audio * sample_gain_lin)

    sos_low_residual = butter(4, 1500.0 / (0.5 * orig_sr), btype='lowpass', output='sos')
    low_residual = sosfilt(sos_low_residual, orig_mono)
    final_audio = processed_bands_sum + low_residual

    if is_stereo:
        mono_diff = final_audio - orig_mono
        final_output = orig_audio + mono_diff[:, np.newaxis]
    else:
        final_output = final_audio

    peak_val = np.max(np.abs(final_output))
    peak_dbfs = 20.0 * np.log10(max(peak_val, 1e-12))
    if peak_dbfs > CEILING_DBFS:
        allowed_peak_lin = 10.0 ** (CEILING_DBFS / 20.0)
        final_output *= (allowed_peak_lin / peak_val)

    sf.write(WAV_OUTPUT_PATH, final_output, orig_sr, subtype='PCM_24')

    print("==================================================")
    print(" RENDER COMPLETE")
    print(f" Output saved to: {WAV_OUTPUT_PATH}")
    print(f" Total time elapsed: {time.time() - t0:.2f} seconds")
    print("==================================================")

if __name__ == "__main__":
    render_sibilance_stem()