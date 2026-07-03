# SplashBurst – Audio-Driven Splash Designer  
<sub>JSFX • Envelope + Noise Layer for drip→splash FX</sub>

---

<div align="center">
  <h3>SplashBurst</h3>
  <p>
    Audio-driven splash effect using transient shaping, high-frequency emphasis,<br>
    and an envelope-controlled reverb + noise layer.<br>
    Designed to turn short “drip” clips into convincing splash bursts.
  </p>
</div>

---

## I/O

<ul>
  <li><b>Inputs:</b> Left, Right (dry drip / source audio)</li>
  <li><b>Outputs:</b> Left, Right (splash-processed signal)</li>
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
      <td><b>Attack boost</b> (slider1)</td>
      <td>0–12 dB</td>
      <td>6</td>
      <td>
        Increases transient attack of the source clip to make the initial impact
        of the splash more pronounced.
      </td>
    </tr>
    <tr>
      <td><b>Sustain cut</b> (slider2)</td>
      <td>0–24 dB</td>
      <td>12</td>
      <td>
        Reduces sustain after the transient, tightening the body of the sound so
        the splash tail dominates.
      </td>
    </tr>
    <tr>
      <td><b>HF emphasis</b> (slider3)</td>
      <td>0–12 dB</td>
      <td>6</td>
      <td>
        High-frequency boost above ~4 kHz to create the bright, noisy “spray”
        character of the splash.
      </td>
    </tr>
    <tr>
      <td><b>Noise burst level</b> (slider4)</td>
      <td>-inf–0 dB</td>
      <td>-12</td>
      <td>
        Level of the synthesized high-frequency noise burst layered under the
        drip to simulate droplets and spray.
      </td>
    </tr>
    <tr>
      <td><b>Splash tail length</b> (slider5)</td>
      <td>5–200 ms</td>
      <td>60</td>
      <td>
        Duration of the splash tail envelope; controls how quickly the reverb
        and noise decay after the transient.
      </td>
    </tr>
    <tr>
      <td><b>Wet mix</b> (slider6)</td>
      <td>0–100 %</td>
      <td>50</td>
      <td>
        Blend between dry source and splash-processed signal. Higher values
        emphasize the synthetic splash tail.
      </td>
    </tr>
    <tr>
      <td><b>Envelope mode</b> (slider7)</td>
      <td>0–1 {Static, Audio-driven}</td>
      <td>1</td>
      <td>
        <b>0 = Static:</b> splash tail uses fixed slider values.<br>
        <b>1 = Audio-driven:</b> splash tail and noise burst follow the input
        amplitude envelope for more natural drip→splash behavior.
      </td>
    </tr>
  </tbody>
</table>

---

## Behavior

<ul>
  <li>
    <b>Transient shaping:</b> Attack boost + sustain cut emphasize the initial
    impact and suppress the body of the sound.
  </li>
  <li>
    <b>High-frequency spray:</b> HF emphasis and a short noise burst layer
    create the bright, chaotic splash character.
  </li>
  <li>
    <b>Tail envelope:</b> Splash tail length shapes a fast-decaying reverb-like
    response suitable for very short clips.
  </li>
  <li>
    <b>Audio-driven mode:</b> When Envelope mode is enabled, the plugin derives
    its splash intensity and tail from the input’s amplitude, making short
    drips naturally bloom into splashes.
  </li>
</ul>
