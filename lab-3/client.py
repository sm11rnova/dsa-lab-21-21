import requests

# 1) GET
resp1 = requests.get('http://localhost:5000/number/', params={'param': 5}).json()
# 2) POST
resp2 = requests.post(
    'http://localhost:5000/number/',
    json={'jsonParam': 7},
    headers={'Content-Type': 'application/json'}
).json()
# 3) DELETE
resp3 = requests.delete('http://localhost:5000/number/').json()

# 4) Собираем выражение:
expr = f"{resp1['result']}{resp1['operation']}{resp2['result']}{resp2['operation']}{resp3['result']}"
print(int(eval(expr)))
