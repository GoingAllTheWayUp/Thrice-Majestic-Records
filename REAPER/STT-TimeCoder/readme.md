<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Timecode Speech-to-Text (STT) Processing Tool - GitHub README</title>
    <!-- Tailwind CSS for modern GitHub-like styling -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- MathJax for LaTeX formatting -->
    <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
    <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
</head>
<body class="bg-gray-950 text-gray-100 font-sans antialiased min-h-screen py-10 px-4 sm:px-6 lg:px-8">
    
    <div class="max-w-4xl mx-auto bg-gray-900 border border-gray-800 rounded-xl shadow-2xl overflow-hidden">
        
        <!-- GitHub Repo Header Bar -->
        <div class="bg-gray-800 px-6 py-4 border-b border-gray-700 flex items-center justify-between">
            <div class="flex items-center space-x-2 text-sm text-gray-400">
                <svg class="w-5 h-5 text-gray-400" fill="currentColor" viewBox="0 0 16 16"><path d="M2 2.5A2.5 2.5 0 0 1 4.5 0h8.75a.75.75 0 0 1 .75.75v12.5a.75.75 0 0 1-.75.75h-2.5a.75.75 0 0 1 0-1.5h1.75v-2h-8a1 1 0 0 0-.714 1.7.75.75 0 1 1-1.072 1.05A2.495 2.495 0 0 1 2 11.5v-9zm10.5-1V9h-8c-.356 0-.694.074-1 .208V2.5a1 1 0 0 1 1-1h8zM5 12.25v3.25a.25.25 0 0 0 .4.2l1.45-1.087a.25.25 0 0 1 .3 0L8.6 15.7a.25.25 0 0 0 .4-.2v-3.25a.25.25 0 0 0-.25-.25h-3.5a.25.25 0 0 0-.25.25z"/></svg>
                <span class="font-semibold text-blue-400">username</span>
                <span>/</span>
                <span class="font-semibold text-blue-400">timecode-stt-processor</span>
            </div>
            <div class="flex items-center space-x-2 text-xs">
                <span class="bg-gray-700 text-gray-300 px-2.5 py-1 rounded-full font-medium">README.md</span>
                <span class="bg-blue-600/20 text-blue-400 border border-blue-500/30 px-2.5 py-1 rounded-full font-medium">Python 3.8+</span>
            </div>
        </div>

        <!-- Document Content Body -->
        <div class="p-6 sm:p-10 space-y-8 leading-relaxed">
            
            <!-- Title -->
            <div class="border-b border-gray-800 pb-6">
                <h1 class="text-3xl sm:text-4xl font-extrabold tracking-tight text-white flex items-center space-x-3">
                    <span>🎙️</span>
                    <span>Timecode Speech-to-Text (STT) Processing Tool</span>
                </h1>
                <p class="mt-4 text-gray-300 text-lg">
                    Welcome to the <strong>Timecode STT Processor</strong>, a Python-based utility engineered to convert spoken audio files into precision-timed, word-by-word transcription logs saved directly into a structured CSV format.
                </p>
                <p class="mt-2 text-gray-400">
                    This script is specifically tuned to catch fast-paced, mumbled, or quiet vocals—making it an ideal companion pipeline for automated audio-reactive shaders, lyric videos, music visualizers, or subtitle synchronization.
                </p>
            </div>

            <!-- Layman's Manual -->
            <section class="space-y-4">
                <h2 class="text-2xl font-bold text-white border-b border-gray-800 pb-2">📖 Layman's Manual: What Does This Script Do?</h2>
                <p class="text-gray-300">
                    Imagine you have a recording of someone talking or singing quickly, and you want a computer to look at that audio and tell you the exact millisecond every single word starts and stops. That is precisely what this script achieves!
                </p>
                <ol class="list-decimal list-inside space-y-2 text-gray-300 pl-2">
                    <li><strong class="text-white">Reads Your Audio:</strong> It points to your designated audio recording file on your computer.</li>
                    <li><strong class="text-white">Cleans & Prepares It:</strong> If the audio is recorded in stereo (two separate channels), it flattens it down to mono and standardizes its sample rate so the artificial intelligence can process it cleanly.</li>
                    <li><strong class="text-white">Listens with AI:</strong> It utilizes OpenAI's powerful <strong>Whisper</strong> speech recognition engine. We’ve custom-tuned its sensitivity settings so it doesn't accidentally skip over mumbled words, quiet beginnings, or rapid-fire speaking styles.</li>
                    <li><strong class="text-white">Logs the Data:</strong> It extracts the exact start time and duration for every individual word spoken and writes them neatly into a spreadsheet-ready <code class="bg-gray-800 text-blue-300 px-1.5 py-0.5 rounded text-sm">.csv</code> file containing three columns: <code class="bg-gray-800 text-blue-300 px-1.5 py-0.5 rounded text-sm">start</code>, <code class="bg-gray-800 text-blue-300 px-1.5 py-0.5 rounded text-sm">duration</code>, and <code class="bg-gray-800 text-blue-300 px-1.5 py-0.5 rounded text-sm">text</code>.</li>
                </ol>
            </section>

            <!-- Dependencies -->
            <section class="space-y-6">
                <h2 class="text-2xl font-bold text-white border-b border-gray-800 pb-2">🛠️ Dependency Requirements, Creators, & Usage</h2>
                <p class="text-gray-300">To run this script successfully, you need Python installed along with a few external libraries. Below is the breakdown of each dependency, who created them, and why they are essential to this specific pipeline:</p>

                <div class="space-y-6 pl-2">
                    <!-- Dep 1 -->
                    <div class="bg-gray-800/50 border border-gray-700/60 rounded-lg p-5">
                        <h3 class="text-lg font-semibold text-blue-400 flex items-center space-x-2">
                            <span>1.</span>
                            <code>openai-whisper</code>
                        </h3>
                        <ul class="mt-3 space-y-2 text-sm text-gray-300">
                            <li><strong class="text-gray-200">Creator:</strong> OpenAI (released as open-source in 2022).</li>
                            <li><strong class="text-gray-200">What it is:</strong> A general-purpose speech recognition model trained on a massive dataset of diverse audio capable of multilingual speech recognition and translation.</li>
                            <li><strong class="text-gray-200">Why it is used here:</strong> It serves as the core intelligence of the script. The code invokes <code class="bg-gray-800 text-blue-300 px-1 py-0.5 rounded">model.transcribe()</code> with specialized flags (<code class="bg-gray-800 text-blue-300 px-1 py-0.5 rounded">word_timestamps=True</code>, <code class="bg-gray-800 text-blue-300 px-1 py-0.5 rounded">no_speech_threshold=0.3</code>, <code class="bg-gray-800 text-blue-300 px-1 py-0.5 rounded">temperature=0.0</code>) to force Whisper to break output down into individual words and catch low-volume or rapid speech that standard tools drop.</li>
                        </ul>
                    </div>

                    <!-- Dep 2 -->
                    <div class="bg-gray-800/50 border border-gray-700/60 rounded-lg p-5">
                        <h3 class="text-lg font-semibold text-blue-400 flex items-center space-x-2">
                            <span>2.</span>
                            <code>soundfile</code>
                        </h3>
                        <ul class="mt-3 space-y-2 text-sm text-gray-300">
                            <li><strong class="text-gray-200">Creator:</strong> Bastian Bechtold (built as a Python wrapper around the <code class="bg-gray-800 text-blue-300 px-1 py-0.5 rounded">libsndfile</code> C library, originally created by Erik de Castro Lopo).</li>
                            <li><strong class="text-gray-200">What it is:</strong> A fast, reliable library for reading and writing sound files natively.</li>
                            <li><strong class="text-gray-200">Why it is used here:</strong> Handled via the custom <code class="bg-gray-800 text-blue-300 px-1 py-0.5 rounded">load_audio_direct</code> function, <code class="bg-gray-800 text-blue-300 px-1 py-0.5 rounded">soundfile</code> allows the script to read raw audio data straight from disk efficiently without heavy auxiliary codecs.</li>
                        </ul>
                    </div>

                    <!-- Dep 3 -->
                    <div class="bg-gray-800/50 border border-gray-700/60 rounded-lg p-5">
                        <h3 class="text-lg font-semibold text-blue-400 flex items-center space-x-2">
                            <span>3.</span>
                            <code>numpy</code>
                        </h3>
                        <ul class="mt-3 space-y-2 text-sm text-gray-300">
                            <li><strong class="text-gray-200">Creator:</strong> Travis Oliphant (originally created in 2005 by building upon older libraries like Numeric and Numarray).</li>
                            <li><strong class="text-gray-200">What it is:</strong> The fundamental package for scientific computing and array manipulation in Python, supporting large multi-dimensional matrices and mathematical functions.</li>
                            <li><strong class="text-gray-200">Why it is used here:</strong> Used to manipulate the raw audio waveforms loaded by <code class="bg-gray-800 text-blue-300 px-1 py-0.5 rounded">soundfile</code>. Specifically, it handles stereo-to-mono downmixing (<code class="bg-gray-800 text-blue-300 px-1 py-0.5 rounded">np.mean</code>) and linear interpolation (<code class="bg-gray-800 text-blue-300 px-1 py-0.5 rounded">np.interp</code>) to resample audio data to match the strict $16\text{kHz}$ input format expected by Whisper.</li>
                        </ul>
                    </div>

                    <!-- Dep 4 -->
                    <div class="bg-gray-800/50 border border-gray-700/60 rounded-lg p-5">
                        <h3 class="text-lg font-semibold text-blue-400 flex items-center space-x-2">
                            <span>4.</span>
                            <code>os</code> & <code>csv</code> (Python Standard Libraries)
                        </h3>
                        <ul class="mt-3 space-y-2 text-sm text-gray-300">
                            <li><strong class="text-gray-200">Creator:</strong> Python Core Development Team.</li>
                            <li><strong class="text-gray-200">What it is:</strong> Built-in Python modules for interacting with operating system file paths and parsing/writing Comma-Separated Values files.</li>
                            <li><strong class="text-gray-200">Why it is used here:</strong> <code class="bg-gray-800 text-blue-300 px-1 py-0.5 rounded">os</code> verifies if your input audio paths exist, while <code class="bg-gray-800 text-blue-300 px-1 py-0.5 rounded">csv</code> handles the creation and sequential row-appending of your word-timing logs.</li>
                        </ul>
                    </div>
                </div>
            </section>

            <!-- Instructions -->
            <section class="space-y-4">
                <h2 class="text-2xl font-bold text-white border-b border-gray-800 pb-2">🚀 Getting Started & Installation Instructions</h2>
                <p class="text-gray-300">Follow these step-by-step instructions to get the script running on your machine, even if you are new to Python.</p>
                
                <div class="bg-gray-800/80 border border-gray-700 rounded-lg p-4 space-y-2">
                    <h3 class="font-semibold text-white">Prerequisites</h3>
                    <ul class="list-disc list-inside text-gray-300 space-y-1 text-sm">
                        <li>Ensure you have <strong class="text-white">Python 3.8+</strong> installed on your system.</li>
                        <li>You will also need <strong class="text-white">FFmpeg</strong> installed and added to your system path, as OpenAI's Whisper relies on it to process audio files.</li>
                    </ul>
                </div>

                <div class="space-y-4 pt-2">
                    <div>
                        <h3 class="font-semibold text-white text-lg">Step 1: Install Required Dependencies</h3>
                        <p class="text-gray-300 text-sm mt-1">Open your terminal or command prompt and install the necessary Python libraries using <code class="bg-gray-800 text-blue-300 px-1 py-0.5 rounded">pip</code>:</p>
                        <pre class="bg-black/80 border border-gray-800 text-emerald-400 p-4 rounded-lg mt-2 font-mono text-sm overflow-x-auto"><code>pip install openai-whisper soundfile numpy</code></pre>
                    </div>

                    <div>
                        <h3 class="font-semibold text-white text-lg">Step 2: Configure Your File Paths</h3>
                        <p class="text-gray-300 text-sm mt-1">Open <code class="bg-gray-800 text-blue-300 px-1 py-0.5 rounded">timecode-STT.v2.py</code> in any text editor and update the configuration variables at the top of the file to point to your actual local file locations:</p>
                        <pre class="bg-black/80 border border-gray-800 text-blue-300 p-4 rounded-lg mt-2 font-mono text-sm overflow-x-auto"><code># Configuration Paths
AUDIO_PATH = r"C:\Your\Path\To\Audio-2-STT.wav"
CSV_PATH = r"C:\Your\Path\To\Save\Audio_Transcription.csv"</code></pre>
                    </div>

                    <div>
                        <h3 class="font-semibold text-white text-lg">Step 3: Run the Script</h3>
                        <p class="text-gray-300 text-sm mt-1">Execute the script from your terminal:</p>
                        <pre class="bg-black/80 border border-gray-800 text-emerald-400 p-4 rounded-lg mt-2 font-mono text-sm overflow-x-auto"><code>python timecode-STT.v2.py</code></pre>
                    </div>
                </div>
            </section>

            <!-- Advanced Tuning -->
            <section class="space-y-4">
                <h2 class="text-2xl font-bold text-white border-b border-gray-800 pb-2">⚙️ Advanced Parameter Tuning Reference</h2>
                <p class="text-gray-300">If you want to experiment with performance or accuracy, look inside the <code class="bg-gray-800 text-blue-300 px-1 py-0.5 rounded">transcribe_and_update_csv</code> function:</p>
                <ul class="list-disc list-inside space-y-2 text-gray-300 pl-2">
                    <li><strong class="text-white"><code class="bg-gray-800 text-blue-300 px-1 py-0.5 rounded">model_size</code>:</strong> Defaults to <code class="bg-gray-800 text-blue-300 px-1 py-0.5 rounded">"small"</code>. You can change this to <code class="bg-gray-800 text-blue-300 px-1 py-0.5 rounded">"tiny"</code>, <code class="bg-gray-800 text-blue-300 px-1 py-0.5 rounded">"base"</code>, <code class="bg-gray-800 text-blue-300 px-1 py-0.5 rounded">"medium"</code>, or <code class="bg-gray-800 text-blue-300 px-1 py-0.5 rounded">"large"</code> depending on your hardware capabilities and accuracy needs.</li>
                    <li><strong class="text-white"><code class="bg-gray-800 text-blue-300 px-1 py-0.5 rounded">no_speech_threshold=0.3</code>:</strong> Lowered from the default to ensure quieter or mumbled vocal starts are captured instead of filtered out as silence.</li>
                    <li><strong class="text-white"><code class="bg-gray-800 text-blue-300 px-1 py-0.5 rounded">compression_ratio_threshold=2.6</code>:</strong> Prevents the algorithm from falsely discarding fast, repeating phrasing blocks.</li>
                    <li><strong class="text-white"><code class="bg-gray-800 text-blue-300 px-1 py-0.5 rounded">duration</code> floor (<code class="bg-gray-800 text-blue-300 px-1.5 py-0.5 rounded">max(end_time - start_time, 0.35)</code>):</strong> Ensures ultra-fast words hold a minimum duration threshold of $0.35$ seconds, preventing visual glitches if mapped directly to shader animations.</li>
                </ul>
            </section>

        </div>

        <!-- Footer -->
        <div class="bg-gray-950 px-6 py-4 border-t border-gray-800 text-center text-xs text-gray-500">
            Timecode Speech-to-Text Pipeline • Built for Python & Whisper
        </div>

    </div>

</body>
</html>