import httpx

BASE = "http://localhost:8000"

# 1. Login
r = httpx.post(f"{BASE}/api/v1/auth/login", json={
    "username_or_email": "admin@library.com",
    "password": "Admin@123"
})
print(f"1. Login: {r.status_code}")
assert r.status_code == 200
token = r.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
user = r.json()["user"]
print(f"   User: {user['full_name']} ({user['role']})")

# 2. Create Author
r = httpx.post(f"{BASE}/api/v1/authors", json={
    "name": "J.K. Rowling", "nationality": "British"
}, headers=headers)
print(f"2. Create Author: {r.status_code}")
assert r.status_code == 201
author_id = r.json()["id"]

# 3. Create Publisher
r = httpx.post(f"{BASE}/api/v1/publishers", json={
    "name": "Bloomsbury"
}, headers=headers)
print(f"3. Create Publisher: {r.status_code}")
assert r.status_code == 201
publisher_id = r.json()["id"]

# 4. Create Category
r = httpx.post(f"{BASE}/api/v1/categories", json={
    "name": "Fantasy"
}, headers=headers)
print(f"4. Create Category: {r.status_code}")
assert r.status_code == 201
category_id = r.json()["id"]

# 5. Create Book
r = httpx.post(f"{BASE}/api/v1/books", json={
    "title": "Harry Potter and the Philosopher's Stone",
    "isbn": "9780747532699",
    "author_id": author_id,
    "publisher_id": publisher_id,
    "category_id": category_id,
    "total_copies": 5,
    "language": "English",
}, headers=headers)
print(f"5. Create Book: {r.status_code}")
assert r.status_code == 201
book_id = r.json()["id"]

# 6. List Books
r = httpx.get(f"{BASE}/api/v1/books")
print(f"6. List Books: {r.status_code}, total={r.json()['total']}")

# 7. Settings
r = httpx.get(f"{BASE}/api/v1/settings", headers=headers)
print(f"7. Settings: {r.status_code}")
settings_keys = [s["key"] for s in r.json()["items"]]
print(f"   Keys: {', '.join(settings_keys)}")

# 8. Dashboard
r = httpx.get(f"{BASE}/api/v1/reports/dashboard", headers=headers)
print(f"8. Dashboard: {r.status_code}")
d = r.json()
print(f"   Books: {d['total_books']}, Students: {d['total_students']}, Borrowed: {d['total_borrowed']}")

# 9. Change Password
r = httpx.post(f"{BASE}/api/v1/auth/change-password", json={
    "old_password": "Admin@123",
    "new_password": "NewAdmin@123"
}, headers=headers)
print(f"9. Change Password: {r.status_code}")

print("\nAll tests passed!")
