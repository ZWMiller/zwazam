<<<<<<< HEAD
# A simple model-based prediction app

Running locally...
=======
# A simple song fingerprint app
>>>>>>> 28423d6a3fa786091cd7f157c46e83fb6ccbca31

Start by booting up the app:

```bash
python zwazam_api.py
```

In a different terminal you can do:

#### Example with `curl`:

```bash
curl http://127.0.0.1:5000

curl http://127.0.0.1:5000/match -X POST -H 'Content-Type: application/json' -d '{"waveform": [11,20,31,4,5,6,73,...]}'
```


#### Example with `requests`:

```python
import requests

response = requests.get('http://127.0.0.1:5000/')
print(response.text)

response = requests.post('http://127.0.0.1:5000/match',
                         json={'waveform': [11,20,31,4,5,6,73,...]})
print(response.json())
```

#### A usage example with real data is here: [test_api](test_api.py)
