# SplashGrain v3 – Real‑Time Granular Splash for Short Audio Clips  
<sub>JSFX • Micro‑grain splash from audio with optional envelope following</sub>

---

<div align="center">
  <h3>SplashGrain v3</h3>
  <p>
    Real‑time granular splash effect for <b>short audio clips</b>.<br>
    Uses a single moving grain window, pitch randomization, and an optional<br>
    audio envelope follower to turn transient “drip” sounds into splash‑like bursts.
  </p>
</div>

---

## I/O

<ul>
  <li><b>Inputs:</b> Left, Right (source audio / drip) *Drip" created via reaPitch w/ envelope shapeing</li>
  <li><b>Outputs:</b> Left, Right (granular splash mix)</li>
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
      <td><b>Grain Size (ms)</b> (slider1)</td>
      <td>2–30 (step 1)</td>
      <td>8</td>
      <td>
        Length of the grain window in milliseconds.<br>
        Internally converted to samples as:<br>
        <code>grainlen = slider1 * srate * 0.001;</code>
      </td>
    </tr>
    <tr>
      <td><b>Pitch Chaos (%)</b> (slider2)</td>
      <td>0–100 (step 1)</td>
      <td>50</td>
      <td>
        Amount of random pitch offset per grain, expressed as a percentage.<br>
        Used as:<br>
        <code>pitch_rng = slider2 / 100;</code><br>
        and applied via:<br>
        <code>pitch = (rand(2) - 1) * pitch_rng;</code>
      </td>
    </tr>
    <tr>
      <td><b>Mix (%)</b> (slider3)</td>
      <td>0–100 (step 1)</td>
      <td>50</td>
      <td>
        Wet/dry blend between the original input and the grain‑processed signal.<br>
        Used as:<br>
        <code>mix = slider3 / 100;</code><br>
        in the output:<br>
        <code>out = in * (1 - mix) + grain * (mix * env);</code>
      </td>
    </tr>
    <tr>
      <td><b>Envelope Mode</b> (slider4)</td>
      <td>0–1 {Manual, Audio envelope}</td>
      <td>1</td>
      <td>
        <b>0 = Manual:</b> grain output is not scaled by input level.<br>
        <b>1 = Audio envelope:</b> grain output is multiplied by an absolute<br>
        input envelope:<br>
        <code>env = env_mode ? abs(in) : 1;</code>
      </td>
    </tr>
  </tbody>
</table>

---

## Processing overview

<ul>
  <li>
    <b>Grain position:</b> A sample counter (<code>grainpos</code>) advances each
    sample and resets when it reaches <code>grainlen</code>.
  </li>
  <li>
    <b>Pitch offset:</b> On each reset, a new random pitch factor is computed
    from <code>pitch_rng</code> and used to derive a fractional read position:
    <code>readpos = grainpos * (1 + pitch);</code>
  </li>
  <li>
    <b>Windowing:</b> A simple triangular window is applied per grain:
    <code>win = 1 - (grainpos / grainlen);</code> and the grain is:
    <code>grain = in * win;</code>
  </li>
  <li>
    <b>Envelope scaling:</b> When Envelope Mode = 1, the grain is scaled by
    <code>env = abs(in)</code>, tying splash intensity to input amplitude.
  </li>
  <li>
    <b>Output mix:</b> The final stereo output is:
    <code>out = in*(1-mix) + grain*(mix*env);</code> sent to
    <code>spl0</code> and <code>spl1</code>.
  </li>
</ul>
