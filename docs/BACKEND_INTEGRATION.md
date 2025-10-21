# 🔗 Backend Integration Guide

Návod na prepojenie frontendu s backendom.

## ✅ Backend Setup (HOTOVÉ)

Backend je pripravený a beží na `http://localhost:5000`

### Čo je hotové:

- ✅ Flask + PostgreSQL backend
- ✅ PostgreSQL databáza `diplonovka_db` vytvorená
- ✅ Seed dáta naplnené (users, teams, projects, experiments)
- ✅ API endpointy implementované (auth, projects, teams, tasks, experiments, analytics)
- ✅ JWT authentication
- ✅ CORS configured pre frontend
- ✅ Server beží na port 5000

---

## 🔧 Frontend Integration

### Krok 1: Nastav Frontend Environment

Vytvor `.env` súbor v **root** projekte (vedľa `package.json`):

```env
# Backend API URL
VITE_API_BASE_URL=http://localhost:5000/api
```

### Krok 2: Update Auth Store

Otvor `src/stores/auth-store.ts` a **odkomentuj REAL API kód**, **zakomentuj MOCK kód**:

#### Login funkcia (line ~103-164):

**Zakomentuj MOCK kód:**

```typescript
// MOCK - comment this out
/*
await new Promise((resolve) => setTimeout(resolve, 1000));

const foundUser = mockUsers.find(...);
if (!foundUser) {
  error.value = 'Invalid email or password';
  return false;
}

const mockToken = `mock_jwt_${foundUser.id}_${Date.now()}`;
const { password: _password, ...userWithoutPassword } = foundUser;
user.value = userWithoutPassword;
token.value = mockToken;

if (credentials.rememberMe) {
  localStorage.setItem('auth_token', mockToken);
  localStorage.setItem('auth_user', JSON.stringify(userWithoutPassword));
} else {
  sessionStorage.setItem('auth_token', mockToken);
  sessionStorage.setItem('auth_user', JSON.stringify(userWithoutPassword));
}

return true;
*/
```

**Odkomentuj REAL API kód:**

```typescript
// REAL API - uncomment this
import { api } from 'src/services/api';

const response = await api.post('/auth/login', {
  email: credentials.email,
  password: credentials.password,
});

user.value = response.user;
token.value = response.token;

if (credentials.rememberMe) {
  localStorage.setItem('auth_token', token.value);
  localStorage.setItem('auth_user', JSON.stringify(user.value));
} else {
  sessionStorage.setItem('auth_token', token.value);
  sessionStorage.setItem('auth_user', JSON.stringify(user.value));
}

return true;
```

#### Register funkcia (line ~170-231):

**Zakomentuj MOCK kód:**

```typescript
// MOCK - comment this out
/*
await new Promise((resolve) => setTimeout(resolve, 1000));

if (mockUsers.some((u) => u.email === data.email)) {
  error.value = 'Email already exists';
  return false;
}

const newUser: User = { ... };
mockUsers.push({ ...newUser, password: data.password });
const mockToken = `mock_jwt_${newUser.id}_${Date.now()}`;
user.value = newUser;
token.value = mockToken;

localStorage.setItem('auth_token', mockToken);
localStorage.setItem('auth_user', JSON.stringify(newUser));

return true;
*/
```

**Odkomentuj REAL API kód:**

```typescript
// REAL API - uncomment this
const response = await api.post('/auth/register', {
  email: data.email,
  password: data.password,
  name: data.name,
  role: data.role,
});

user.value = response.user;
token.value = response.token;

localStorage.setItem('auth_token', token.value);
localStorage.setItem('auth_user', JSON.stringify(user.value));

return true;
```

#### UpdateProfile funkcia (line ~269-301):

**Zakomentuj MOCK kód, odkomentuj REAL API kód** (podobne ako vyššie).

### Krok 3: Test Backend Integration

1. **Backend musí bežať:**

   ```bash
   cd backend
   .\venv\Scripts\Activate.ps1
   python run.py
   ```

2. **Frontend spusti:**

   ```bash
   npm run dev
   ```

3. **Otestuj login:**
   - Otvor `http://localhost:9000` (alebo port ktorý ti Quasar ukáže)
   - Prihlás sa pomocou demo účtu:
     - Email: `admin@example.com`
     - Password: `admin123`

4. **Ak login funguje, uvidíš:**
   - ✅ JWT token v localStorage
   - ✅ User info v auth store
   - ✅ Redirect na dashboard
   - ✅ Backend API volania v Network tab (F12)

---

## 🔄 Migrácia Mock Dát na Backend

Po úspešnom pripojení môžeš nahradiť mock stores skutočným API:

### Project Store

**Aktuálne:** Mock dáta v `src/stores/project-store.ts`  
**Nahraď:** API volania cez `api.get('/projects')`

```typescript
// Namiesto:
const projects = ref<Project[]>([...hardcoded data...]);

// Použi:
const projects = ref<Project[]>([]);

async function fetchProjects() {
  const response = await api.get('/projects?details=true');
  projects.value = response;
}
```

### Team Store

**Aktuálne:** Mock dáta v `src/stores/team-store.ts` (ak existuje)  
**Nahraď:** API volania cez `api.get('/teams')`

### Mock Data Store

**Môžeš vymazať:** `src/stores/mock-data.ts` (po migrácii všetkých dát na backend)

---

## 📡 API Endpoints Ready to Use

### Authentication

```typescript
// Login
await api.post('/auth/login', { email, password });

// Register
await api.post('/auth/register', { email, password, name, role });

// Get current user
await api.get('/auth/me');

// Update profile
await api.put('/auth/profile', { name, avatar });
```

### Projects

```typescript
// Get all projects
await api.get('/projects');

// Get project with details
await api.get('/projects?details=true');

// Get single project
await api.get(`/projects/${projectId}`);

// Create project
await api.post('/projects', projectData);

// Update project
await api.put(`/projects/${projectId}`, updates);

// Delete project
await api.delete(`/projects/${projectId}`);
```

### Teams

```typescript
// Get all team members
await api.get('/teams');

// Create team member
await api.post('/teams', memberData);

// Update team member
await api.put(`/teams/${memberId}`, updates);
```

### Tasks

```typescript
// Get tasks for project
await api.get(`/tasks?project_id=${projectId}`);

// Create task with PERT + RACI
await api.post('/tasks', {
  name: 'Task name',
  projectId: 1,
  pert: { optimistic: 10, mostLikely: 15, pessimistic: 20 },
  raci: { responsible: [1, 2], accountable: 1, consulted: [], informed: [3] }
});

// Bulk update tasks (for PERT/RACI optimization)
await api.post('/tasks/bulk-update', { tasks: [...] });
```

### Experiments

```typescript
// Get all experiments
await api.get('/experiments');

// Get experiment stats
await api.get('/experiments/stats');

// Create experiment (Manager+)
await api.post('/experiments', experimentData);
```

### Analytics

```typescript
// Dashboard metrics
await api.get('/analytics/dashboard');

// PERT+RACI metrics
await api.get('/analytics/pert-raci');

// Workload distribution
await api.get('/analytics/workload');

// Comparison data
await api.get('/analytics/comparison');
```

---

## 🧪 Testing

### Test Backend API Directly

```bash
# Health check
curl http://localhost:5000/api/health

# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123"}'

# Get projects (with token)
curl http://localhost:5000/api/projects \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Test Frontend Integration

1. Open browser DevTools (F12)
2. Go to Network tab
3. Login to app
4. Watch for API calls to `localhost:5000`
5. Check if responses are correct

---

## 🐛 Troubleshooting

### CORS Error

**Problem:** `CORS policy: No 'Access-Control-Allow-Origin'`

**Fix:**

- Check backend `.env` has correct `CORS_ORIGINS`
- Should include `http://localhost:9000` (or your frontend port)
- Restart backend after `.env` change

### 401 Unauthorized

**Problem:** `Invalid or expired token`

**Fix:**

- Token might be expired
- Login again to get new token
- Check if token is being sent in Authorization header

### Connection Refused

**Problem:** `Failed to fetch` or `ERR_CONNECTION_REFUSED`

**Fix:**

- Backend is not running
- Start backend: `python run.py`
- Check if running on correct port (5000)

### Database Error

**Problem:** `Database does not exist`

**Fix:**

```bash
cd backend
python create_database.py
python seed_database.py
```

---

## ✅ Integration Checklist

- [ ] Backend running on port 5000
- [ ] Frontend `.env` created with `VITE_API_BASE_URL`
- [ ] Auth store updated (MOCK commented, REAL uncommented)
- [ ] Test login works
- [ ] Test register works
- [ ] Test protected routes work
- [ ] Check API calls in Network tab
- [ ] Verify JWT token in localStorage
- [ ] Test logout clears token

---

## 🚀 Next Steps

Po úspešnej integrácii autentifikácie:

1. ✅ Migruj Project Store na API volania
2. ✅ Migruj Team Store na API volania
3. ✅ Migruj Research Store (Experiments) na API
4. ✅ Update všetky komponenty aby používali API namiesto mock stores
5. ✅ Odstráň mock-data.ts store
6. ✅ Testuj všetky funkcie end-to-end

---

**Ready for production!** 🎉
