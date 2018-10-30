import requests
import sys
sys.path.append("../src")

response = requests.post('http://127.0.0.1:5000/wav_upload',
                         files={'file':open('../test_wav/samples_for_test/Bust_This_subsection.wav','rb')})
print(response.json())