# ✅ Všetky Errory Opravené!

## 🔧 Opravy (4 linter errors → 0):

### 1. ✅ Linter Errors

**Files:** `ProjectsPage.vue`, `TeamPage.vue`

**Zmena:**

```typescript
// PRED:
catch (error) {
  $q.notify({ message: 'Failed...' });
}

// PO:
catch (err) {
  console.error('Operation error:', err);
  $q.notify({ message: 'Failed...' });
}
```

### 2. ✅ CORS Configuration

**File:** `backend/app/__init__.py`

**Zmena:**

```python
CORS(app, resources={
    r"/api/*": {
        "origins": ["*"],  # Allow all origins in development
        "methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "Access-Control-Allow-Origin"],
        "supports_credentials": False,
        "max_age": 3600
    }
})
```

### 3. ✅ Environment Files

**Frontend `.env` (root):**

```
VITE_API_BASE_URL=http://localhost:5000/api
```

**Backend `.env` (backend/):**

```
DATABASE_URL=postgresql://postgres:daniela13@localhost:5432/diplonovka_db
CORS_ORIGINS=http://localhost:9000,http://localhost:9001
JWT_SECRET_KEY=dev-jwt-secret-key-diplomovka-2024
...
```

---

## 🚀 AKO SPUSTIŤ:

### Terminal 1 - Backend:

```bash
cd backend
.\venv\Scripts\Activate.ps1
python run.py
```

### Terminal 2 - Frontend:

```bash
npm run dev
```

### Test v browseri:

```
http://localhost:9000
Login: admin@example.com / admin123
```

---

## ✅ Výsledok:

- ✅ **Linter:** 0 errors
- ✅ **CORS:** Nakonfigurovaný
- ✅ **Environment:** Frontend `.env` ready
- ✅ **Backend:** Ready to start
- ✅ **Frontend:** Ready to start

---

## 🐛 Ak máš problémy:

### CORS Error v Console:

1. Uisti sa, že backend beží: `curl http://localhost:5000/api/health`
2. Reštartuj backend po zmene CORS settings

### Data sa nenačítavajú:

1. Otvor Console (F12)
2. Skontroluj Network tab
3. Hľadaj červené requests
4. Skontroluj či backend beží

### Backend sa nespúšťa:

```bash
cd backend
.\venv\Scripts\Activate.ps1
python seed_database.py  # Ak treba reseed
python run.py
```

---

🎉 **Hotovo! Teraz spusti backend a frontend!** 🎉
