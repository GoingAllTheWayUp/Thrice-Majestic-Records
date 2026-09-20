import os
import csv
import numpy as np
import soundfile as sf
import whisper

# Configuration Paths
AUDIO_PATH = r"X:\Path\To)\Transcript\Recorded\Vocal\Audio-2-STT.wav"
CSV_PATH = r"X:\Path\To|Save\Vocal\Audio_Transcription.csv"

def load_audio_direct(file_path, target_sr=16000):
    """Loads audio file natively using soundfile and resamples/mono-mixes for Whisper."""
    data, samplerate = sf.read(file_path)
    
    # Convert stereo to mono if necessary
    if len(data.shape) > 1:
        data = np.mean(data, axis=1)
        
    if samplerate != target_sr:
        duration = len(data) / samplerate
        target_length = int(duration * target_sr)
        data = np.interp(
            np.linspace(0, len(data) - 1, target_length),
            np.arange(len(data)),
            data
        )
    return data.astype(np.float32)

def transcribe_and_update_csv(audio_file, csv_file, model_size="small"):
    if not os.path.exists(audio_file):
        print(f"Error: Audio file not found at {audio_file}")
        return

    # Upgrading to "small" or "medium" gives drastically better results for fast/mumbled vocals
    print(f"Loading Whisper model ('{model_size}')...")
    model = whisper.load_model(model_size)

    print(f"Loading audio data natively from: {audio_file}")
    audio_array = load_audio_direct(audio_file)

    print("Transcribing with high-sensitivity parameters for fast/mumbled speech...")
    
    # Tuned parameters to catch fast speech and mumbling:
    # - word_timestamps=True: Breaks down phrases word-by-word for your shader
    # - no_speech_threshold=0.3: Relaxes the silence filter to catch quieter/mumbled starts
    # - compression_ratio_threshold=2.6: Prevents Whisper from discarding fast-paced text
    # - condition_on_previous_text=False: Keeps it from getting confused by fast overlapping words
    result = model.transcribe(
        audio_array, 
        word_timestamps=True,
        no_speech_threshold=0.3,
        compression_ratio_threshold=2.6,
        condition_on_previous_text=False,
        temperature=0.0
    )

    segments = result.get("segments", [])
    print(f"Transcription complete. Found {len(segments)} segments.")

    file_exists = os.path.exists(csv_file)

    with open(csv_file, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        if not file_exists:
            writer.writerow(["start", "duration", "text"])
            print("Created new phrases.csv with headers [start, duration, text].")

        print(f"Appending word-by-word rows to: {csv_file}")
        for segment in segments:
            words = segment.get("words", [])
            for w in words:
                word_text = w["word"].strip()
                if not word_text:
                    continue
                
                start_time = round(w["start"], 3)
                end_time = round(w["end"], 3)
                
                # Minimum duration floor of 0.35s so quick words register on the shader
                duration = round(max(end_time - start_time, 0.35), 3)

                writer.writerow([start_time, duration, word_text])
                print(f"  [word] {start_time}s -> {duration}s: \"{word_text}\"")

    print("Successfully updated phrases.csv!")

if __name__ == "__main__":
    transcribe_and_update_csv(AUDIO_PATH, CSV_PATH, model_size="small")