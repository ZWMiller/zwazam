# A simple song fingerprint app


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
                         json={'example': [11,20,31,4,5,6,73,...]})
print response.json()
```
