<h1>LYZER: Deterministic Dual-Mono Stereo Balancer</h1>

<p>
  LYZER is a deterministic, offline, CSV-driven audio analysis and stereo-balancing pipeline designed for REAPER.
  It analyzes two mono stems (left and right), computes loudness differences, and writes calibrated Trim Volume
  automation to maintain a stable stereo image.
</p>

<p>
  The original purpose of this project was to act as a <strong>dual-mono leveler</strong>:
  reduce whichever side is louder at each moment so the stereo image is preserved without boosting the quieter channel.
</p>

<h2>Pipeline Overview</h2>

<pre><code>[LYZER Analyzer] → CSV_A / CSV_B
        ↓
[DiffEng Difference Engine] → TrackAB_differences.csv
        ↓
[ElopeIter Envelope Writer] → Trim Volume automation in REAPER
</code></pre>

<h2>Requirements</h2>

<h3>Python Version</h3>
<p><strong>Python 3.8+</strong> (3.10–3.12 recommended)</p>

<h3>Python Dependencies</h3>

<pre><code>numpy
soundfile
pyloudnorm
</code></pre>

<p>Install with:</p>

<pre><code>pip install numpy soundfile pyloudnorm
</code></pre>

<h3>REAPER Requirements</h3>
<ul>
  <li>REAPER 6 or 7</li>
  <li>Trim Volume envelopes must be visible/enabled on both tracks</li>
  <li>Select exactly two mono tracks (A = right, B = left)</li>
</ul>

<h2>Known Limitation: Off-Center Analysis Window</h2>

<p>
  In <strong>LYZERv1.0</strong>, all analysis windows are <strong>forward-looking</strong>:
</p>

<pre><code>RMS window: [t → t + RMS_WINDOW_MS]
M_LUFS:     [t → t + M_LUFS_WINDOW_MS]
ST_LUFS:    [t → t + ST_LUFS_WINDOW_MS]
</code></pre>

<p>
  This means the measurement is <strong>not centered</strong> around the timestamp. A centered-window version can be added later.
</p>

<h2>Usage</h2>

<h3>1. Analyze WAVs (LYZERv1.0)</h3>

<pre><code>python LYZERv1.0.py
</code></pre>

<p>Produces per-window metric CSVs for the left and right stems.</p>

<h3>2. Compute Differences (DiffEngv2.0)</h3>

<pre><code>python DiffEngv2.0.py
</code></pre>

<p>Produces <code>TrackAB_differences.csv</code> with A–B deltas.</p>

<h3>3. Write Envelopes in REAPER (ElopeIterv2.0)</h3>

<ul>
  <li>Select <strong>exactly two tracks</strong> in REAPER</li>
  <li>Run <code>ElopeIterv2.0.lua</code></li>
</ul>

<p>Trim Volume automation is written to both tracks based on the chosen difference metric.</p>

<hr />

<h2>LYZERv1.0 — Offline Analyzer (Python)</h2>

<p><strong>File:</strong> <code>LYZERv1.0.py</code></p>

<h3>Purpose</h3>

<p>
  Reads WAV files, computes windowed loudness metrics, and writes CSVs for deterministic downstream processing.
  Stereo WAVs are converted to mono by averaging channels.
</p>

<h3>Configurable Windows</h3>

<pre><code>STEP_MS           = 20
RMS_WINDOW_MS     = 50
M_LUFS_WINDOW_MS  = 400
ST_LUFS_WINDOW_MS = 3000
</code></pre>

<h3>Metrics</h3>

<ul>
  <li><strong>RMS</strong> (dB)</li>
  <li><strong>Peak</strong> (linear)</li>
  <li><strong>Momentary LUFS</strong></li>
  <li><strong>Short-Term LUFS</strong></li>
  <li><strong>Integrated LUFS</strong> (full-file)</li>
</ul>

<h3>CSV Columns</h3>

<pre><code>project_time, local_time, sample_start, sample_end,
RMS, Peak, M_LUFS, ST_LUFS, Int_LUFS
</code></pre>

<hr />

<h2>DiffEngv2.0 — Difference Engine (Python)</h2>

<p><strong>File:</strong> <code>DiffEngv2.0.py</code></p>

<h3>Purpose</h3>

<p>
  Loads the two analysis CSVs (A and B), ensures they are aligned, and computes A–B differences for each metric.
</p>

<h3>Output Columns</h3>

<pre><code>project_time, local_time,
RMS_A, RMS_B, RMS_DIFF,
Peak_A, Peak_B, Peak_DIFF,
M_LUFS_A, M_LUFS_B, M_LUFS_DIFF,
ST_LUFS_A, ST_LUFS_B, ST_LUFS_DIFF,
Int_LUFS_A, Int_LUFS_B, Int_LUFS_DIFF
</code></pre>

<hr />

<h2>ElopeIterv2.0 — Envelope Writer (REAPER Lua)</h2>

<p><strong>File:</strong> <code>ElopeIterv2.0.lua</code></p>

<h3>Purpose</h3>

<p>
  Reads <code>TrackAB_differences.csv</code> and writes Trim Volume envelope points to two selected tracks.
  Implements the dual-mono leveler: the louder side is attenuated, preserving stereo image.
</p>

<h3>Metric Selection</h3>

<pre><code>local METRIC = "RMS_DIFF"
</code></pre>

<p>Options: RMS_DIFF, M_LUFS_DIFF, ST_LUFS_DIFF, Int_LUFS_DIFF, Peak_DIFF</p>

<h3>Gain Logic (Reduction-Only)</h3>

<pre><code>diff > 0 → A louder → reduce A
diff < 0 → B louder → reduce B
diff = 0 → no change
</code></pre>

<h3>Calibration</h3>

<pre><code>ENV_ZERO = 716.217850312608   -- 0 dB
ENV_MIN  = 0.0                -- -inf
</code></pre>

<p>Maps dB attenuation to REAPER’s Trim Volume envelope scale.</p>
