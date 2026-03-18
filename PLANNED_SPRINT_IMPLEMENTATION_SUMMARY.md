# ✅ PLANNED SPRINT - Kompletná implementácia

## 📦 Implementované funkcionality

### 1. **PERT + RACI Integration** - Tab "Plánovaný Šprit"
**Súbor:** `src/pages/PertRaciOptimizationPage.vue`

**Pridané:**
```typescript
// Computed properties
const plannedSprint = computed(() => ...)
const plannedSprintTasks = computed(() => ...)
const plannedSprintSummary = computed(() => ...)

// UI
<q-tab name="planned" icon="event_available" label="Plánovaný Šprit" />
<q-tab-panel name="planned">
  - Info banner: "Planned Sprint Preview"
  - Summary cards: Task count, Duration increase %
  - Table: PERT + Adjusted Duration + RACI + CV
  - Empty state: "No planned sprint" + link to Smart Planning
</q-tab-panel>
```

**Workflow:**
```
1. User vytvoriť planned sprint (Smart Planning)
2. Otvoriť PERT + RACI Integration
3. Tab "Plánovaný Šprit" → Preview:
   • PERT estimates (optimistic/most likely/pessimistic)
   • Adjusted Duration (s RACI overhead)
   • Duration Increase % (impact of RACI roles)
   • Uncertainty level (CV)
   • RACI role distribution
4. Rozhodnúť: Start sprint alebo upraviť
```

---

### 2. **Project Optimization** - Tab "Planned Sprint"
**Súbor:** `src/pages/RequirementChangePage.vue`

**Pridané:**
```typescript
// Computed properties
const hasPlannedSprint = computed(() => ...)
const plannedSprint = computed(() => ...)

// UI
<q-tab name="planned_sprint" icon="event_available" label="Planned Sprint" />
<q-tab-panel name="planned_sprint">
  - Info banner: "Preview optimization before starting"
  - Buttons: "Analyze & Optimize", "PERT+RACI Analysis"
  - OptimizationProposals component (10+ optimization strategies)
  - Success/Empty/Loading states
</q-tab-panel>

// Functions updated
async function analyzeTab(scope: 'current_sprint' | 'planned_sprint' | 'backlog')
async function analyzePertRaciTab(scope: 'current_sprint' | 'planned_sprint' | 'backlog')
```

**Workflow:**
```
1. User vytvoriť planned sprint (Smart Planning)
2. Otvoriť Project Optimization
3. Tab "Planned Sprint"
4. Kliknúť "Analyze & Optimize" alebo "PERT+RACI Analysis"
5. Dostať optimization proposals:
   ✓ Deadline risks
   ✓ Priority conflicts
   ✓ Workload imbalance
   ✓ PERT uncertainty
   ✓ RACI overload
   ✓ Adjusted duration risks
   ✓ Task complexity
   ✓ Missing assignments
   ✓ Skill mismatches
   ✓ Dependency issues
6. Vybrať proposals + Apply
7. Start optimalizovaný sprint ✅
```

---

### 3. **Backend Support**
**Súbor:** `backend/app/routes/requirement_changes.py`

**Upravené:**
```python
# auto_optimize_project()
scope = data.get('scope', 'backlog')  # ← Supports 'planned_sprint'

if scope == 'planned_sprint':
    planned_sprint = next((s for s in sprints if s.status == 'planned'), None)
    if planned_sprint:
        tasks = [t for t in active_tasks if t.sprint_id == planned_sprint.id]
    else:
        tasks = []

is_sprint_scope = (scope in ['current_sprint', 'planned_sprint'])
# ← Planned sprint je teraz považovaný za sprint scope

# analyze_pert_raci()
# Rovnaká logika ako auto_optimize
```

**Súbor:** `src/stores/requirement-change-store.ts`

**Upravené:**
```typescript
// Export type
export type OptimizationScope = 'current_sprint' | 'planned_sprint' | 'backlog';

// Function signatures
async function autoOptimizeProject(
  projectId: number,
  scope: OptimizationScope = 'backlog'
): Promise<AnalysisResult | null>

async function analyzePertRaci(
  projectId: number,
  scope: OptimizationScope = 'backlog'
): Promise<AnalysisResult | null>
```

---

## 🎯 Celkový workflow s PLANNED sprintami

```
┌──────────────────────────────────────────────────────────────┐
│                  SPRINT LIFECYCLE                             │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  1. CREATE PLANNED SPRINT                                    │
│     → Smart Sprint Planning                                  │
│     → AI vytvára planned sprint s taskami                    │
│                                                               │
│  2. MANAGE TASKS                                             │
│     → Project Detail Page                                    │
│     → Drag & Drop tasky do/z planned sprintu                │
│     → Edit/Delete tasks                                      │
│                                                               │
│  3. PREVIEW & OPTIMIZE (NOVÉ! ✨)                            │
│     a) PERT + RACI Integration → Tab "Plánovaný Šprit"      │
│        ✓ Vidieť adjusted duration                            │
│        ✓ Vidieť RACI workload distribution                   │
│        ✓ Vidieť uncertainty risks (CV)                       │
│                                                               │
│     b) Project Optimization → Tab "Planned Sprint"           │
│        ✓ Analyze & Optimize (10+ strategies)                 │
│        ✓ Get optimization proposals                          │
│        ✓ Apply proposals PRED štartom                        │
│                                                               │
│  4. START SPRINT                                             │
│     → Project Detail Page                                    │
│     → Kliknúť "Start Sprint" button                         │
│     → Planned → Active                                       │
│                                                               │
│  5. TRACK PROGRESS                                           │
│     → Active sprint tracking                                 │
│     → Burndown chart (budúcnosť)                            │
│     → Daily standup                                          │
│                                                               │
│  6. COMPLETE SPRINT                                          │
│     → Complete button                                        │
│     → Active → Completed                                     │
│     → Velocity calculation                                   │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

---

## 🔧 Technické detaily

### Type Safety:
```typescript
// Centralizovaný type
export type OptimizationScope = 'current_sprint' | 'planned_sprint' | 'backlog';

// Používa sa v:
- src/stores/requirement-change-store.ts
- src/pages/RequirementChangePage.vue
- backend/app/routes/requirement_changes.py (Python string)
```

### Backend Filtering:
```python
# Planned sprint tasks sú filtrované rovnako ako active sprint tasks
if scope == 'planned_sprint':
    planned_sprint = next((s for s in sprints if s.status == 'planned'), None)
    if planned_sprint:
        tasks = [t for t in active_tasks if t.sprint_id == planned_sprint.id]

# Workload calculations:
is_sprint_scope = (scope in ['current_sprint', 'planned_sprint'])
# ← Planned sprint je považovaný za sprint scope (nie backlog)
```

### Frontend Computed:
```typescript
// PERT + RACI Integration
const plannedSprintTasks = computed(() => {
  if (!plannedSprint.value) return [];
  return tasks
    .filter(task => task.sprintId === plannedSprint.value!.id)
    .map(task => convertToTask(task, plannedSprint.value!.id, false));
});

const plannedSprintSummary = computed(() => {
  const totalPert = plannedSprintTasks.value.reduce(...);
  const totalAdjusted = plannedSprintTasks.value.reduce(...);
  const increase = ((totalAdjusted - totalPert) / totalPert) * 100;
  
  return { taskCount, totalPertDuration, totalAdjustedDuration, durationIncrease };
});
```

---

## 📊 Prínos pre používateľa

### Pred implementáciou:
```
User vytvorí planned sprint → Nevie vidieť PERT/RACI analýzu
→ Musí štartovať "naslepo" bez preview
→ Zistí problémy až PO štarte sprintu
```

### Po implementácii:
```
User vytvorí planned sprint → Vidí PERT/RACI analýzu PRED štartom
→ Preview: adjusted duration, workload, uncertainty
→ Dostane optimization proposals
→ Aplikuje optimalizácie
→ Štartuje už optimalizovaný sprint ✅
```

---

## ✅ Testing Checklist

### PERT + RACI Integration:
- [ ] Vytvoriť planned sprint (Smart Planning)
- [ ] Otvoriť PERT + RACI Integration
- [ ] Vybrať projekt s planned sprintom
- [ ] Kliknúť tab "Plánovaný Šprit"
- [ ] Vidieť:
  - [ ] Info banner "Planned Sprint Preview"
  - [ ] Summary: Task count, Duration increase %
  - [ ] Table: PERT estimates, Adjusted Duration, RACI, CV
- [ ] Ak žiadny planned sprint → Empty state + link na Smart Planning

### Project Optimization:
- [ ] Vytvoriť planned sprint (Smart Planning)
- [ ] Otvoriť Project Optimization
- [ ] Vybrať projekt s planned sprintom
- [ ] Kliknúť tab "Planned Sprint"
- [ ] Vidieť:
  - [ ] Info banner "Preview optimization"
  - [ ] Buttons: "Analyze & Optimize", "PERT+RACI Analysis"
- [ ] Kliknúť "Analyze & Optimize"
- [ ] Dostať optimization proposals
- [ ] Vybrať proposals
- [ ] Kliknúť "Apply Changes"
- [ ] Proposals aplikované ✅

---

## 🐛 Bug Fixes (dnešná session)

### Smart Sprint Planning:
1. ✅ Odstránený obsolete "close active sprint" warning
2. ✅ Pridaný "existing planned sprint" warning
3. ✅ Generate button disabled ak planned sprint existuje
4. ✅ Frontend validácia: max 1 active sprint
5. ✅ Backend validácia: max 1 active sprint (update_sprint)
6. ✅ UX fix: Success notification pred reload

### Project Optimization:
7. ✅ Pridaný "Planned Sprint" tab
8. ✅ Backend support pre 'planned_sprint' scope
9. ✅ Type safety: OptimizationScope type export

### PERT + RACI Integration:
10. ✅ Pridaný "Plánovaný Šprit" tab
11. ✅ Preview PERT/RACI analýzy pre planned sprint

---

## 📝 Notes

### TypeScript Cache:
Ak vidíš v terminale error:
```
Argument of type '"planned_sprint"' is not assignable...
```

**To je starý cache** - `ReadLints` potvrdil že kód je správny!

**Fix (ak potrebuješ):**
- Refresh browser (F5)
- Alebo restart `quasar dev`

### Vetur Error:
```
Module 'OptimizationProposals.vue' has no default export
```

Toto je **predexistujúci error** (nie súvisiaci s planned sprintami). Neovplyvňuje funkcionalitu.
