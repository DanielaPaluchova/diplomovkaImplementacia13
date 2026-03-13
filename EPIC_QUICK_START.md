# Epic Functionality - Quick Start Guide

## 🚀 Rýchly Start

### 1. Spustenie Migrácie

```bash
cd backend
python migrations/add_epic_functionality.py
```

Zadaj **yes** pre potvrdenie migrácie.

### 2. Seed Testovacích Dát (Voliteľné)

```bash
# Pre projekt s ID=1
python backend/seed_epics.py 1
```

### 3. Spustenie Aplikácie

**Backend:**
```bash
cd backend
python run.py
```

**Frontend:**
```bash
cd quasar-project
npm install  # ak ešte nebolo spustené
quasar dev
```

### 4. Používanie Epic Funkcionality

1. **Navigácia na Epic Management:**
   - Otvor projekt detail
   - Klikni na tlačidlo "Epics" alebo prejdi na `/projects/:id/epics`

2. **Vytvorenie Epicu:**
   - Klikni "Create Epic"
   - Vyplň formulár (name, description, PERT estimates, business value, atď.)
   - Voliteľne pridaj dependencies na iné epics
   - Klikni "Create Epic"

3. **Priradenie Tasku k Epicu:**
   - Pri vytváraní/editácii tasku nájdi sekciu "Epic (Optional)"
   - Vyber epic zo zoznamu
   - Ulož task

4. **Zobrazenie PERT Diagramu:**
   - Na Epics page klikni "View PERT Diagram"
   - Môžeš drag&drop epics, zoom in/out, a pan po diagrame

5. **Critical Path Calculation:**
   - Na Epics page klikni "Calculate Critical Path"
   - Zobrazí sa project duration a critical path medzi epicmi

## 📁 Implementované Súbory

### Backend
- ✅ `backend/app/models/epic.py` - Epic model
- ✅ `backend/app/models/task.py` - Updated (pridané epic_id)
- ✅ `backend/app/routes/epics.py` - Epic API endpoints
- ✅ `backend/migrations/add_epic_functionality.py` - Databázová migrácia
- ✅ `backend/seed_epics.py` - Seed script pre testové dáta

### Frontend
- ✅ `src/stores/epic-store.ts` - Epic Pinia store
- ✅ `src/pages/EpicsPage.vue` - Epic management page
- ✅ `src/pages/EpicPertDiagramPage.vue` - Epic PERT diagram
- ✅ `src/components/EpicDialog.vue` - Epic create/edit dialog
- ✅ `src/pages/ProjectDetailPage.vue` - Updated (epic selector v task dialógoch)
- ✅ `src/stores/project-store.ts` - Updated (pridané epicId do Task interface)
- ✅ `src/router/routes.ts` - Updated (pridané epic routes)

## 🔑 Kľúčové Features

### Epic Management
- ✅ CRUD operácie pre epics
- ✅ PERT estimates pre strategické plánovanie
- ✅ Dependencies medzi epicmi
- ✅ Business value tracking
- ✅ Target release planning
- ✅ Status tracking (not_started, in_progress, completed)

### Epic-Task Integration
- ✅ Voliteľné priradenie tasku k epicu
- ✅ Task môže existovať bez epicu (backward compatible)
- ✅ Epic selector v task create/edit dialógoch
- ✅ Cascade delete: zmazanie epicu neovplyvní tasky

### PERT Analysis
- ✅ Epic PERT diagram s dependencies
- ✅ Critical path calculation pre epics
- ✅ Drag & drop positioning
- ✅ Zoom a pan funkcionalita
- ✅ Critical path visualization

## 📊 API Endpoints

```
GET    /api/projects/<id>/epics                    - List epics
POST   /api/projects/<id>/epics                    - Create epic
GET    /api/projects/<id>/epics/<epic_id>          - Get epic detail
PUT    /api/projects/<id>/epics/<epic_id>          - Update epic
DELETE /api/projects/<id>/epics/<epic_id>          - Delete epic
GET    /api/projects/<id>/epics/critical-path      - Calculate critical path
```

## 🧪 Testing Checklist

- [ ] Spustená migrácia úspešne
- [ ] Vytvorený aspoň 1 epic
- [ ] Pridané dependencies medzi epicmi
- [ ] Priradený task k epicu
- [ ] Zobrazený PERT diagram
- [ ] Vypočítaný critical path
- [ ] Zmazaný epic (tasky zostali)
- [ ] Existujúce tasky fungujú bez epics

## 📖 Dokumentácia

Detailná dokumentácia: `backend/EPIC_IMPLEMENTATION.md`

## 💡 Dôležité Poznámky

1. **Epic je VOLITEĽNÝ** - všetky existujúce funkcie fungujú bez epics
2. **Žiadne breaking changes** - existujúce tasky a projekty fungujú ako predtým
3. **Epic ≠ Task** - epics sú samostatné plánovacie entity
4. **Strategické plánovanie** - epics sú pre long-term planning (mesiace), nie daily/weekly
5. **Sprint planning ignoruje epics** - sprint planning pracuje len s taskami

## 🆘 Support

Ak narazíš na problémy:
1. Skontroluj `backend/EPIC_IMPLEMENTATION.md` pre troubleshooting
2. Overiť databázové pripojenie
3. Skontroluj backend/frontend logs
4. Overiť, že migrácia prebehla úspešne

## 🎯 Príklad Workflow

```
1. Vytvor Epic: "User Authentication" (BV: 100)
2. Vytvor Epic: "User Profile" (BV: 80, depends on Epic 1)
3. Vytvor Epic: "Dashboard" (BV: 90, depends on Epic 1)
4. Vytvor tasky a priraď ich k epicum
5. Zobraz PERT diagram a critical path
6. Trackuj progress a upravuj status epics
```

Happy planning! 🚀
