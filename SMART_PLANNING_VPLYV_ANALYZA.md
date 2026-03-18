# Vplyv zmeny 'planned' sprint status na Smart Planning

## 🎯 TL;DR: **ŽIADNY VPLIV NA FUNKČNOSŤ**

Zmena z `status='active'` na `status='planned'` **NEOVPLYVŇUJE** algoritmy Smart Planningu.

---

## 📋 Čo robí Smart Sprint Planner?

### 1. Prijíma input od používateľa/API:
```json
{
  "strategy": "hybrid",
  "sprintName": "Sprint 5",
  "startDate": "2024-01-15",
  "endDate": "2024-01-29",
  "targetUtilization": 85,
  "considerCrossProjectWorkload": true
}
```

### 2. Vyberie eligible tasky:
```python
# backend/app/services/smart_sprint_planner.py, line 61-65

eligible_tasks = [
    task for task in tasks
    if task.status != 'Done' and not self._is_in_active_sprint(task, sprint_config)
]
```

**Kľúčové:** 
- ❌ **NEČÍTA** `sprint.status`
- ✅ Kontroluje len: `task.status != 'Done'`
- ✅ Kontroluje: task nie je v aktívnom šprinte (cez `sprint_config['activeSprintId']`)

### 3. Spustí stratégiu (napr. hybrid):
```python
# Stratégie: priority, workload-balanced, skill-match, skill-priority, 
#            skill-value, value-driven, hybrid

result = planner_func(
    eligible_tasks,
    team_members,
    target_capacity,
    planning_context  # obsahuje cross-project workload
)
```

### 4. Vráti result:
```json
{
  "suggestedTasks": [...],
  "assignments": {...},
  "metrics": {...},
  "reasoning": {...}
}
```

---

## 🔍 Kde Smart Planner ČÍTA sprint status?

### Backend route: `smart_sprint.py`

#### A) Zbieranie eligible taskov (line 95-118)
```python
# Get active sprint if exists
active_sprint = Sprint.query.filter_by(
    project_id=project_id,
    status='active'  # ← ČÍta len active
).first()

# Filter eligible tasks
if active_sprint and not close_active_sprint:
    # Exclude tasks from active sprint
    eligible_tasks = [
        task for task in all_tasks
        if task.status != 'Done' and task.sprint_id != active_sprint.id
    ]
else:
    # Include all non-done tasks
    eligible_tasks = [
        task for task in all_tasks
        if task.status != 'Done'
    ]
```

**Čo to znamená?**
- ✅ Hľadá **ACTIVE sprint** (nie planned)
- ✅ Ak existuje active sprint a `closeActiveSprint=false` → vyradí jeho tasky
- ✅ Ak neexistuje active sprint → všetky non-done tasky sú eligible
- ✅ **Planned sprints sú IGNOROVANÉ** pri filtrovaní taskov

#### B) Cross-project workload (line 124-170)
```python
if consider_cross_project:
    for member in team_members:
        for proj in all_projects:
            # Get active sprints in other projects
            other_active_sprints = Sprint.query.filter_by(
                project_id=proj.id,
                status='active'  # ← ČÍta len active
            ).all()
            
            for sprint in other_active_sprints:
                # Calculate member workload
```

**Čo to znamená?**
- ✅ Cross-project workload počíta **LEN z ACTIVE sprints**
- ✅ Planned sprints v iných projektoch **NIE SÚ započítané**
- ✅ **SPRÁVNE** - plánovaný šprinť ešte nebeží, nemá workload

---

## 📊 Scenáre: PRED vs. PO zmene

### Scenár 1: AI Planner vytvorí nový šprinť (žiadny active)

**PRED (status='active'):**
```
1. AI Planner → vytvorí Sprint 5 (status='active')
2. Smart Planner v iných projektoch:
   - Vidí Sprint 5 ako ACTIVE
   - Započíta jeho workload do cross-project calculation
   - Členovia tímu vyzerajú preťažení ❌
3. Problém: Nemôžem upraviť Sprint 5 pred spustením
```

**PO (status='planned'):**
```
1. AI Planner → vytvorí Sprint 5 (status='planned')
2. Smart Planner v iných projektoch:
   - NEVIDÍ Sprint 5 (je planned, nie active)
   - Workload je stále dostupný ✅
   - Členovia tímu majú korektný workload
3. Benefit: Môžem upraviť Sprint 5 pred spustením
4. Spustím Sprint 5 → zmení sa na 'active'
5. TERAZ sa započíta do workload ✅
```

### Scenár 2: Existuje active sprint, vytváram ďalší

**PRED (status='active'):**
```
Project má Sprint 4 (active)
1. AI Planner → chce vytvoriť Sprint 5 (active)
2. Backend: ERROR ❌ - nemôžeš mať 2 active sprints!
3. Musíš zavrieť Sprint 4 alebo povoliť closeActiveSprint
```

**PO (status='planned'):**
```
Project má Sprint 4 (active)
1. AI Planner → vytvorí Sprint 5 (planned) ✅
2. Sprint 4 beží normálne
3. Sprint 5 čaká (planned)
4. Eligible tasky pre Smart Planner:
   - Vyradené: tasky v Sprint 4 (active)
   - Zahrnuté: tasky v Sprint 5 (planned) AJ backlog
   - SPRÁVNE ✅
```

---

## 🧮 Vplyv na jednotlivé stratégie

### Priority-Based Strategy
```python
def _plan_priority_based(tasks, team_members, target_capacity, context):
    # Sortuje tasky podľa priority (high > medium > low)
    # NEČÍTA sprint status taskov ✅
    # Používa len: task.priority, task.story_points
```
**Vpliv:** ✅ **ŽIADNY**

### Workload-Balanced Strategy
```python
def _plan_workload_balanced(tasks, team_members, target_capacity, context):
    # Balansuje workload medzi členmi
    # Používa member_workloads z context (cross-project)
    # member_workloads = len z ACTIVE sprints ✅
```
**Vpliv:** ✅ **POZITÍVNY** - planned sprints neovplyvňujú balance

### Skill-Match Strategy
```python
def _plan_skill_match(tasks, team_members, target_capacity, context):
    # Matchuje skills medzi členmi a taskmi
    # Používa team_scoring.rank_members_for_task()
    # NEČÍTA sprint status ✅
    # Používa member_workloads pre workload score
```
**Vpliv:** ✅ **POZITÍVNY** - správny workload pre skill matching

### Hybrid Strategy
```python
def _plan_hybrid(tasks, team_members, target_capacity, context):
    # Kombinuje všetky faktory s váhami
    # weights: priority, workload, skills, dependency
    # Používa member_workloads (z active sprints)
```
**Vpliv:** ✅ **POZITÍVNY** - všetky komponenty fungujú správne

---

## 🎭 Príklad: Komplexný scenár

### Setup
- **Projekt A:** Sprint 3 (active) - 40 SP
- **Projekt B:** Sprint 2 (active) - 30 SP  
- **Projekt C:** Žiadny active sprint

### Členovia tímu (pracujú na všetkých projektoch)
- **Alice:** Max 20 SP/sprint
  - Sprint 3 (A): 15 SP (Responsible)
  - Sprint 2 (B): 10 SP (Responsible)
  - **Celkový workload:** 25 SP → 125% ❌ OVERLOADED

- **Bob:** Max 20 SP/sprint
  - Sprint 3 (A): 5 SP (Responsible)
  - Sprint 2 (B): 8 SP (Responsible)
  - **Celkový workload:** 13 SP → 65% ✅ OK

### Smart Planning v Projekte C

**PRED (ak by planned sprints boli započítané):**
```
Projekt C chce vytvoriť Sprint 1
AI Planner (hybrid strategy):
- Alice workload: 25 SP (125%) ❌
- Bob workload: 13 SP (65%) ✅
- Result: Priradí všetko Bobovi, Alice nedostane tasky
- Problém: Alice má kapacitu v Projekte C, len je preťažená inde
```

**PO (planned sprints sa nezapočítavajú):**
```
Projekt C vytvorí Sprint 1 (planned)
AI Planner v Projekte D chce vytvoriť Sprint 1:
- Alice workload: 25 SP (125%) ❌ - z A+B active sprints
- Bob workload: 13 SP (65%) ✅
- Sprint 1 Projektu C (planned) NIE JE započítaný ✅
- Result: Bob dostane tasky
- Správne: Sprint C1 ešte nebeží!

Keď sa Sprint C1 spustí (active):
- Alice workload: 25 + X SP (zo C1)
- Teraz sa započíta pre ďalšie plánovanie ✅
```

---

## 🔧 Čo SA zmení vs. čo zostáva

### ❌ NEMENÍ SA (Smart Planner algoritmy)
- ✅ Priority-based selection
- ✅ Workload balancing
- ✅ Skill matching
- ✅ Dependency checking
- ✅ Value-driven selection
- ✅ Hybrid scoring
- ✅ Task filtering (`task.status != 'Done'`)
- ✅ Team capacity calculation
- ✅ Story points calculation

### ✅ MĚNÍ SA (len backend API behavior)
- `status='active'` → `status='planned'` pri vytvorení
- Odstránená validácia blokujúca viacero 'active' šprintov
- Planned sprints sa **nezapočítavajú** do workload (už to tak bolo!)

---

## 📈 Výhody pre Smart Planning

### 1. Lepšia cross-project visibility
```
PRED: Plánované šprinty vyzerajú ako "bežiace"
PO:   Vidíš len skutočne bežiace šprinty ✅
```

### 2. Multi-sprint scenarios
```
PRED: Nemôžeš vytvoriť viac šprintov naraz
PO:   AI môže vytvoriť Sprint 5, 6, 7 naraz (všetky planned) ✅
      Vyberieš ktorý spustiť prvý
```

### 3. Iteratívne plánovanie
```
PRED: AI vytvorí Sprint 5 → stuck with it
PO:   AI vytvorí Sprint 5 → môžeš upraviť → run AI again → compare ✅
```

### 4. Staging pre veľké zmeny
```
PRED: AI vytvorí Sprint 5 (active) → okamžite ovplyvňuje workload
PO:   AI vytvorí Sprint 5 (planned) → môžeš testovať bez side-effects ✅
      Spustíš až keď si istý
```

---

## 🧪 Testovací scenár

### Test 1: Základný AI Planning
```
1. Projekt má 50 taskov v backlog
2. Spustíš AI Planner (hybrid strategy)
3. Očakávaný výsledok:
   - Vytvorí planned sprint s 15-20 taskami ✅
   - Assignments based on skills + workload ✅
   - Workload calculation korektná ✅
```

### Test 2: Cross-project s planned sprints
```
1. Projekt A: Sprint 3 (active)
2. Projekt B: Sprint 2 (planned) - vytvorený AI
3. Smart Planning v Projekte C:
   - Workload zahŕňa len Sprint 3 (A) ✅
   - Nezahŕňa Sprint 2 (B) ✅
4. Spustíš Sprint 2 (B) → active
5. Smart Planning v Projekte C:
   - Workload TERAZ zahŕňa Sprint 2 (B) ✅
```

### Test 3: Viacnásobné planned sprints
```
1. Spustíš AI Planner 3x
2. Vytvorí Sprint 5, 6, 7 (všetky planned)
3. Smart Planning v inom projekte:
   - Workload nezahŕňa 5, 6, 7 ✅
4. Spustíš Sprint 5 → active
5. Smart Planning v inom projekte:
   - Workload zahŕňa len Sprint 5 ✅
   - Stále nezahŕňa 6, 7 (sú planned) ✅
```

---

## 📝 Záver pre Smart Planning

### 🎯 Hlavný výsledok
**Smart Planning algoritmy zostávajú ÚPLNE NEZMENENÉ.**

### ✅ Čo funguje rovnako
- Všetky stratégie (priority, skill-match, hybrid, atď.)
- Task selection logic
- Team capacity calculations
- Skill matching
- Workload balancing
- Dependency checking
- Reasoning generation

### ✨ Čo je lepšie
- **Korektný cross-project workload** (planned ≠ running)
- **Flexibility** - môžeš upraviť pred spustením
- **Multi-sprint planning** - viacero planned šprintov naraz
- **Staging** - testuj bez side-effects

### 🔑 Kľúčové pravidlo
```
Workload calculation VŽDY používa:
    Sprint.status = 'active'

Planned sprints NIKDY neboli započítavané.
Zmena len sprístupňuje túto logiku užívateľovi.
```

---

## 💡 Odporúčanie

**NIČ NEMENIŤ v Smart Planning kóde.**

Je to perfektne navrhnuté:
- ✅ Workload = len active sprints (správne!)
- ✅ Task filtering = len Done (správne!)
- ✅ Stratégie = nezávislé od sprint status (správne!)

Zmena len umožňuje **lepší user workflow** bez toho aby sa dotkla algoritmov.
