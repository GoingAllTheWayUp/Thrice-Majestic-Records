import soundfile as sf
import numpy as np
import pyloudnorm as pyln
import csv
import os

# ============================================================
# USER SETTINGS
# ============================================================

WAV_A = r"X:\ProjectsFolder\Session\projectNAME\ReaperProject_stem_TrackName_Left-001.wav"
WAV_B = r"X:\ProjectsFolder\Session\projectNAME\ReaperProject_stem_TrackName_Right-001.wav.csv"

CSV_A = r"X:\ProjectsFolder\Session\projectNAME\ReaperProject_stem_TrackName_Left-001.wav.csv"
CSV_B = r"X:\ProjectsFolder\Session\projectNAME\ReaperProject_stem_TrackName_Right-001.wav.csv"

STEP_MS           = 20
RMS_WINDOW_MS     = 50
M_LUFS_WINDOW_MS  = 400
ST_LUFS_WINDOW_MS = 3000

# ============================================================
# HELPERS
# ============================================================

def lin2db(x):
    if x <= 0:
        return -150.0
    return 20 * np.log10(x)

def window_energy(samples):
    if len(samples) == 0:
        return 0.0, 0.0
    peak = np.max(np.abs(samples))
    rms = np.sqrt(np.mean(samples**2))
    return rms, peak

def safe_lufs(meter, samples):
    """Return LUFS or -150 if pyloudnorm rejects the buffer."""
    try:
        if len(samples) < meter.block_size:
            return -150.0
        return meter.integrated_loudness(samples)
    except:
        return -150.0

# ============================================================
# ANALYZE ONE TRACK
# ============================================================

def analyze_track(wav_path, csv_path):
    print(f"\nLoading WAV: {wav_path}")

    audio, sr = sf.read(wav_path)
    if audio.ndim > 1:
        audio = np.mean(audio, axis=1)

    length_sec = len(audio) / sr
    print(f"  Sample rate: {sr}")
    print(f"  Length: {length_sec:.3f} sec")

    meter = pyln.Meter(sr)

    print("  Computing integrated LUFS...")
    integrated_lufs = safe_lufs(meter, audio)

    step_s    = STEP_MS / 1000.0
    rms_win_s = RMS_WINDOW_MS / 1000.0
    m_win_s   = M_LUFS_WINDOW_MS / 1000.0
    st_win_s  = ST_LUFS_WINDOW_MS / 1000.0

    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    csv_file = open(csv_path, "w", newline="")
    writer = csv.writer(csv_file)

    writer.writerow([
        "project_time","local_time","sample_start","sample_end",
        "RMS","Peak","M_LUFS","ST_LUFS","Int_LUFS"
    ])
    writer.writerow(["t_proj","t_loc","s_start","s_end","r","p","m","st","i"])

    print("  Analyzing windows...")
    line_count = 0
    t = 0.0

    while t < length_sec:
        s_start = int(t * sr)

        # RMS window
        s_end_rms = int((t + rms_win_s) * sr)
        rms_samples = audio[s_start:s_end_rms]
        rms_val, peak_val = window_energy(rms_samples)
        rms_db = lin2db(rms_val)

        # Momentary LUFS
        s_end_m = int((t + m_win_s) * sr)
        m_samples = audio[s_start:s_end_m]
        m_lufs = safe_lufs(meter, m_samples)

        # Short-term LUFS
        s_end_st = int((t + st_win_s) * sr)
        st_samples = audio[s_start:s_end_st]
        st_lufs = safe_lufs(meter, st_samples)

        writer.writerow([
            t, t, s_start, s_end_rms,
            rms_db, peak_val, m_lufs, st_lufs, integrated_lufs
        ])

        line_count += 1
        t += step_s

    csv_file.close()

    print(f"  Done. Wrote {line_count} lines → {csv_path}")
    return line_count

# ============================================================
# RUN
# ============================================================

print("======================================")
print(" PYTHON ANALYZER v1.3")
print("======================================")
print(f"STEP={STEP_MS}ms  RMS={RMS_WINDOW_MS}ms  M={M_LUFS_WINDOW_MS}ms  ST={ST_LUFS_WINDOW_MS}ms")

linesA = analyze_track(WAV_A, CSV_A)
linesB = analyze_track(WAV_B, CSV_B)

print("\n======================================")
print(" ANALYSIS COMPLETE")
print(f" Track A CSV: {CSV_A} ({linesA} lines)")
print(f" Track B CSV: {CSV_B} ({linesB} lines)")
print("======================================\n")
