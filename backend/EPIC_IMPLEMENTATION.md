# Epic Functionality Implementation

## Overview

Epic funkcionalita umožňuje strategické plánovanie projektov na vysokej úrovni. Epics sú samostatné plánovacie entity, ktoré môžu obsahovať viaceré tasky a majú vlastné PERT estimates a dependencies.

## Kľúčové vlastnosti

### Epic Features
- ✅ Samostatná entita (nezávislá od taskov)
- ✅ PERT estimates (optimistic, most_likely, pessimistic, expected)
- ✅ Dependencies medzi epicmi
- ✅ Business value a target release
- ✅ Status tracking (not_started, in_progress, completed)
- ✅ PERT diagram position (drag & drop)
- ✅ Critical path calculation pre epics

### Task-Epic Integration
- ✅ Task môže byť voliteľne priradený k epicu (epic_id)
- ✅ Task môže existovať bez epicu (epic_id = null)
- ✅ Cascade delete: ak sa zmaže epic, tasky ostanú (epic_id sa nastaví na NULL)
- ✅ Epic selector v task dialógoch (create/edit)

## Databázová Štruktúra

### Nová Tabuľka: `epics`
```sql
CREATE TABLE epics (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    status VARCHAR(50) NOT NULL DEFAULT 'not_started',
    pert_optimistic FLOAT,
    pert_most_likely FLOAT,
    pert_pessimistic FLOAT,
    pert_expected FLOAT,
    dependencies JSON,
    business_value INTEGER NOT NULL DEFAULT 0,
    target_release VARCHAR(100),
    diagram_position_x FLOAT,
    diagram_position_y FLOAT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);
```

### Zmena v Tabuľke: `tasks`
```sql
ALTER TABLE tasks 
ADD COLUMN epic_id INTEGER NULL,
ADD CONSTRAINT fk_task_epic 
FOREIGN KEY (epic_id) REFERENCES epics(id) ON DELETE SET NULL;
```

## Inštalácia a Migrácia

### 1. Spustenie Migrácie

```bash
cd backend
python migrations/add_epic_functionality.py
```

Migrácia:
- Vytvorí tabuľku `epics`
- Pridá stĺpec `epic_id` do tabuľky `tasks`
- Nastaví ON DELETE SET NULL pre epic_id
- Všetky existujúce tasky budú mať epic_id = NULL

### 2. Seed Data (Voliteľné)

Po migrácii môžete vytvoriť testové epics pre existujúci projekt:

```bash
python backend/seed_epics.py <project_id>

# Príklad:
python backend/seed_epics.py 1
```

Seed script vytvorí:
- 8 realistických epics s dependencies
- Epics majú PERT estimates a business value
- Možnosť automaticky priradiť existujúce tasky do epics

## API Endpoints

### Epic CRUD

```
GET    /api/projects/<project_id>/epics
       - Získať všetky epics pre projekt
       - Query params: include_tasks=true/false

POST   /api/projects/<project_id>/epics
       - Vytvoriť nový epic
       - Body: { name, description, status, pert, dependencies, businessValue, targetRelease }

GET    /api/projects/<project_id>/epics/<epic_id>
       - Získať detail epicu
       - Query params: include_tasks=true/false

PUT    /api/projects/<project_id>/epics/<epic_id>
       - Aktualizovať epic
       - Body: partial epic data

DELETE /api/projects/<project_id>/epics/<epic_id>
       - Zmazať epic (tasky ostanú, epic_id = null)
```

### Epic Critical Path

```
GET    /api/projects/<project_id>/epics/critical-path
       - Vypočítať critical path medzi epicmi
       - Response: { criticalPath: [epic_ids], epicSchedule: {...}, projectDuration }
```

## Frontend Komponenty

### Pages
- **EpicsPage.vue** - Hlavná stránka pre Epic management
  - Zoznam epics s možnosťou create/edit/delete
  - Expandable cards s progress tracking
  - Critical path calculation button
  
- **EpicPertDiagramPage.vue** - PERT diagram pre epics
  - Vizualizácia dependencies medzi epicmi
  - Zvýraznenie critical path
  - Drag & drop positioning

### Components
- **EpicDialog.vue** - Dialog pre vytvorenie/editáciu epicu
  - PERT estimates input
  - Dependencies selector
  - Business value a target release
  
- **Task Dialogs** (ProjectDetailPage.vue)
  - Epic selector v create task dialog
  - Epic selector v edit task dialog

### Store
- **epic-store.ts**
  - CRUD operácie pre epics
  - Critical path calculation
  - Epic position update

## Routing

```typescript
// Epic management page
/projects/:id/epics

// Epic PERT diagram
/projects/:id/epics/pert-diagram
```

## Použitie

### 1. Vytvorenie Epicu

1. Naviguj na projekt detail
2. V navigácii klikni na "Epics" alebo prejdi na `/projects/:id/epics`
3. Klikni "Create Epic"
4. Vyplň:
   - Epic name (required)
   - Description
   - Status (not_started, in_progress, completed)
   - PERT estimates (optimistic, most_likely, pessimistic)
   - Dependencies (iné epics)
   - Business value
   - Target release
5. Klikni "Create Epic"

### 2. Priradenie Tasku k Epicu

1. Otvor task dialog (create alebo edit)
2. Nájdi sekciu "Epic (Optional)"
3. Vyber epic zo zoznamu
4. Ulož task

### 3. Zobrazenie PERT Diagramu

1. Na Epics page klikni "View PERT Diagram"
2. Diagram zobrazí:
   - Všetky epics ako nody
   - Dependencies ako šípky
   - Critical path (červená farba)
3. Môžeš:
   - Zoom in/out
   - Pan po diagrame
   - Drag & drop epics na nové pozície

### 4. Critical Path Calculation

1. Na Epics page klikni "Calculate Critical Path"
2. Zobrazí sa:
   - Project duration
   - Critical path (zoznam epics)
   - Schedule pre každý epic (ES, EF, LS, LF, slack)

## Testing Scenáre

### 1. Základné CRUD Operácie
- ✅ Vytvorenie epicu
- ✅ Úprava epicu
- ✅ Zmazanie epicu
- ✅ Získanie zoznamu epics

### 2. Dependencies
- ✅ Vytvorenie epicu s dependencies
- ✅ Validácia circular dependencies
- ✅ Critical path calculation

### 3. Task-Epic Integrácia
- ✅ Priradenie tasku k epicu
- ✅ Odobranie tasku z epicu (set epic_id = null)
- ✅ Zmazanie epicu neovplyvní tasky

### 4. PERT Diagram
- ✅ Zobrazenie epics
- ✅ Zobrazenie dependencies
- ✅ Zvýraznenie critical path
- ✅ Drag & drop positioning
- ✅ Zoom a pan

### 5. Backward Compatibility
- ✅ Všetky existujúce tasky fungujú bez epics
- ✅ Existujúce API endpoints fungujú bez zmien
- ✅ Sprint planning funguje len s taskami (ignore epics)

## Dôležité Poznámky

1. **Epic je VOLITEĽNÝ** - projekt môže fungovať aj bez epics
2. **Task môže existovať bez epicu** - epic_id = null je validný stav
3. **Epic NIE JE task** - sú to samostatné entity
4. **Epic je pre strategické plánovanie** - nie pre daily/weekly planning
5. **Sprint planning používa len tasky** - epics sú ignorované

## Troubleshooting

### Migrácia zlyhala
```bash
# Check database connection
psql -h localhost -U postgres -d diplomovka_db

# Verify tables exist
\dt

# Manual rollback if needed
python migrations/add_epic_functionality.py
# Then select downgrade option
```

### Epics sa nezobrazujú na frontende
```bash
# Check backend logs
# Verify API endpoint responds
curl http://localhost:5000/api/projects/1/epics

# Check browser console for errors
# Verify epic store is imported correctly
```

### Critical path calculation fails
- Skontroluj, či epics majú PERT estimates
- Overiť, že dependencies sú validné (žiadne circular dependencies)
- Skontroluj backend logs pre error messages

## Príklad Epic Štruktúry

```
Epic 1: User Authentication (BV: 100)
  ├─ Task 1: Login endpoint
  ├─ Task 2: Registration form
  └─ Task 3: Password reset

Epic 2: User Profile (BV: 80) [depends on Epic 1]
  ├─ Task 4: Profile page
  └─ Task 5: Avatar upload

Epic 3: Dashboard (BV: 90) [depends on Epic 1]
  ├─ Task 6: Dashboard layout
  └─ Task 7: Analytics charts

Epic 4: Mobile App (BV: 95) [depends on Epic 1, 2, 3]
  ├─ Task 8: iOS app
  └─ Task 9: Android app
```

## Ďalší Vývoj (Future Enhancements)

- [ ] Epic progress tracking based on completed tasks
- [ ] Epic burndown chart
- [ ] Epic capacity planning
- [ ] Epic templates
- [ ] Epic cloning
- [ ] Export epic roadmap to PDF
- [ ] Epic notifications when status changes
- [ ] Epic comments and attachments
