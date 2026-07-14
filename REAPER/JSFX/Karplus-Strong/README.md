# Karplus–Strong Resonator (audio‑driven)  
<sub>JSFX • Note Step + Hz mode w/ text display</sub>

---

<div align="center">
  <h3>Karplus–Strong Resonator</h3>
  <p>
    Audio‑driven resonator using a delay‑line Karplus–Strong algorithm.<br>
    Supports <b>MIDI note</b> tuning and <b>Hz</b> tuning with on‑screen text feedback.
  </p>
</div>

---

## I/O

<ul>
  <li><b>Inputs:</b> Left, Right (audio excite / dry)</li>
  <li><b>Outputs:</b> Left, Right (resonated signal)</li>
</ul>

---

## Controls

<table>
  <thead>
    <tr>
      <th>Slider</th>
      <th>Range</th>
      <th>Default</th>
      <th>Description</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>Tuning mode</b> (slider6)</td>
      <td>0–1 {MIDI, Hz}</td>
      <td>0</td>
      <td>
        <b>0 = MIDI:</b> use <code>slider1</code> as MIDI note.<br>
        <b>1 = Hz:</b> use <code>slider7</code> as frequency in Hz.
      </td>
    </tr>
    <tr>
      <td><b>MIDI note</b> (slider1)</td>
      <td>24–96 (step 1)</td>
      <td>60</td>
      <td>Resonator pitch in MIDI notes (C1–C7 approx.).</td>
    </tr>
    <tr>
      <td><b>Frequency (Hz)</b> (slider7)</td>
      <td>20–20000 (step 1)</td>
      <td>1000</td>
      <td>Direct Hz tuning when Tuning mode = Hz.</td>
    </tr>
    <tr>
      <td><b>Damping</b> (slider2)</td>
      <td>0.5–0.999 (step 0.001)</td>
      <td>0.8</td>
      <td>Decay time of the resonator; higher = longer ring.</td>
    </tr>
    <tr>
      <td><b>Input mix</b> (slider3)</td>
      <td>0–1 (step 0.01)</td>
      <td>0.3</td>
      <td>Blend between dry input and excite signal into the resonator.</td>
    </tr>
    <tr>
      <td><b>Lowpass amount</b> (slider4)</td>
      <td>0–1 (step 0.01)</td>
      <td>0.4</td>
      <td>Lowpass filtering inside the delay line; shapes tone and decay.</td>
    </tr>
    <tr>
      <td><b>Stereo spread</b> (slider5)</td>
      <td>0–1 (step 0.01)</td>
      <td>0</td>
      <td>Offsets left/right delay to widen stereo image.</td>
    </tr>
  </tbody>
</table>

---

## Visual display (@gfx)

<div>
  <p>The JSFX draws a small status line in the graphics area:</p>
  <ul>
    <li><b>MIDI mode:</b> <code>NOTE_NAME — XX.XX Hz</code> (e.g. <code>C4 — 261.63 Hz</code>)</li>
    <li><b>Hz mode:</b> <code>Hz mode — XX.XX Hz</code></li>
  </ul>
  <p>Text is rendered at <code>(10, 10)</code> with white color.</p>
</div>

---

## Implementation notes

<ul>
  <li><b>Pitch:</b> MIDI notes converted via <code>440 * 2^((n-69)/12)</code>.</li>
  <li><b>Buffer size:</b> <code>bufsize = max(8, floor(sample_rate / freq))</code> for the delay line.</li>
  <li><b>Safety:</b> Frequency clamped to <code>&gt;= 20 Hz</code> to avoid extreme buffer sizes.</li>
  <li><b>Hz slider:</b> currently linear mapping; exponential mapping can be added later.</li>
</ul>

---
