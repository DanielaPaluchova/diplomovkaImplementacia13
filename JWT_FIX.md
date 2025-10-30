# ✅ Oprava JWT Tokenu - "Subject must be a string"

## 🐛 Problém

```json
{
  "error": "Invalid or expired token",
  "message": "Subject must be a string"
}
```

## 🔍 Príčina

**Flask-JWT-Extended očakáva string ako identity, ale dostával Integer!**

### V kóde:

```python
# ❌ ZLEHACKPÁVA
access_token = create_access_token(identity=user.id)  # user.id je Integer!
```

Flask-JWT-Extended internálne vyžaduje, aby `identity` (subject v JWT tokene) bol **string**, nie číslo.

---

## ✅ Riešenie

### 1. **Backend `/auth/login`** (`backend/app/routes/auth.py`)

**Riadok 70:**

```python
# PRED:
access_token = create_access_token(identity=user.id)  # ❌ Integer

# PO:
access_token = create_access_token(identity=str(user.id))  # ✅ String
```

### 2. **Backend `/auth/register`** (`backend/app/routes/auth.py`)

**Riadok 41:**

```python
# PRED:
access_token = create_access_token(identity=user.id)  # ❌ Integer

# PO:
access_token = create_access_token(identity=str(user.id))  # ✅ String
```

### 3. **Get Current User** (`backend/app/utils/auth.py`)

**Riadok 24-25:**

```python
# PRED:
def get_current_user():
    user_id = get_jwt_identity()
    return User.query.get(user_id)  # ❌ user_id je string, ale DB očakáva int

# PO:
def get_current_user():
    user_id = get_jwt_identity()  # This is a string now
    return User.query.get(int(user_id))  # ✅ Convert back to int for DB query
```

---

## 🚀 Ako spustiť opravený backend

### **KROK 1: Zastaviť starý backend**

```powershell
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
```

### **KROK 2: Spustiť nový backend**

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python run.py
```

**Očakávaný output:**

```
 * Serving Flask app 'app'
 * Debug mode: on
WARNING: This is a development server.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.x.x:5000
Press CTRL+C to quit
```

### **KROK 3: Otestovať backend**

**V novom PowerShell okne:**

```powershell
Invoke-RestMethod -Uri "http://localhost:5000/api/health" -Method GET
```

**Očakávaný output:**

```json
{
  "status": "ok",
  "message": "Diplomová práca API is running"
}
```

---

## 🧪 Testovanie

### **1. Otestovať login cez PowerShell/curl:**

```powershell
$body = @{
    email = "manager@example.com"
    password = "manager123"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:5000/api/auth/login" `
    -Method POST `
    -Body $body `
    -ContentType "application/json"

$response
```

**Očakávaný output:**

```json
{
  "user": {
    "id": 2,
    "email": "manager@example.com",
    "name": "Project Manager",
    "role": "manager",
    ...
  },
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### **2. Otestovať protected endpoint:**

```powershell
$token = $response.token

$headers = @{
    "Authorization" = "Bearer $token"
}

Invoke-RestMethod -Uri "http://localhost:5000/api/teams" `
    -Method GET `
    -Headers $headers
```

**Očakávaný výsledok:** ✅ **Status 200** + data z databázy

---

## 📊 Zhrnutie zmien

| Súbor                           | Zmena          | Dôvod                        |
| ------------------------------- | -------------- | ---------------------------- |
| `backend/app/routes/auth.py:41` | `str(user.id)` | JWT identity musí byť string |
| `backend/app/routes/auth.py:70` | `str(user.id)` | JWT identity musí byť string |
| `backend/app/utils/auth.py:25`  | `int(user_id)` | DB query vyžaduje integer    |

---

## 🎯 Výsledok

### ✅ **Po týchto opravách:**

1. ✅ Login vráti validný JWT token
2. ✅ JWT token obsahuje string ako subject
3. ✅ Protected endpoints prijmú a validujú token správne
4. ✅ Žiadne "Subject must be a string" errors
5. ✅ Frontend môže autentifikovať a pristupovať k API

---

## 🔍 Technické vysvetlenie

**Prečo Flask-JWT-Extended vyžaduje string?**

JWT štandard (RFC 7519) definuje `sub` (subject) claim ako:

> "The 'sub' (subject) claim identifies the principal that is the subject of the JWT. The value MUST be a **string**."

Flask-JWT-Extended dodržiava tento štandard a trvá na type safety.

---

**Status:** ✅ **HOTOVO - REŠTARTUJ BACKEND!**

---

## 🚨 Ak backend stále nefunguje:

1. Skontroluj, či beží PostgreSQL
2. Skontroluj `.env` súbor v `backend/` folder
3. Skontroluj, či existuje databáza `diplonovka_db`
4. Skontroluj console output backendu pre chybové hlášky

