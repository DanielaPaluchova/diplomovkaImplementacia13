# ✅ Backend Setup Complete!

## 🎉 Čo je hotové

### Backend (Flask + PostgreSQL)

✅ **Databázové modely:**

- User (authentication)
- TeamMember
- Project (with sprints and roles)
- Sprint
- Task (with PERT + RACI data)
- ProjectRole (permissions)
- Experiment (research data)

✅ **API Endpointy:**

- `/api/auth/*` - Authentication (login, register, profile)
- `/api/projects/*` - Projects CRUD + sprints management
- `/api/teams/*` - Team members CRUD
- `/api/tasks/*` - Tasks CRUD + PERT/RACI + bulk update
- `/api/experiments/*` - Experiments CRUD + stats
- `/api/analytics/*` - Dashboard, PERT+RACI metrics, workload, efficiency, comparison

✅ **Security:**

- JWT authentication
- Password hashing (bcrypt)
- Role-based access control (Admin, Manager, Developer, Viewer)
- CORS configured

✅ **Database:**

- PostgreSQL databáza `diplonovka_db` vytvorená
- Seed dáta naplnené (3 users, 6 team members, 2 projects with tasks, 5 experiments)

✅ **Server:**

- Beží na `http://localhost:5000`
- Health check: `http://localhost:5000/api/health`

---

## 🚀 Ako spustiť

### Backend

```bash
cd backend
.\venv\Scripts\Activate.ps1
python run.py
```

### Frontend

```bash
# V root adresári projektu
npm run dev
```

---

## 🔐 Demo účty

| Email                 | Password   | Role      |
| --------------------- | ---------- | --------- |
| admin@example.com     | admin123   | Admin     |
| manager@example.com   | manager123 | Manager   |
| developer@example.com | dev123     | Developer |

---

## 📁 Štruktúra projektu

```
quasar-project/
├── backend/                    # ✅ NOVÉ - Flask Backend
│   ├── app/
│   │   ├── models/             # Database models
│   │   ├── routes/             # API endpoints
│   │   ├── utils/              # Auth helpers
│   │   └── __init__.py         # Flask app factory
│   ├── venv/                   # Python virtual environment
│   ├── .env                    # Environment variables
│   ├── requirements.txt        # Python dependencies
│   ├── run.py                  # Server entry point
│   ├── create_database.py      # Database creation script
│   ├── seed_database.py        # Seed data script
│   └── README.md               # Backend documentation
│
├── src/                        # Frontend (Quasar + Vue 3)
│   ├── pages/                  # All UI pages
│   ├── stores/                 # Pinia stores
│   │   ├── auth-store.ts       # ⚠️ Needs integration
│   │   ├── project-store.ts    # ⚠️ Can migrate to API
│   │   └── mock-data.ts        # ⚠️ Can remove after migration
│   ├── services/
│   │   └── api.ts              # ✅ API client ready
│   └── composables/
│       └── useApi.ts           # ✅ API composable ready
│
├── docs/
│   ├── AUTH.md                 # Auth system docs
│   ├── QUICK_START.md          # Quick start guide
│   └── BACKEND_INTEGRATION.md  # ✅ NOVÉ - Integration guide
│
├── .env                        # ✅ NOVÉ - Frontend environment
└── README.md                   # Main documentation
```

---

## 🔗 Integrácia Frontend ↔ Backend

### Aktuálny stav:

- ✅ Backend API beží a funguje
- ✅ Frontend má pripravený API client (`api.ts`)
- ✅ Auth store má pripravený kód pre backend (zakomentovaný)
- ⚠️ Frontend stále používa mock dáta

### Čo treba urobiť (voliteľné):

**Pre full integration:**

1. **Update Auth Store** (5 min)
   - Otvor `src/stores/auth-store.ts`
   - Zakomentuj MOCK kód (line ~108-140)
   - Odkomentuj REAL API kód (line ~142-157)

2. **Test login** (2 min)
   - Spusti backend + frontend
   - Prihlás sa s demo účtom
   - Skontroluj Network tab - mali by ísť requesty na `localhost:5000`

3. **Migruj ostatné stores** (20-30 min)
   - Update `project-store.ts` aby používal `api.get('/projects')`
   - Update `team-store.ts` aby používal `api.get('/teams')`
   - Odstráň `mock-data.ts`

**Detailný návod:** Pozri `docs/BACKEND_INTEGRATION.md`

---

## 📊 API Endpointy

### Test pomocou curl

```bash
# Health check
curl http://localhost:5000/api/health

# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"admin@example.com\",\"password\":\"admin123\"}"

# Get projects (with token)
curl http://localhost:5000/api/projects \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Všetky endpointy

Pozri `backend/README.md` pre kompletný zoznam.

---

## 🎯 Ďalšie kroky (voliteľné)

### Pre diplomovú prácu:

- ✅ Backend je pripravený - môžeš exportovať dáta cez API
- ✅ Frontend funguje s mock dátami - môžeš screenshotovať
- ⚡ Integrácia je **voliteľná** - záleží či chceš produkčné nasadenie

### Pre produkčné nasadenie:

1. Integruj frontend s backendom (podľa `BACKEND_INTEGRATION.md`)
2. Testuj všetky features end-to-end
3. Deploy backend (Heroku / Railway / DigitalOcean)
4. Deploy frontend (Vercel / Netlify)
5. Update environment variables pre production

---

## 📚 Dokumentácia

- **Backend API:** `backend/README.md`
- **Integration Guide:** `docs/BACKEND_INTEGRATION.md`
- **Auth System:** `docs/AUTH.md`
- **Quick Start:** `docs/QUICK_START.md`
- **Main README:** `README.md`

---

## 🐛 Troubleshooting

### Backend nefunguje

```bash
cd backend
python create_database.py  # Vytvor databázu
python seed_database.py    # Naplň dáta
python run.py              # Spusti server
```

### CORS errors

- Skontroluj backend `.env` - `CORS_ORIGINS` by malo obsahovať frontend URL
- Reštartuj backend po zmene `.env`

### Database errors

- Skontroluj či PostgreSQL beží
- Verify credentials v `backend/.env`
- Skús znovu vytvoriť databázu: `python create_database.py`

---

## ✨ Zhrnutie

**Backend:** ✅ Kompletne funkčný  
**Frontend:** ✅ Funguje s mock dátami  
**Integrácia:** ⚠️ Pripravená, čaká na aktiváciu

**Time to integrate:** ~30 min  
**Alternative:** Ponechaj mock dáta pre diplomovku, integruj neskôr

---

🎉 **Gratulujem! Backend je hotový a pripravený na použitie!** 🎉

Ak máš otázky alebo potrebuješ pomoc s integráciou, daj vedieť! 💪
