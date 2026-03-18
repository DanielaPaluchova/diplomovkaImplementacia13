# Analýza vplyvu zmeny 'planned' sprint status na PERT/RACI optimalizáciu

## Zhrnutie
**✅ ŽIADNY NEGATÍVNY VPLIV** - Zmena z `status='active'` na `status='planned'` pri vytváraní šprintov **NEMÁ VPLYV** na PERT, RACI, Adjusted PERT/RACI ani optimalizáciu.

---

## 1. Smart Sprint Planner - ŽIADNY VPLIV

### Súčasné správanie
```python
# backend/app/services/smart_sprint_planner.py

def plan_sprint(...):
    # Filtruje eligible tasky
    eligible_tasks = [
        task for task in tasks
        if task.status != 'Done' and not self._is_in_active_sprint(task, sprint_config)
    ]
```

### Analýza
- **Smart Sprint Planner NEČÍTA sprint status** pri výbere taskov
- Používa len: `task.status != 'Done'` a kontroluje `sprint_config['activeSprintId']`
- Výber taskov, skill matching, workload balancing **nie sú ovplyvnené**
- Všetky stratégie (priority, skill-match, hybrid, atď.) zostávajú **NEZMENENÉ**

### Záver: ✅ **BEZ VPLYVU**

---

## 2. PERT Uncertainty Analysis - ŽIADNY VPLYIV

### Súčasné správanie
```python
# backend/app/services/pert_raci_analyzer.py, line 38-143

def find_pert_uncertainty_risks(self, tasks: List[Task]) -> List[Dict]:
    for task in tasks:
        if task.status == 'Done':
            continue
        
        # Analyzuje PERT estimates (optimistic, pessimistic, expected)
        # Počíta Coefficient of Variation (CV)
        # Navrhuje split ak CV > 33%
```

### Analýza
- **PERT analýza NEČÍTA `sprint_id` ani sprint status**
- Kontroluje len: `task.status == 'Done'`
- Počíta:
  - Standard Deviation: `σ = (Pessimistic - Optimistic) / 6`
  - Coefficient of Variation: `CV = σ / Expected`
  - Confidence intervals (68%, 95%)
- Proposals sa generujú **nezávisle od šprintu**

### Záver: ✅ **BEZ VPLYVU**

---

## 3. RACI Overload Analysis - POUŽÍVA LEN ACTIVE SPRINTS ✅

### Súčasné správanie
```python
# backend/app/services/pert_raci_analyzer.py, line 146-374

def find_raci_overload_risks(
    self,
    team_members: List[TeamMember],
    tasks: List[Task],
    sprint_id: int = None,
    all_tasks: List[Task] = None
) -> List[Dict]:
    # Volá cross-project workload calculator
    from app.utils.workload_calculator import calculate_cross_project_raci_workload
    
    cross_project_workload = calculate_cross_project_raci_workload(
        team_members,
        sprint_id=sprint_id
    )
```

### Workload Calculator - KĽÚČOVÁ ČASŤ
```python
# backend/app/utils/workload_calculator.py, line 77-176

def calculate_cross_project_raci_workload(...):
    """
    Calculate RACI-weighted workload for team members across ALL projects.
    Always calculates from ACTIVE sprints in all projects.
    """
    
    # KRITICKÉ: Používa len ACTIVE sprints!
    active_sprints = Sprint.query.filter_by(
        project_id=proj.id,
        status='active'  # ← HARDCODED!
    ).all()
    
    for sprint in active_sprints:
        # Počíta RACI weighted workload
        # R: 1.0, A: 0.1, C: 0.05, I: 0.01
```

### Analýza
- **RACI Overload POUŽÍVA LEN `status='active'` sprints**
- Planned sprints **NIE SÚ ZAPOČÍTANÉ** do workload calculation
- To je **SPRÁVNE SPRÁVANIE** pretože:
  - Planned sprint = ešte nebeží
  - Workload overload = aktuálne preťaženie
  - Až keď sa planned sprint spustí (`status='active'`), začne sa započítavať

### Implikácia zmeny na 'planned'
**✅ POZITÍVNY EFEKT:**
- AI Sprint Planner vytvorí šprinť s `status='planned'`
- **Workload sa nezapočíta** kým nespustíte šprinť
- Môžete **naplánovať viacero šprintov dopredu** bez ovplyvnenia RACI analýzy
- Akonáhle spustíte šprinť (zmena na `'active'`), **automaticky sa započíta** do workload

### Záver: ✅ **ŽIADNY NEGATÍVNY VPLIV, POZITÍVNY BENEFIT**

---

## 4. Adjusted Duration (PERT + RACI) - POUŽÍVA LEN ACTIVE SPRINTS ✅

### Súčasné správanie
```python
# backend/app/services/pert_raci_analyzer.py, line 376-633

def find_adjusted_duration_risks(...):
    """
    Find tasks where RACI-adjusted duration significantly exceeds PERT duration
    """
    
    # Používa rovnaký workload calculator ako RACI Overload
    cross_project_workload = calculate_cross_project_raci_workload(
        team_members,
        sprint_id=sprint_id
    )
    
    # Pre každý task počíta:
    adjusted_duration = self._calculate_task_adjusted_duration(
        task, team_members, member_workloads
    )
    
    # Formula: T_adjusted = T_pert × (1 + (1×LR) + (0.1×LA) + (0.05×LC) + (0.01×LI))
    # kde LR, LA, LC, LI sú EXCESS overload (nad 100%) pre jednotlivé RACI role
```

### Analýza
- **Adjusted Duration POUŽÍVA workload calculator**
- Workload calculator používa **LEN ACTIVE sprints** (viď bod 3)
- Planned sprints **NIE SÚ ZAPOČÍTANÉ**
- Duration overhead sa počíta len z **aktuálneho (active) preťaženia**

### Implikácia zmeny na 'planned'
**✅ SPRÁVNE SPRÁVANIE:**
- Planned sprint tasks **nespôsobujú duration overhead**
- Až po spustení šprintu (`status='active'`) sa začne počítať overhead
- **Logické** - plánovaný šprinť ešte nebeží, takže nespôsobuje preťaženie

### Záver: ✅ **ŽIADNY NEGATÍVNY VPLIV**

---

## 5. OptimizationLog - ŽIADNY VPLIV

### Súčasné správanie
```python
# backend/app/routes/smart_sprint.py, line 377-393

optimization_log = OptimizationLog(
    project_id=project_id,
    optimization_type='smart_sprint',
    proposals_count=len(task_ids),
    applied_count=tasks_updated,
    scope='sprint_planning',
    results={
        'sprintId': new_sprint.id,
        'sprintName': sprint_name,
        'tasksUpdated': tasks_updated,
        'assignmentsApplied': assignments_applied,
        'plannedStoryPoints': new_sprint.planned_story_points,
        'closedSprint': closed_sprint is not None
    }
)
```

### Analýza
- **OptimizationLog NEPOUŽÍVA sprint status**
- Loguje len: ID, meno, tasky, story points
- Žiadna logika závislá na statuse

### Záver: ✅ **BEZ VPLYVU**

---

## 6. Cross-Project Workload Consideration - POUŽÍVA LEN ACTIVE SPRINTS ✅

### Smart Sprint Planning s Cross-Project Workload
```python
# backend/app/routes/smart_sprint.py, line 124-170

if consider_cross_project:
    for member in team_members:
        # Get all projects where member is assigned
        all_projects = [...]
        
        for proj in all_projects:
            if proj.id == project_id:
                continue  # Skip current project
            
            # Get active sprints in other projects
            other_active_sprints = Sprint.query.filter_by(
                project_id=proj.id,
                status='active'  # ← HARDCODED!
            ).all()
```

### Analýza
- **Smart Sprint Planning cross-project workload POUŽÍVA LEN `status='active'`**
- Planned sprints v iných projektoch **NIE SÚ ZAPOČÍTANÉ**
- To je **SPRÁVNE** - nechceme blokovať plánovanie kvôli plánovaným (ešte nebežiacim) šprintom

### Záver: ✅ **SPRÁVNE SPRÁVANIE, BEZ NEGATÍVNEHO VPLYVU**

---

## 7. Sprint Analyzer - ANALYZUJE VŠETKY STATUSY ✅

### Súčasné správanie
```python
# backend/app/services/sprint_analyzer.py

for sprint in project.sprints:
    if sprint.status != 'completed':  # Analyzuje active AJ planned
        # Calculate utilization, velocity, risk
```

### Analýza
- **Sprint Analyzer analyzuje ACTIVE aj PLANNED sprints**
- Počíta metrics:
  - Utilization (capacity usage)
  - Velocity (task completion rate)
  - Risk level
  - Overload/underutilization
- **Správne správanie** - môžete analyzovať aj plánované šprinty

### Záver: ✅ **FUNGUJE SPRÁVNE PRE PLANNED SPRINTS**

---

## FINÁLNE ZHRNUTIE

### Zmeny ktoré boli urobené
1. ✅ AI Sprint Planner vytvára sprints s `status='planned'` namiesto `'active'`
2. ✅ Odstránená validácia blokujúca vytvorenie nového šprintu pri existujúcom active šprinte

### Vplyv na jednotlivé komponenty

| Komponent | Status Check | Vpliv | Poznámka |
|-----------|-------------|-------|----------|
| **Smart Sprint Planner** | ❌ Nepoužíva | ✅ BEZ VPLYVU | Filtruje len `task.status != 'Done'` |
| **PERT Uncertainty** | ❌ Nepoužíva | ✅ BEZ VPLYVU | Analyzuje len PERT estimates |
| **RACI Overload** | ✅ `status='active'` | ✅ POZITÍVNE | Planned sprints sa nezapočítavajú (správne) |
| **Adjusted Duration** | ✅ `status='active'` | ✅ POZITÍVNE | Planned sprints nespôsobujú overhead (správne) |
| **Cross-Project Workload** | ✅ `status='active'` | ✅ POZITÍVNE | Planned sprints v iných projektoch neblokujú plánovanie |
| **Sprint Analyzer** | ✅ `!='completed'` | ✅ FUNGUJE | Analyzuje aj planned sprints |
| **OptimizationLog** | ❌ Nepoužíva | ✅ BEZ VPLYVU | Loguje len základné info |

### Kľúčové zistenia

#### 1. Workload Calculation je SPRÁVNE implementovaný
```python
# Všetky workload calculations používajú:
status='active'  # HARDCODED, NIE parameter!
```
**Dôsledok:**
- Planned sprints **NIKDY** neboli započítavané do workload
- Zmena na `status='planned'` **nemení** toto správanie
- **Korektné** - plánovaný šprinť ešte nebeží, nemá workload

#### 2. PERT/RACI analýza je nezávislá od sprint status
```python
# PERT analyzuje:
if task.status == 'Done':
    continue
# IGNORUJE sprint_id, sprint status
```
**Dôsledok:**
- PERT proposals sa generujú **nezávisle od šprintov**
- Task môže byť v planned šprinte a stále sa analyzuje
- **Správne** - PERT risk existuje nezávisle od sprint assignment

#### 3. Adjusted PERT/RACI používa aktuálny (active) workload
```python
# Počíta duration overhead len z ACTIVE sprints
# Formula: T_adjusted = T_pert × (1 + RACI_overload)
# kde overload = len z active sprints
```
**Dôsledok:**
- Planned sprint tasks **nespôsobujú** duration overhead
- Overhead sa objaví až **po spustení** šprintu
- **Logické** a **korektné**

---

## Nové možnosti s Jira-style workflow

### Pred zmenou
```
AI Planner → Sprint (status='active') → Nemôžem upraviť → Problém!
```

### Po zmene
```
AI Planner → Sprint (status='planned') ✓
    ↓
Môžem upraviť tasky ✓
    ↓
Môžem upraviť šprinť ✓
    ↓
Start Sprint → Sprint (status='active') ✓
    ↓
Workload sa TERAZ započíta do RACI analýzy ✓
```

### Benefit pre optimalizáciu
1. **Naplánovať viacero šprintov dopredu** bez ovplyvnenia RACI workload
2. **Testovať rôzne scenáre** (AI planner môže vytvoriť viacero plánov)
3. **Upraviť plán** pred spustením (pridať/odobrať tasky)
4. **RACI analýza vidí len reálne bežiace šprinty** (active)
5. **Akonáhle spustíte šprinť**, workload sa **automaticky započíta**

---

## Odporúčania

### ✅ NIČ NEMENIŤ v optimalizácii
- Súčasná logika je **SPRÁVNA**
- Workload calculations sú **KOREKTNÉ**
- PERT/RACI analýza je **NEZÁVISLÁ** od sprint status

### ✅ Dokumentovať pre používateľov
Pri AI Sprint Planning informovať:
```
⚠️ POZNÁMKA:
Vytvorený šprinť má status PLANNED.
RACI workload sa započíta až po SPUSTENÍ šprintu (tlačidlo Start).
Môžete upraviť tasky a assignments pred spustením.
```

### ✅ Možné rozšírenia (budúcnosť)
1. **"What-if" analýza:**
   - Pridať tlačidlo "Preview RACI Impact"
   - Ukáže ako by vyzeral workload **ak by** sa šprinť spustil
   - Pomocná funkcia pre rozhodovanie

2. **Multi-sprint planning:**
   - AI Planner vytvorí viacero planned šprintov naraz
   - Používateľ vyberie ktorý spustiť prvý

3. **Planned sprint warnings:**
   - Ak má projekt viac ako 3 planned sprints → warning
   - "Máte veľa plánovaných šprintov, možno ich čas spustiť?"

---

## Testovanie

### Scenáre na otestovanie
1. ✅ **Vytvorenie planned šprintu cez AI Planner**
   - Overiť `status='planned'`
   - RACI workload **NEMÁ** zahŕňať tieto tasky

2. ✅ **Spustenie planned šprintu**
   - Zmena na `status='active'`
   - RACI workload **TERAZ ZAHŔŇA** tieto tasky

3. ✅ **Viacero planned šprintov**
   - Vytvoriť 2-3 planned sprints
   - Overiť že workload zostáva stabilný
   - Spustiť jeden → workload sa zvýši len pre ten jeden

4. ✅ **Cross-project s planned sprints**
   - Projekt A: active sprint
   - Projekt B: planned sprint (s rovnakými členmi)
   - Workload v projekte A by mal zahŕňať len A active sprint

---

## Záver

### 🎯 HLAVNÝ VÝSLEDOK
**Zmena z `status='active'` na `status='planned'` pri vytváraní šprintov cez AI Planner:**
- ✅ **NEMÁ NEGATÍVNY VPLIV** na PERT analýzu
- ✅ **NEMÁ NEGATÍVNY VPLIV** na RACI analýzu
- ✅ **NEMÁ NEGATÍVNY VPLIV** na Adjusted PERT/RACI
- ✅ **NEMÁ NEGATÍVNY VPLIV** na optimalizáciu
- ✅ **PRINÁŠA BENEFIT** - flexibilnejší workflow

### 📊 Technické zistenie
Všetky workload calculations používajú **HARDCODED** `status='active'` filter, čo znamená:
- Planned sprints **NIKDY** neboli započítavané
- Zmena **NEMENÍ** toto správanie
- Je to **SPRÁVNY DESIGN** - planned ≠ running

### ✨ Výhoda
Nový Jira-style workflow je **plne kompatibilný** s existujúcou optimalizáciou a umožňuje **lepšie plánovanie** bez nežiadúcich vedľajších efektov.
