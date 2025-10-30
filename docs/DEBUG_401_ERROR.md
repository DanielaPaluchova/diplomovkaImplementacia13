# 🔍 Debug 401 Unauthorized Error

## Problém:

```
127.0.0.1 - - [21/Oct/2025 18:05:13] "GET /api/teams HTTP/1.1" 401 -
```

**401 Unauthorized** znamená, že JWT token:

1. Nie je posielaný
2. Nie je správne formátovaný
3. Alebo je neplatný/expirovaný

---

## 🛠️ Debug Kroky:

### 1. Skontroluj Token v Browser Console (F12):

```javascript
// Skontroluj či token existuje
console.log('Token:', localStorage.getItem('auth_token'));
console.log('User:', localStorage.getItem('auth_user'));

// Alebo session storage
console.log('Session Token:', sessionStorage.getItem('auth_token'));
```

**Ak token chýba** → Prihlás sa znova!

---

### 2. Skontroluj Network Request (F12 → Network Tab):

1. Otvor **Network tab**
2. Klikni na request **GET /api/teams**
3. Pozri **Headers → Request Headers**
4. **Hľadaj:** `Authorization: Bearer <token>`

**Ak Authorization header chýba** → Token sa neposiela!

---

### 3. Manuálny Test cez Console:

```javascript
// Get token
const token = localStorage.getItem('auth_token');
console.log('Token:', token);

// Test API call
fetch('http://localhost:5000/api/teams', {
  headers: {
    Authorization: `Bearer ${token}`,
  },
})
  .then((r) => r.json())
  .then((d) => console.log('✅ Success:', d))
  .catch((e) => console.error('❌ Error:', e));
```

---

### 4. Backend Token Verification Test:

```bash
# V PowerShell (v backend adresári):
cd backend
python

# Potom v Python:
>>> from app import create_app, db
>>> from app.models.user import User
>>> app = create_app()
>>> with app.app_context():
...     users = User.query.all()
...     for u in users:
...         print(f"User: {u.email}, ID: {u.id}")
```

---

## 🔧 Možné Riešenia:

### Riešenie 1: Token Nie Je Uložený

**Problém:** Po prihlásení sa token neuložil do localStorage/sessionStorage

**Fix v `auth-store.ts`:**

```typescript
// Skontroluj že toto sa vykoná po úspešnom logine:
if (token.value) {
  localStorage.setItem('auth_token', token.value);
  localStorage.setItem('auth_user', JSON.stringify(user.value));
}
```

---

### Riešenie 2: Token Sa Neposiela

**Problém:** Axios interceptor nepridáva Authorization header

**Fix v `services/api.ts`:**

```typescript
this.client.interceptors.request.use((config) => {
  const authStore = useAuthStore();
  console.log('🔐 Token from store:', authStore.token); // DEBUG
  if (authStore.token) {
    config.headers.Authorization = `Bearer ${authStore.token}`;
    console.log('✅ Authorization header added'); // DEBUG
  } else {
    console.warn('⚠️ No token in store!'); // DEBUG
  }
  return config;
});
```

---

### Riešenie 3: JWT Secret Key Nesedí

**Problém:** Backend používa iný JWT_SECRET_KEY ako pri vytváraní tokenu

**Skontroluj `backend/.env`:**

```env
JWT_SECRET_KEY=dev-jwt-secret-key-diplomovka-2024
```

**A `backend/app/__init__.py`:**

```python
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev-jwt-secret-key-diplomovka-2024')
```

---

### Riešenie 4: Token Expiroval

**Problém:** Token expiroval (default je 1 hodina)

**Fix:** Prihlás sa znova alebo zvýš expiráciu v `backend/.env`:

```env
JWT_ACCESS_TOKEN_EXPIRES=86400  # 24 hodín
```

---

## ✅ Quick Fix - Vyskúšaj toto:

### 1. **Logout a Login znova:**

```javascript
// V browser console:
localStorage.clear();
sessionStorage.clear();
// Potom sa prihlás znova
```

### 2. **Pridaj Debug Logging:**

**V `src/services/api.ts` - line 26:**

```typescript
this.client.interceptors.request.use((config) => {
  const authStore = useAuthStore();
  console.log('🔍 Auth Store Token:', authStore.token); // ADD THIS
  if (authStore.token) {
    config.headers.Authorization = `Bearer ${authStore.token}`;
    console.log('✅ Added Authorization header'); // ADD THIS
  }
  return config;
});
```

### 3. **Reštartuj Backend:**

```bash
# Zastav backend (Ctrl+C)
cd backend
python run.py
```

---

## 🎯 Očakávaný Výsledok:

Po oprave by mal request vyzerať takto:

**Request Headers:**

```
GET /api/teams HTTP/1.1
Host: localhost:5000
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
Content-Type: application/json
```

**Response:**

```
HTTP/1.1 200 OK
Content-Type: application/json

[
  { "id": 1, "name": "John Doe", ... },
  ...
]
```

---

## 📝 Checklist:

- [ ] Token existuje v localStorage/sessionStorage
- [ ] Authorization header sa posiela v requestoch
- [ ] Token je správne formátovaný (`Bearer <token>`)
- [ ] JWT_SECRET_KEY je rovnaký v backend/.env
- [ ] Token nie je expirovaný
- [ ] Backend beží a vracia správne responsy

---

**Ak stále nefunguje, skontroluj console logy a pošli mi output!** 🔍
