# 🚀 Quick Start Guide - Authentication System

## Spustenie aplikácie

```bash
# Install dependencies
npm install

# Run development server
npm run dev
```

Aplikácia beží na: `http://localhost:9000` (alebo iný port podľa Quasar config)

---

## 🔐 Prvé prihlásenie

Keď prvýkrát otvoríš aplikáciu, budeš presmerovaný na **Login Page** (`/login`).

### Demo účty (fungujú hneď):

| Role      | Email                 | Password   | Prístup                             |
| --------- | --------------------- | ---------- | ----------------------------------- |
| Admin     | admin@example.com     | admin123   | Plný prístup k všetkému             |
| Manager   | manager@example.com   | manager123 | Project management + experimentácia |
| Developer | developer@example.com | dev123     | Základné funkcie projektu           |

**Tip:** Na login stránke je expansion panel "Demo Accounts" s quick login buttonmi - stačí kliknúť na "Use".

---

## 📖 Navigácia v aplikácii

Po prihlásení uvidíš **MainLayout** so sidebar menu:

### 1. **Main Navigation**

- 🏠 Dashboard - prehľad projektov
- 📁 Projects - správa projektov
- 👥 Team - tímové zdroje
- 📊 Workload - cross-project zaťaženie

### 2. **Project Management**

- 🌳 PERT Analysis - kritické cesty
- 👔 RACI Matrix - zodpovednosti
- 📅 Gantt Chart - timeline
- ⚡ **PERT + RACI Integration** ← **JADRO DIPLOMOVKY**
- 🔄 **Requirement Changes** ← **AUTO-ADAPTÁCIA**

### 3. **Research & Analytics**

- 🧪 Experiments - výskumné testy
- 📈 Analytics - metriky
- 🔀 Comparisons - porovnania metodík
- 📄 Reports - exporty

### 4. **User Menu** (pravý horný roh)

- 👤 Profile - user profile
- 🔐 Role badge - aktuálna rola
- 🚪 Logout - odhlásenie

---

## 🎯 Testovanie kľúčových funkcií

### ✅ 1. PERT + RACI Integration

**Kde:** Menu → PERT + RACI Integration

**Čo testovať:**

1. Vyber projekt (napr. "Mobile App")
2. Nastav RACI váhy (R: 0.6, A: 0.45, C: 0.3, I: 0.05)
3. Klikni **"Run Optimization"**
4. Pozri before/after metrics:
   - Total Duration
   - Workload Balance
   - Critical Path Score

**Výsledok:** Uvidíš vizualizáciu, ako RACI optimalizácia upravuje PERT durácie.

---

### ✅ 2. Requirement Changes Simulator

**Kde:** Menu → Requirement Changes

**Čo testovať:**

1. Vyber projekt (napr. "Mobile App")
2. Nastav:
   - Change Type: "Add new task"
   - Number of Changes: 3
   - Adaptation Strategy: "Balanced"
3. Klikni **"Run Simulation"**
4. Pozri:
   - Adaptation Time (< 5s)
   - Improvement Rate
   - Before/After charts (Duration, Workload, Balance)

**BONUS: Batch Simulation**

1. Zapni "Batch Mode"
2. Nastav Batch Count: 10
3. Klikni **"Run Batch Simulation"**
4. Pozri agregované štatistiky:
   - Average Adaptation Time
   - Success Rate
   - Average Improvement
5. Export výsledky (JSON)

**Výsledok:** Demonštrácia automatickej adaptácie na zmeny požiadaviek v real-time.

---

### ✅ 3. Experiments

**Kde:** Menu → Experiments

**Čo testovať:**

1. Pozri zoznam 5 experimentov
2. Rozklikni "PERT+RACI vs Traditional Planning" (Completed)
3. Pozri:
   - Hypothesis
   - Methodology
   - Results: **+28% improvement, 93% confidence**
4. Export:
   - Klikni "Export" na experimente → JSON
   - Klikni "Export Data" v headeri → JSON + CSV

**Výsledok:** Dáta pre diplomovú prácu (JSON + CSV).

---

### ✅ 4. Analytics

**Kde:** Menu → Analytics

**Čo testovať:**

1. Pozri dashboard s metrikami:
   - Project Efficiency: 85%
   - PERT Accuracy: 92%
   - RACI Compliance: 88%
2. Pozri grafy:
   - Efficiency Over Time
   - Duration Accuracy
   - Team Workload Distribution
3. Pozri insights & recommendations

**Výsledok:** Performance insights pre optimalizáciu.

---

### ✅ 5. Comparisons

**Kde:** Menu → Comparisons

**Čo testovať:**

1. Compare methodologies:
   - Traditional PERT
   - PERT + RACI
   - PERT + RACI + Optimized
2. Pozri metriky pre každý approach:
   - Average Duration
   - Accuracy Rate
   - Team Satisfaction
   - Adaptation Time
3. Pozri visual comparison charts

**Výsledok:** Objektívne porovnanie tradičných vs. inovatívnych prístupov.

---

## 👤 Testovanie User Management

### Profile Page

**Kde:** User Menu → Profile

**Čo testovať:**

1. Zmeň name: "John Doe" → "Jane Doe"
2. Klikni **"Save Changes"**
3. Refresh stránku → zmena persistuje
4. Pozri Role badge (Admin/Manager/Developer)
5. Skús zmeniť heslo (UI dialog)
6. Logout

**Výsledok:** User profil funguje, zmeny sa ukladajú do localStorage.

---

### Registration

**Kde:** Login Page → "Sign up" link → `/register`

**Čo testovať:**

1. Registruj nového usera:
   - Name: "Test User"
   - Email: "test@example.com"
   - Password: "test123"
   - Confirm Password: "test123"
   - ✅ I agree to Terms...
2. Klikni **"Create Account"**
3. Automaticky prihlásený → redirect na Dashboard
4. Pozri user menu → "Test User"

**Výsledok:** Nový user vytvorený, automaticky prihlásený (mock mode).

---

## 🔒 Testovanie Route Guards

### Protected Routes

**Čo testovať:**

1. Odhlás sa (Logout)
2. Manuálne zadaj URL: `http://localhost:9000/#/projects`
3. **Očakávané:** Redirect na `/login?redirect=/projects`
4. Prihlás sa
5. **Očakávané:** Redirect späť na `/projects`

**Výsledok:** Protected routes fungujú správne.

---

## 📊 Export dát pre diplomovku

### Experiments Export

**Kde:** Menu → Experiments → "Export Data"

**Čo exportovať:**

1. Individual experiment (JSON)
2. All experiments (JSON + CSV)

**Výsledok:**

- `experiment_<id>.json`
- `all_experiments.json`
- `all_experiments.csv`

### Batch Simulation Export

**Kde:** Menu → Requirement Changes → Batch Mode → "Export Batch Results"

**Čo exportovať:**

1. Batch statistics (JSON)

**Výsledok:**

- `batch_results_<timestamp>.json`

---

## 🛠️ Ako postupovať ďalej

### Pre diplomovú prácu (bez backendu):

✅ **Všetko funguje s mock dátami**

1. Použi demo účty
2. Testuj všetky funkcie
3. Exportuj dáta (JSON + CSV)
4. Dokumentuj výsledky
5. Screenshoty pre diplomovku

### Pre produkčné nasadenie (s backendom):

📋 **Pripravené na integráciu**

1. Vytvor backend API (Flask/Django/Node.js)
2. Implementuj endpointy podľa `docs/AUTH.md`
3. Nastav `.env` file:
   ```
   VITE_API_BASE_URL=http://localhost:5000/api
   ```
4. V `src/stores/auth-store.ts`:
   - Zakomentuj MOCK kód
   - Odkomentuj REAL API kód
5. Test login/logout flow
6. Deploy 🚀

---

## ❓ Troubleshooting

### "Nemôžem sa prihlásiť"

- Skontroluj email/password (case-sensitive)
- Demo účty sú v tabuľke vyššie
- Použi quick login buttony v expansion paneli

### "Token not persisting"

- Skontroluj "Remember me" checkbox
- Clear browser localStorage/sessionStorage
- Hard refresh (Ctrl + Shift + R)

### "Route redirect loop"

- Clear browser cache
- Logout a znova login
- Check developer console pre errors

### "Linter errors"

```bash
npm run lint
```

### "Type errors"

```bash
npx vue-tsc --noEmit
```

---

## 📚 Ďalšia dokumentácia

- **`docs/AUTH.md`** - Kompletný auth system dokumentácia
- **`README.md`** - Hlavná dokumentácia projektu
- **Code comments** - všetky súbory majú komentáre

---

## 🎓 Pre diplomovú prácu

### Čo mám hotové:

✅ PERT + RACI integrácia (matematický model)
✅ Automatická adaptácia (requirement changes simulator)
✅ Batch simulation (5-50 scenárov)
✅ Visual comparison charts
✅ Experimentálna platforma (5 experimentov)
✅ Export functionality (JSON + CSV)
✅ Porovnávanie metodík
✅ Analytics & reporting
✅ **Authentication system (ready for backend)**

### Čo môžem zdokumentovať:

📊 Výsledky experimentov (+28%, +43% improvement)
📈 Performance metriky (adaptation < 5s)
📉 Porovnania (Traditional vs. PERT+RACI)
🧪 Batch testing výsledky
📄 Export dát pre štatistiku

---

**Enjoy! 🎉**
