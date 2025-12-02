import requests

BASE = "http://localhost:5000"
EMAIL = "john@student.pict.edu"
PASSWORD = "student123"

resp = requests.post(f"{BASE}/api/auth/login", json={"email": EMAIL, "password": PASSWORD})
print("login status", resp.status_code)
print(resp.text)
token = resp.json().get("token")
print("token", token[:25] + "..." if token else None)

if token:
    headers = {"Authorization": f"Bearer {token}"}
    resp2 = requests.get(f"{BASE}/api/student/dashboard", headers=headers)
    print("dashboard status", resp2.status_code)
    print(resp2.text[:200])

