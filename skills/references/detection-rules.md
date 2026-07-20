# Detection Rules - Admin Panel & Login Page Identification

This file contains the core detection rules for identifying admin panels and login pages.

## Login Page Indicators

These patterns indicate a page is likely a login page. They look for password input fields, login forms, and authentication-related content.

### Password Field Patterns
```
[type="password"]
[type='password']
[type:"password"]
[Type="password"]
[Type='password']
[input[type=password]]
["a-input-password"]
[type=password]
[type: \"password\"]
[Type:"password"]
[type="Password"]
```

### Login Configuration Patterns
```
[logIn:"登录",username:"账号",password:"密码"]
["input-password"]
[/_app.config.js?v=]
[auth.password]
```

### Product-Specific Markers
```
[<title>金蝶云]    # Kingdee Cloud
```

**Detection Logic:** If ANY of these patterns are found in the HTML response (wrapped in brackets for context matching), the page is flagged as a potential login page.

---

## CAPTCHA Detection Rules

These patterns identify the presence of CAPTCHA/verification code fields on login pages.

### CAPTCHA Indicators
```
[请输入验证码]              # "Please enter verification code"
[placeholder="验证码"]      # Placeholder with "verification code"
[placeholder="captcha"]     # English captcha placeholder
[title="验证码"]            # Title with "verification code"
[title="captcha"]           # English captcha title
[alt="验证码"]              # Alt text with "verification code"
[alt="captcha"]             # English captcha alt
[name="captcha"]            # Input name "captcha"
[请输入手机验证码]          # "Please enter SMS verification code"
[login.VerificationCode"]   # JavaScript verification code variable
[validateEvent]             # Validation event
[validateState]             # Validation state
```

**Usage:** CAPTCHA detection increases the confidence that a page is a login page and provides additional context for the user.

---

## False Positive Exclusion Rules

These patterns identify pages that should be EXCLUDED from results (not admin/login pages).

### Exclusion Patterns
```
页面不存在</title>          # "Page not found" in title
<h1>页面不存在.</h1>        # "Page not found" heading (with period)
<h1>页面不存在</h1>         # "Page not found" heading
<h2>页面不存在.</h2>        # "Page not found" subheading (with period)
<h2>页面不存在</h2>         # "Page not found" subheading
<title>AIHelp Web Portal</title>  # AIHelp portal (not admin)
```

**Detection Logic:** If ANY of these patterns are found, the page is IMMEDIATELY excluded from results, even if other login indicators are present.

---

## Confidence Scoring System

### High Confidence
- Matches admin condition regex patterns (product fingerprints)
- Contains both password field AND admin-related title
- Matches multiple product-specific patterns
- Known admin URL paths (e.g., /admin, /wp-admin)

### Medium Confidence
- Matches login CSS conditions (password fields)
- Contains login-related text but no admin indicators
- Generic login paths (e.g., /login, /signin)
- Does NOT match any exclusion patterns

### Low Confidence
- Partial matches or ambiguous indicators
- Generic paths that could be admin (e.g., /dashboard, /portal)
- Requires manual verification

---

## Detection Workflow

```
1. Fetch URL
   |
2. Check exclusion patterns (false positives)
   |--> If matched: EXCLUDE and stop
   |
3. Check login CSS conditions
   |
4. Check admin condition regex patterns
   |
5. Check CAPTCHA conditions
   |
6. Calculate confidence level
   |
7. Extract page title
   |
8. Record result with metadata
```

---

## HTTP Request Configuration

### Headers
```python
{
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, sdch",
    "Accept-Language": "en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4,zh-TW;q=0.2",
    "Connection": "keep-alive",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.2357.130 Safari/537.36",
}
```

### Request Settings
- Timeout: 10 seconds
- Follow redirects: Yes
- SSL verification: No (ignore certificate errors)
- Accept status codes: 200, 401
- Max response size: 5MB

---

## URL Extraction & Following

### Redirect URL Patterns
Extract redirect URLs from:
- `location.href = "..."`
- `<meta http-equiv="refresh" ... url=...>`
- `window.open("...")`

### JavaScript/CSS Link Extraction
- `<script src="...">` - Extract JavaScript file URLs
- `<link href="...">` - Extract CSS file URLs
- `<a href="...">` - Extract link URLs

Filter out static assets (.js, .css, .png, .jpg, .gif, etc.) and scan remaining URLs.

---

## Result Deduplication

### Enhanced Deduplication Logic

The scanner uses a **multi-layer deduplication** approach to prevent reporting duplicate or near-duplicate results:

#### Layer 1: URL Normalization
1. Remove trailing slashes (`/admin/` → `/admin`)
2. Remove query parameters (`/admin?id=1` → `/admin`)
3. Convert to lowercase for comparison
4. If normalized URLs match, keep only the first result

#### Layer 2: Content Hashing
1. Strip dynamic content from HTML:
   - Remove `<meta>` tags (often contain timestamps)
   - Remove `<script>` blocks (may contain dynamic tokens)
   - Remove HTML comments
   - Normalize whitespace
2. Compute hash of cleaned content
3. If content hashes match AND URLs are similar, treat as duplicate

#### Layer 3: Title Similarity
1. Compare page titles (case-insensitive)
2. If titles are identical AND:
   - Confidence levels match
   - URLs contain each other (e.g., `/admin` in `/admin/index`)
3. Keep only one result

#### Layer 4: Response Length Comparison
1. Group results by title + CAPTCHA status
2. Compare response lengths within each group
3. If responses are within 50 bytes, keep only one

### Deduplication Examples

**Example 1: Trailing Slash Duplicate**
- `/admin` and `/admin/` return identical content
- **Result**: Only report `/admin`

**Example 2: Query Parameter Duplicate**
- `/login` and `/login?redirect=/admin` return same page
- **Result**: Only report `/login`

**Example 3: Similar Path Duplicate**
- `/admin` and `/admin/index.php` return same title and content
- **Result**: Only report `/admin`

**Example 4: Different Pages**
- `/admin` (Admin Panel) and `/login` (Login Page) have different content
- **Result**: Report both

---

## Best Practices for Detection

1. **Always check exclusion patterns first** - Avoid false positives
2. **Use multiple indicators** - Don't rely on a single pattern match
3. **Consider context** - URL path + content + title together
4. **Product fingerprints > Generic patterns** - Higher confidence for known products
5. **CAPTCHA presence increases confidence** - Indicates authentication requirement
6. **Deduplicate results** - Avoid noise from similar pages

---

## Common Detection Scenarios

### Scenario 1: Clear Admin Panel
- URL: `/admin`
- Title: `<title>后台管理系统</title>`
- Content: Contains `[type="password"]`
- Result: HIGH confidence, Admin Panel

### Scenario 2: Login Page
- URL: `/login`
- Title: `<title>用户登录</title>`
- Content: Contains `[type="password"]` and `[placeholder="验证码"]`
- Result: MEDIUM confidence, Login Page with CAPTCHA

### Scenario 3: Known Product
- URL: `/druid/login.html`
- Title: `<title>Druid Stat Index</title>`
- Content: Matches `<title>druid.*</title>`
- Result: HIGH confidence, Druid Admin Panel

### Scenario 4: False Positive
- URL: `/admin-nonexistent`
- Title: `<title>页面不存在</title>`
- Content: Matches exclusion pattern
- Result: EXCLUDED (not reported)
