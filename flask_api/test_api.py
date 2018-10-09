import requests
import sys
sys.path.append("../src")
from wav_fingerprint import WavFingerprint

track = WavFingerprint("../test_wav/samples_for_test/Bust_This_subsection.wav", min_peak_amplitude=50)
response = requests.post('http://127.0.0.1:5000/match',
                         json={'waveform':track.raw_data_left.tolist()})
print(response.json())