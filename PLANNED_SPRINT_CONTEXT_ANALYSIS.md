# Komplexná analýza: Kde riešiť PLANNED sprints

## Prehľad stránok používajúcich sprints

### ✅ 1. **Smart Sprint Planning** (`SmartSprintPlanningPage.vue`)
**Účel:** AI-driven plánovanie sprintov

**Aktuálny stav:**
- ✅ Vytvára PLANNED sprints
- ✅ Detekuje existing planned sprint
- ✅ Blokuje vytvorenie druhého planned sprintu
- ✅ Umožňuje Start/Delete planned sprintu
- ✅ Informuje o existing active sprinte

**Planned sprints:** **VYRIEŠENÉ** ✅

---

### ✅ 2. **Project Detail Page** (`ProjectDetailPage.vue`)
**Účel:** Prehľad projektu, Backlog, Sprint Management, Kanban

**Aktuálny stav:**
- ✅ Expandable Planned Sprints
- ✅ Drag & Drop do planned sprintov
- ✅ Start/Edit/Delete planned sprintov
- ✅ Jednoznačné UI pre planned/active/completed

**Planned sprints:** **VYRIEŠENÉ** ✅

---

### 🟡 3. **PERT + RACI Integration** (`PertRaciOptimizationPage.vue`)
**Účel:** Analýza času (PERT) + zodpovednosti (RACI)

**Čo robí:**
```javascript
// Tab: "ACTIVE SPRINT"
const activeSprintTasks = computed(() => {
  if (!activeSprint.value) return [];
  return tasks.filter(task => task.sprintId === activeSprint.id);
});

// Vypočítava:
- PERT duration (optimistic, most likely, pessimistic)
- Adjusted duration s RACI weights
- Workload per member v ACTIVE sprinte
- Cross-project workload (LEN active sprints)
```

**Otázka:** Má zmysel pridať tab "PLANNED SPRINT"?

**Odpoveď:** 🟢 **ÁNO**, má zmysel!
- User chce **naplánovať** PERT odhady a RACI assignments **pred** štartom sprintu
- "Planned Sprint" tab by umožnil **preview** adjusted duration a workload
- Pomohlo by to rozhodnúť či sprint štartovať alebo ešte upraviť

**Implementácia:**
```vue
<!-- Pridať nový tab -->
<q-tab name="planned" label="Planned Sprint" />

<q-tab-panel name="planned">
  <!-- Rovnaké tabuľky ako Active Sprint, ale pre planned sprint -->
  <!-- Umožní preview PERT/RACI analýzy pred štartom -->
</q-tab-panel>
```

---

### 🟡 4. **Requirement Change Impact** (`RequirementChangePage.vue`)
**Účel:** Analýza dopadu zmien v projektových požiadavkách

**Čo robí:**
```javascript
const activeSprint = sprints.find(s => s.status === 'active');

// Vypočítava workload z ACTIVE sprint tasks
// Simuluje "what-if" scenáre pri zmenách requirements
```

**Otázka:** Má zmysel pridať podporu pre planned sprints?

**Odpoveď:** 🟢 **ÁNO**, má zmysel!
- User môže chcieť simulovať **"čo ak zmením requirements pred štartom planned sprintu"**
- Užitočné pre decision-making pred commit

**Implementácia:**
```vue
<!-- Pridať výber sprintu -->
<q-select 
  v-model="selectedSprintId"
  :options="[
    { label: 'Active Sprint', value: activeSprint?.id },
    { label: 'Planned Sprint', value: plannedSprint?.id },
  ]"
/>

<!-- Analyzovať vybraný sprint (active alebo planned) -->
```

---

### 🟡 5. **Workload Dashboard** (`WorkloadDashboardPage.vue`)
**Účel:** Cross-project workload monitoring pre team members

**Čo robí:**
```javascript
const activeSprintsOverview = computed(() => {
  return projects.map(project => {
    const activeSprint = getActiveSprint(project.id);
    // Zobrazuje workload z ACTIVE sprintov
  });
});
```

**Otázka:** Má zmysel pridať planned sprints?

**Odpoveď:** 🟢 **ÁNO**, ale **voliteľne**!
- User môže chcieť vidieť **"forecasted workload"** ak štartne planned sprint
- Užitočné pre capacity planning

**Implementácia:**
```vue
<!-- Pridať toggle -->
<q-checkbox 
  v-model="includePlannedSprints"
  label="Include planned sprints in forecast"
/>

<!-- Filter -->
const workloadSprints = projects.flatMap(p => 
  p.sprints.filter(s => 
    s.status === 'active' || 
    (includePlannedSprints.value && s.status === 'planned')
  )
);
```

---

### ✅ 6. **Critical Path** (`CriticalPathPage.vue`)
**Účel:** Epic dependencies, kritická cesta

**Otázka:** Používa sprints?

**Potrebujem skontrolovať:**
```javascript
// Skontrolujte či Critical Path používa sprints alebo len epics
```

---

### ✅ 7. **PERT Analysis** (`PertAnalysisPage.vue`)
**Účel:** Samostatná PERT analýza času

**Stav:** ✅ **Nepoužíva sprints**
- Analyzuje **všetky tasky v projekte** (bez ohľadu na sprint)
- Vypočítava PERT estimates, CV, uncertainty risks

**Planned sprints:** **Neriešiť** - už funguje správne ✅

---

### ✅ 8. **RACI Matrix** (`RaciMatrixPage.vue`)
**Účel:** Samostatná RACI matrica zodpovedností

**Stav:** ✅ **Nepoužíva sprints**
- Analyzuje **všetky tasky v projekte** (bez ohľadu na sprint)
- Zobrazuje RACI assignments, overload warnings

**Planned sprints:** **Neriešiť** - už funguje správne ✅

---

### ✅ 9. **Epic PERT Diagram** (`EpicPertDiagramPage.vue`)
**Účel:** PERT diagram pre epics

**Stav:** ✅ **Pracuje s epics, nie sprints**

**Planned sprints:** **Neriešiť** - nie je relevantné ✅

---

## Backend analýza

### ✅ 1. **Smart Sprint Planner** (`services/smart_sprint_planner.py`)
**Stav:** ✅ Už upravené - vytvára planned sprints

### ✅ 2. **Workload Calculator** (`utils/workload_calculator.py`)
**Stav:** ✅ Správne - počíta LEN active sprints (nie planned)

### ✅ 3. **PERT/RACI Analyzer** (`services/pert_raci_analyzer.py`)
**Stav:** ✅ Správne - nezávislý od sprint statusu

---

## 📊 Sumár: Kde riešiť PLANNED sprints

### ✅ **HOTOVO** (Core Workflow):
1. ✅ **Smart Sprint Planning** - Vytvára planned sprints, validácie
2. ✅ **Project Detail Page** - Backlog, drag&drop, start/edit/delete

### 🟢 **ODPORÚČAM PRIDAŤ** (High Value):
3. 🟢 **PERT + RACI Integration** - Tab "Planned Sprint" (preview pred štartom)
4. 🟢 **Workload Dashboard** - Forecast toggle (capacity planning)

### 🟡 **NICE-TO-HAVE** (Optional):
5. 🟡 **Requirement Changes** - Sprint selector (what-if pre planned)

### ⚪ **NETREBA** (Already Working / Not Relevant):
6. ✅ **PERT Analysis** - Analyzuje všetky tasky (sprint-agnostic)
7. ✅ **RACI Matrix** - Analyzuje všetky tasky (sprint-agnostic)
8. ✅ **Critical Path** - Epic dependencies (sprint-agnostic)
9. ⚪ **Burndown** - Iba pre ACTIVE (tracking progress)
10. ⚪ **Velocity** - Iba pre COMPLETED (história)

### 🔵 Nízka priorita / Neriešiť:
6. ✅ **Critical Path** (`CriticalPathPage.vue`) - Používa epics, nie sprints
7. ⚪ **Burndown Chart** - Neexistuje ešte (bude len pre ACTIVE)
8. ⚪ **Velocity** - Neexistuje ešte (bude len pre COMPLETED)
9. ⚪ **Sprint Report** - Neexistuje ešte (bude len pre COMPLETED)

---

## 🎯 Use Cases: Prečo pridať podporu pre PLANNED sprints?

### Scenár 1: Preview pred štartom
```
User Story:
"Chcem vidieť PERT adjusted duration a workload distribution 
 PRED tým ako štartnem planned sprint, aby som vedel či ho 
 treba ešte upraviť."

Riešenie:
→ PERT + RACI Integration: Tab "Planned Sprint"
→ Zobrazí adjusted duration, workload per member
→ Ak je workload vysoký → upraví RACI assignments → regeneruje
```

### Scenár 2: Capacity Planning
```
User Story:
"Mám 2 projekty s planned sprintami. Chcem vedieť koľko 
 workloadu bude mať môj team AK ich oba štartnem."

Riešenie:
→ Workload Dashboard: Toggle "Include planned sprints"
→ Zobrazí Current Workload + Forecasted Workload
→ Rozhodne či môže štartovať oba alebo len jeden
```

### Scenár 3: What-If Analysis
```
User Story:
"Chcem pridať nový requirement do planned sprintu. 
 Aký bude impact na workload a duration?"

Riešenie:
→ Requirement Changes: Sprint selector "Planned Sprint"
→ Simuluje pridanie nového tasku
→ Zobrazí nový workload/duration pred commitom
```

---

## Vizuálny prehľad

```
┌─────────────────────────────────────────────────────────────────┐
│                    SPRINT LIFECYCLE                              │
├─────────────────────────────────────────────────────────────────┤
│  BACKLOG → [PLANNED] → [ACTIVE] → [COMPLETED]                   │
│              ↑           ↑            ↑                          │
│              │           │            │                          │
│         Preview here  Tracking   History                         │
└─────────────────────────────────────────────────────────────────┘

Ktoré stránky by mali podporovať [PLANNED] sprints?

✅ HOTOVO:
  ├─ Smart Sprint Planning ← Vytvára planned sprints
  └─ Project Detail Page   ← Spravuje planned sprints

🟢 ODPORÚČAM PRIDAŤ:
  ├─ PERT + RACI Integration ← Preview adjusted duration pred štartom
  ├─ Workload Dashboard      ← Forecast workload (optional toggle)
  └─ Requirement Changes     ← What-if scenáre pre planned sprint

⚪ NETREBA:
  ├─ PERT Analysis      ← Analyzuje všetky tasky (bez sprint context)
  ├─ RACI Matrix        ← Analyzuje všetky tasky (bez sprint context)
  ├─ Critical Path      ← Používa epics, nie sprints
  ├─ Burndown Chart     ← Len pre ACTIVE (tracking progress)
  └─ Velocity/Report    ← Len pre COMPLETED (história)
```

---

## Detailné odporúčania

### 🟢 1. PERT + RACI Integration - "Planned Sprint" Tab

**Prínos:**
- User vidí **adjusted duration** a **workload** pred štartom
- Môže upraviť RACI assignments aby znížil workload
- Môže rozhodnúť či sprint štartovať alebo ešte upraviť

**Implementácia:**
```vue
<q-tabs v-model="activeTab">
  <q-tab name="active" label="Active Sprint" />
  <q-tab name="planned" label="Planned Sprint" />   ← NOVÝ TAB
  <q-tab name="future" label="Future & Backlog" />
</q-tabs>

<q-tab-panel name="planned">
  <!-- Rovnaká logika ako Active Sprint tab -->
  <!-- Len filtruje tasky z planned sprintu -->
  <div v-if="!plannedSprint">
    <q-banner>No planned sprint. Create one in Smart Planning.</q-banner>
  </div>
</q-tab-panel>
```

---

### 🟢 2. Workload Dashboard - Forecast Toggle

**Prínos:**
- User vidí **forecasted workload** ak štartne planned sprint
- Pomôže s capacity planning
- Voliteľné (toggle on/off)

**Implementácia:**
```vue
<q-checkbox 
  v-model="includeePlannedInForecast"
  label="Show forecast with planned sprints"
/>

const workloadData = computed(() => {
  return members.map(member => {
    const activeWorkload = getActiveSprintWorkload(member);
    const plannedWorkload = includePlannedInForecast.value 
      ? getPlannedSprintWorkload(member) 
      : 0;
    
    return {
      current: activeWorkload,
      forecast: activeWorkload + plannedWorkload
    };
  });
});
```

---

### 🟡 3. Requirement Changes - Sprint Selector

**Prínos:**
- What-if analýza pre planned sprint
- "Čo ak zmením requirements pred štartom?"

**Implementácia:**
```vue
<q-select
  v-model="selectedSprintType"
  :options="[
    { label: 'Active Sprint', value: 'active' },
    { label: 'Planned Sprint', value: 'planned' },
  ]"
/>
```

---

## Odporúčanie pre implementáciu

**Priorita 1 (high impact, low effort):**
1. **PERT + RACI Integration** - Pridať "Planned Sprint" tab
   - Effort: Medium (copy existing logic)
   - Impact: High (preview pred štartom)

**Priorita 2 (medium impact, medium effort):**
2. **Workload Dashboard** - Pridať forecast toggle
   - Effort: Medium
   - Impact: Medium (capacity planning)

**Priorita 3 (nice-to-have):**
3. **Requirement Changes** - Sprint selector
   - Effort: Low
   - Impact: Low (edge case use)

---

## Čo NERIEŠIŤ

❌ **Burndown Chart** - má zmysel len pre ACTIVE sprint (tracking denného progressu)
❌ **Velocity Report** - historické dáta z COMPLETED sprintov
❌ **Sprint Retrospective** - len pre COMPLETED sprints

---

## Aktuálny stav (po dnešných fixoch)

### ✅ Core Workflow (HOTOVO):
- Vytvoriť planned sprint (Smart Planning + Manual)
- Pridávať/odoberať tasky (Drag & Drop)
- Editovať planned sprint
- Štartovať planned sprint → active
- Validácia: max 1 planned per project
- Validácia: max 1 active per project

### 🐛 Bugy opravené dnes:
1. ✅ Smart Planning: Obsolete "close active sprint" warning
2. ✅ Smart Planning: Pridaný "existing planned sprint" warning
3. ✅ Backend: Validácia pri update_sprint (nemožno 2 active)
4. ✅ Frontend: Validácia pred startExistingPlannedSprint
5. ✅ UX: Success notification zobrazená pred reload (nie po)

---

## 🚀 Action Plan (ak chceš implementovať)

### Krok 1: PERT + RACI Integration (HIGH PRIORITY)
```bash
Súbor: src/pages/PertRaciOptimizationPage.vue

Zmeny:
1. Pridať computed: const plannedSprint = ...
2. Pridať computed: const plannedSprintTasks = ...
3. Pridať tab: <q-tab name="planned" label="Planned Sprint" />
4. Pridať panel: <q-tab-panel name="planned"> ... </q-tab-panel>
5. Copy logiku z "Active Sprint" tab, len zmeniť filter

Effort: ~2-3 hodiny
Impact: HIGH (preview pred štartom sprintu)
```

### Krok 2: Workload Dashboard (MEDIUM PRIORITY)
```bash
Súbor: src/pages/WorkloadDashboardPage.vue

Zmeny:
1. Pridať toggle: includePlannedSprints
2. Upraviť computed workload functions
3. Pridať "Forecast" column do tabuliek
4. Pridať legend: "Current (Active) | Forecast (+Planned)"

Effort: ~1-2 hodiny
Impact: MEDIUM (capacity planning)
```

### Krok 3: Requirement Changes (LOW PRIORITY)
```bash
Súbor: src/pages/RequirementChangePage.vue

Zmeny:
1. Pridať sprint selector: active/planned
2. Upraviť workload calculations
3. Filter tasks podľa vybraného sprintu

Effort: ~1 hodina
Impact: LOW (edge case)
```

---

## 📋 Checklist pre implementáciu

### PERT + RACI Integration - "Planned Sprint" Tab
- [ ] Pridať `const plannedSprint = computed(...)`
- [ ] Pridať `const plannedSprintTasks = computed(...)`
- [ ] Pridať `<q-tab name="planned">`
- [ ] Duplikovať "Active Sprint" panel → zmeniť na "Planned"
- [ ] Zmeniť filter: `task.sprintId === plannedSprint.value.id`
- [ ] Pridať banner: "No planned sprint yet"
- [ ] Test: Vytvoriť planned sprint → vidieť PERT/RACI analýzu

### Workload Dashboard - Forecast Toggle
- [ ] Pridať `const includePlannedSprints = ref(false)`
- [ ] Upraviť `getSprintWorkload()` - pridať parameter `includeP Planned`
- [ ] Pridať "Forecast" column do Member Workload table
- [ ] Pridať color coding: grey (current), blue (forecast)
- [ ] Test: Toggle on → vidieť forecasted workload

### Requirement Changes - Sprint Selector
- [ ] Pridať `const selectedSprintType = ref<'active'|'planned'>('active')`
- [ ] Pridať `<q-select>` pre výber sprintu
- [ ] Upraviť workload calculation functions
- [ ] Test: Select "Planned" → simulovať change
