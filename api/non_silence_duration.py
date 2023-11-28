from flask import Flask, request, jsonify
import numpy as np
import io
import wave

app = Flask(__name__)

@app.route('/calculate-duration', methods=['POST'])
def calculate_duration():
    if 'file' not in request.files:
        return jsonify(error='No file part'), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify(error='No selected file'), 400

    try:
        audio_data = io.BytesIO(file.read())
        non_silence_duration_seconds = calculate_non_silence_duration(audio_data)
        return jsonify(duration=non_silence_duration_seconds)
    except Exception as e:
        return jsonify(error=str(e)), 500

def calculate_non_silence_duration(audio_data_io, threshold_dB=-20):
    # Open the audio data as a wave file
    with wave.open(audio_data_io, 'rb') as wf:
        # Extract audio parameters and read frames
        n_channels, _, framerate, n_frames, _, _ = wf.getparams()
        frames = wf.readframes(n_frames)
    
    # Convert frames to numpy array
    audio = np.frombuffer(frames, dtype=np.int16)
    if n_channels == 2:
        audio = audio.reshape(-1, 2).mean(axis=1)
    
    amplitude = np.abs(audio)
    ref = 32768
    amplitude_dB = 20 * np.log10(np.where(amplitude == 0, np.finfo(float).eps, amplitude) / ref)
    non_silence = amplitude_dB > threshold_dB
    non_silence_duration = np.sum(non_silence) / framerate
    
    return non_silence_duration

if __name__ == '__main__':
    app.run()
