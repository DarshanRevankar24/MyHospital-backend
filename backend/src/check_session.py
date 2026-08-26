import urllib.request
import urllib.parse
import http.cookiejar
import json

jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))

# Step 1: Login
data = urllib.parse.urlencode({'username': 'darshan', 'password': 'MyHospital@123'}).encode()
req = urllib.request.Request('http://localhost:8000/api/v1/auth/login', data=data, method='POST')
req.add_header('Content-Type', 'application/x-www-form-urlencoded')

try:
    resp = opener.open(req)
    body = resp.read().decode()
    print('Login status:', resp.status)
    print('Login body:', body)
    print()
    print('Cookies received:')
    for c in jar:
        print(f'  name={c.name!r}  secure={c.secure}  httponly={c.has_nonstandard_attr("HttpOnly")}  samesite={c.get_nonstandard_attr("SameSite", "not-set")}  domain={c.domain}  path={c.path}')

    csrf_token = json.loads(body).get('csrf_token')
    print(f'\nCSRF token: {csrf_token}')

    # Step 2: protected endpoint
    req2 = urllib.request.Request('http://localhost:8000/api/v1/auth/check-auth')
    if csrf_token:
        req2.add_header('x-csrf-token', csrf_token)
    resp2 = opener.open(req2)
    print('\ncheck-auth status:', resp2.status)
    print('check-auth body:', resp2.read().decode())

except urllib.error.HTTPError as e:
    print('HTTP Error on login:', e.code, e.reason)
    print(e.read().decode())
