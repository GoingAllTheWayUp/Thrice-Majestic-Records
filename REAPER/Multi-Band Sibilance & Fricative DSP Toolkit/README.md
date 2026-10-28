# Multi-Band Sibilance & Fricative DSP Toolkit

A specialized, decoupled 2-part Python toolkit (`multi_band_sibilance_fricative_analyzer` and `multi_band_sibilance_renderer`) engineered specifically for **isolated sibilance and consonant vocal stems**. 

Unlike conventional full-vocal de-essers, this pipeline is designed for stems containing **no main vocal body or sub-bass**, operating exclusively across a contiguous 6-band filter bank from $1.5\text{ kHz}$ to $20.0\text{ kHz}$. It performs offline multi-band energy extraction, logs high-resolution CSV telemetry with built-in statistical stem quantification, and applies phase-coherent, sample-accurate attenuation post-analysis.

---

## 🛠️ Architecture Overview

The toolkit utilizes an offline, two-stage decoupled processing paradigm:

```
                  +-----------------------------------+
                  |  Isolated Sibilance/Consonant WAV  |
                  +-----------------------------------+
                                    |
                                    v
            +-----------------------------------------------+
            |  multi_band_sibilance_fricative_analyzer.py   |
            |   - 6-Band Butterworth SOS Filter Bank        |
            |   - Frame-by-Frame RMS Telemetry Extraction   |
            |   - Built-in Stem Quantifier & Audit Report   |
            +-----------------------------------------------+
                                    |
                                    v
                  +-----------------------------------+
                  |   Multi-Band Telemetry CSV Log    |
                  +-----------------------------------+
                                    |
                                    v
            +-----------------------------------------------+
            |    multi_band_sibilance_renderer.py           |
            |   - CSV Telemetry Parsing & Band Overrides    |
            |   - Sample-Accurate Gain Curve Interpolation  |
            |   - Band Reconstruction & Peak Safety Ceiling |
            +-----------------------------------------------+
                                    |
                                    v
                  +-----------------------------------+
                  |   Pruned, Tamed Sibilance Stem WAV|
                  +-----------------------------------+
```

1. **Analyzer (`multi_band_sibilance_fricative_analyzer-v2.0.py`)**: Slices the input audio into 6 contiguous frequency bands, computes running RMS telemetry in $10\text{ ms}$ hops ($30\text{ ms}$ windows), logs required attenuation to a structured CSV, and generates an instantaneous console **Stem Quantifier & Audit Report** derived from empirical non-silent frame distribution.
2. **Renderer (`multi_band_sibilance_renderer-v2.0.py`)**: Reads the multi-band CSV log, interpolates $10\text{ ms}$ gain points sample-accurately across the full audio timeline, applies independent per-band scale multipliers and cut limits, re-sums the bands with low-frequency residual recovery, and enforces a true-peak ceiling.

---

## 📋 Dependencies

- **Python**: `3.8+`
- **NumPy**: `numpy >= 1.20.0`
- **SciPy**: `scipy >= 1.7.0` (Requires `scipy.signal` and `scipy.interpolate`)
- **PySoundFile**: `soundfile >= 0.10.0`

### Installation
```bash
pip install numpy scipy soundfile
```

---

## 🧮 Mathematical & DSP Foundations

### 1. Digital Butterworth Filter Bank (Second-Order Sections)
The core filter engine constructs contiguous bandpass filters using digital **Butterworth** topology. Butterworth filters are selected for their **maximally flat magnitude response** in the passband:

$$|H(j\omega)|^2 = \frac{1}{1 + \left(\frac{\omega}{\omega_c}\right)^{2N}}$$

Where $N$ is the filter order ($N=4$ in this implementation, yielding a $24\text{ dB/octave}$ rolloff).

To preserve numerical stability at high sample rates and tight frequency bounds, filters are converted directly into **Second-Order Sections (SOS)** matrices rather than transfer function coefficients $(b, a)$:

$$H(z) = g \cdot \prod_{k=1}^{L} \frac{b_{0k} + b_{1k}z^{-1} + b_{2k}z^{-2}}{1 + a_{1k}z^{-1} + a_{2k}z^{-2}}$$

Filtering is executed via `scipy.signal.sosfilt`, preventing floating-point degradation in narrow high-frequency bands.

### 2. Logarithmic Decibel Metrics
Signal amplitudes are evaluated in dBFS using stabilized RMS calculation across frame segments:

$$\text{RMS} = \sqrt{\frac{1}{M} \sum_{m=0}^{M-1} x[m]^2 + \epsilon}$$

$$\text{dBFS} = 20 \cdot \log_{10}\left(\max(\text{RMS}, \epsilon)\right)$$

Where $\epsilon = 10^{-12}$ prevents logarithm domain errors during silent audio intervals.

### 3. Sample-Accurate Envelope Interpolation
The renderer upsamples discrete $10\text{ ms}$ analysis gain frames $g[k]$ to match the sample rate $f_s$ of the audio stream using 1D linear interpolation (`scipy.interpolate.interp1d`):

$$g(t) = g[k] + \frac{t - t_k}{t_{k+1} - t_k} \left( g[k+1] - g[k] \right)$$

This linear gain envelope is converted back to linear scale:

$$A_{\text{lin}}(t) = 10^{\frac{g(t)}{20}}$$

And multiplied against the corresponding bandpass-filtered signal $x_b(t)$:

$$y_b(t) = x_b(t) \cdot A_{\text{lin}}(t)$$

---

## 📊 6-Band Filter Bank Architecture

The stem spectrum ($1.5\text{ kHz}$ to $20.0\text{ kHz}$) is segmented into 6 contiguous bands tailored to phonetic friction and sibilance zones:

| Band | Name | Frequency Bounds | Phonetic & Acoustic Mapping |
| :--- | :--- | :--- | :--- |
| **B1** | `B1_Fricative_F` | $1500\text{ Hz} - 2500\text{ Hz}$ | Labiodental fricatives ("F", "Th"), low mouth turbulence, breath strokes. |
| **B2** | `B2_Bite_TPK` | $2500\text{ Hz} - 4500\text{ Hz}$ | Alveolar/Velar mechanical attacks ("T", "P", "K"), tongue clicks, saliva pops. |
| **B3** | `B3_Sibil_SZ` | $4500\text{ Hz} - 7000\text{ Hz}$ | Primary sibilant whistling core ("S", "Z", "Ch", "J"). High ear-fatigue zone. |
| **B4** | `B4_Sh_Wide` | $7000\text{ Hz} - 10000\text{ Hz}$ | Postalveolar fricatives ("Sh"), wide dental edge, extended sibilant diffusion. |
| **B5** | `B5_High_Sizzle` | $10000\text{ Hz} - 14000\text{ Hz}$ | Upper consonant sizzle, metallic vocal sheen, top-end fricative bite. |
| **B6** | `B6_Air_Glare` | $14000\text{ Hz} - 20000\text{ Hz}$ | Ultra-high vocal air, digital mic glare, top-end condenser sizzle. |

---

## 📈 Stem Telemetry Quantifier & Audit Report

The analyzer embeds an automated statistical audit engine. Upon completing the 6-band extraction pass, it evaluates all active audio frames ($\text{RMS} > -90\text{ dBFS}$) and outputs empirical metrics to calibrate target threshold levels (`TARGET_BAND_DB`).

### Empirical Benchmark Data (Rap Vocal Stem Test Set)
```text
==================================================
 STEM TELEMETRY QUANTIFIER & AUDIT REPORT
==================================================
 [B1_Fricative_F] (1500Hz-2500Hz)
   Active Median: -58.21 dB | 99th %: -37.74 dB | Peak: -29.78 dB
 [B2_Bite_TPK] (2500Hz-4500Hz)
   Active Median: -56.40 dB | 99th %: -32.41 dB | Peak: -26.47 dB
 [B3_Sibil_SZ] (4500Hz-7000Hz)
   Active Median: -56.12 dB | 99th %: -32.38 dB | Peak: -28.80 dB
 [B4_Sh_Wide] (7000Hz-10000Hz)
   Active Median: -56.10 dB | 99th %: -32.30 dB | Peak: -29.31 dB
 [B5_High_Sizzle] (10000Hz-14000Hz)
   Active Median: -56.54 dB | 99th %: -36.72 dB | Peak: -30.91 dB
 [B6_Air_Glare] (14000Hz-20000Hz)
   Active Median: -59.88 dB | 99th %: -44.02 dB | Peak: -34.33 dB
==================================================
```

---

## 🚀 Execution Guide

### 1. Analysis Pass
Set your target file path in `multi_band_sibilance_fricative_analyzer-v2.0.py` and run:

```bash
python multi_band_sibilance_fricative_analyzer-v2.0.py
```
* **Input**: Isolated sibilance stem `.wav`
* **Output**: Telemetry CSV (`-SIBILANCE-v2.0-ANALYSIS.csv`) containing time markers, full RMS, per-band RMS, and calculated raw band gain values.

### 2. Render Pass
Adjust your post-analysis overrides in `multi_band_sibilance_renderer-v2.0.py`:

```python
BAND_SCALES = {
    "B1_Fricative_F": 0.6,   # Scale factor (0.0 to 1.0)
    "B2_Bite_TPK":    0.7,
    "B3_Sibil_SZ":    1.0,
    "B4_Sh_Wide":     0.8,
    "B5_High_Sizzle": 0.6,
    "B6_Air_Glare":   0.0    # Bypass air band
}

BAND_MAX_CUTS = {
    "B1_Fricative_F": -4.0,  # Max cut ceiling in dB
    "B2_Bite_TPK":    -5.0,
    "B3_Sibil_SZ":    -8.0,
    "B4_Sh_Wide":     -6.0,
    "B5_High_Sizzle": -4.0,
    "B6_Air_Glare":   0.0
}
```

Run the renderer:
```bash
python multi_band_sibilance_renderer-v2.0.py
```
* **Output**: Tamed, phase-coherent audio stem (`-SIBILANCE-RENDERED-v2.0.wav`).

---

## ⚠️ Limitations, Artifacts & Risk Mitigations

1. **Phase Smearing at Crossover Boundaries**: Splitting audio across 6 IIR filters introduces phase shifts at crossover frequency points. **Mitigation**: Bands are re-summed with an explicit low-frequency residual recovery pass below $1.5\text{ kHz}$ to preserve spectral unity.
2. **Time-Domain Pre-Ringing**: Extremely fast window sizes can cause transient smearing on sharp mouth clicks. **Mitigation**: The analyzer uses a $30\text{ ms}$ centered window with a $0.25$ one-pole IIR smoothing coefficient ($\alpha$) to prevent abrupt gain stepping.
3. **Broadband Mouth Click Masking**: Saliva pops span across multiple bands ($2.5\text{ kHz} - 10.0\text{ kHz}$). **Mitigation**: Adjust `B2_Bite_TPK` scale factors independently to tame mechanical bite without dampening the natural friction of vocal consonants.

---

## 🔮 Future Expansions

- **Dynamic Rolling Noise Floor Gating**: Automatically adjust target thresholds based on moving noise-floor estimation to prevent background room noise elevation.
- **Automated CSV Threshold Auto-Calibration**: Allow the Renderer to read the Quantifier stats directly from the CSV header to set target cuts without requiring manual threshold configuration.

---

## 📚 External References & Literature

- **Acoustic Phonetics**: Stevens, K. N. (2000). *Acoustic Phonetics*. MIT Press. (Detailed acoustic modeling of fricatives and sibilants).
- **DSP & Filter Design**: Oppenheim, A. V., & Schafer, R. W. (2009). *Discrete-Time Signal Processing* (3rd Ed.). Prentice Hall.
- **Vocal Engineering & Sibilance**: Senior, M. (2011). *Mixing Secrets for the Small Studio*. Focal Press.
- **Butterworth Filter Properties**: [SciPy Signal Butterworth Documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.butter.html)