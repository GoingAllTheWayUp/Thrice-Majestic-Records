# SplashGrain v3 – Real‑Time Granular Splash  
<sub>JSFX • Short‑clip splash synthesis using micro‑grains + envelope shaping</sub>

---

<div align="center">
  <h3>SplashGrain v3</h3>
  <p>
    Real‑time granular splash generator designed for <b>very short drip clips</b>.<br>
    Uses micro‑grain windows, pitch chaos, and optional audio‑driven envelopes<br>
    to transform transient droplets into bright, chaotic splash bursts.
  </p>
</div>

---

## I/O

<ul>
  <li><b>Inputs:</b> Left, Right (dry drip / source audio)</li>
  <li><b>Outputs:</b> Left, Right (granular splash signal)</li>
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
      <td><b>Grain Size</b> (slider1)</td>
      <td>2–30 ms</td>
      <td>8</td>
      <td>
        Length of each micro‑grain window. Smaller values produce fine spray;<br>
        larger values create chunkier, more tonal splashes.
      </td>
    </tr>
    <tr>
      <td><b>Pitch Chaos</b> (slider2)</td>
      <td>0–100 %</td>
      <td>50</td>
      <td>
        Random pitch offset applied per grain. Higher values increase<br>
        chaotic, watery splash behavior.
      </td>
    </tr>
    <tr>
      <td><b>Mix</b> (slider3)</td>
      <td>0–100 %</td>
      <td>50</td>
      <td>
        Blend between dry input and granular splash output.
      </td>
    </tr>
    <tr>
      <td><b>Envelope Mode</b> (slider4)</td>
      <td>0–1 {Manual, Audio‑driven}</td>
      <td>1</td>
      <td>
        <b>0 = Manual:</b> splash intensity follows slider values.<br>
        <b>1 = Audio‑driven:</b> splash follows input amplitude, making<br>
        short drips naturally bloom into splash bursts.
      </td>
    </tr>
  </tbody>
</table>

---

## Behavior

<ul>
  <li>
    <b>Micro‑grain engine:</b> Each grain is taken directly from the current
    audio sample, ensuring correct behavior even on extremely short clips.
  </li>
  <li>
    <b>Pitch chaos:</b> Randomized per‑grain pitch offsets create the bright,
    chaotic “spray” characteristic of water splashes.
  </li>
  <li>
    <b>Window shaping:</b> A triangular grain window softens edges and prevents
    harsh artifacts.
  </li>
  <li>
    <b>Envelope shaping:</b> In audio‑driven mode, splash intensity follows the
    transient of the drip, producing natural bloom and decay.
  </li>
  <li>
    <b>Short‑clip optimized:</b> No delay lines or circular buffers — the
    algorithm works directly on the incoming signal, avoiding muffled noise
    when the source is only a few milliseconds long.
  </li>
</ul>

---

## Suggested Settings

<ul>
  <li><b>Grain Size:</b> 6–12 ms</li>
  <li><b>Pitch Chaos:</b> 40–70 %</li>
  <li><b>Mix:</b> 40–60 %</li>
  <li><b>Envelope Mode:</b> Audio‑driven (1)</li>
</ul>

<p>
These values produce a bright, splashy burst ideal for transforming short
drip recordings into expressive water‑like impacts.
</p>
