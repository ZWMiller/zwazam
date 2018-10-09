# A simple model-based prediction app

Running `predictor_app.py` locally...


#### Example with `curl`:

```bash
curl http://127.0.0.1:5000

curl http://127.0.0.1:5000/predict -X POST -H 'Content-Type: application/json' -d '{"example": [154]}'
```


#### Example with `requests`:

```python
import requests

response = requests.get('http://127.0.0.1:5000/')
print response.text

response = requests.post('http://127.0.0.1:5000/predict',
                         json={'example': [154]})
print response.json()
```
