# Testing Guide: PERT + RACI Analysis

## 1. RACI Overload Testing

### A. Reassign Scenario (候选人有容量 <120%)

**Cieľ:** Vyvolať RACI overload na jednom členovi s dostupným kandidátom

**Setup:**
1. **Team Member 1 (Lisa):** Max capacity = 20 SP
   - Priraď 3-4 tasky ako **Responsible** (R) = 25+ SP celkovo
   - RACI-weighted workload = 25/20 = **125%** ✅ Overloaded

2. **Team Member 2 (doggy1):** Max capacity = 20 SP
   - Priraď 1-2 tasky ako Responsible = 10 SP celkovo
   - RACI-weighted workload = 10/20 = **50%** 
   - Po reassignmente jedného tasku (5 SP): 15/20 = **75%** ✅ <120%

**Očakávaný výsledok:**
- ✅ Proposal: "RACI overload: Reassign 'task1' from Lisa to doggy1"
- ⚠️ Bez overload warningu (doggy1 bude na 75%)

### B. Backlog Scenario (všetci >120%)

**Setup:**
1. **Team Member 1 (Lisa):** Max capacity = 20 SP
   - Priraď tasky = 25 SP (125% workload)

2. **Team Member 2 (doggy1):** Max capacity = 20 SP
   - Priraď tasky = 22 SP (110% workload)
   - Po reassignmente jedného tasku (5 SP): 27/20 = **135%** ❌ >120%

**Očakávaný výsledok:**
- ✅ Proposal: "RACI overload: Move 'task1' to backlog"
- 🔴 Severity: `critical`
- 📝 Reason: "Best available candidate doggy1 would be at 135% after reassignment, which is too high"

---

## 2. Duration Risk Testing

**Duration Risk používa 2-strategy approach:**
1. **STRATEGY 1:** Skúsi nájsť reassignment (kandidát s skills + kapacita)
2. **STRATEGY 2:** Ak reassignment neuspeje → navrhne sprint move (backlog)

### A. Reassign Scenario (STRATEGY 1)

**Cieľ:** RACI-adjusted duration > PERT duration * 1.2 + existuje kandidát

**Setup:**
1. Vytvor task s PERT estimates:
   - Optimistic: 2 days
   - Most Likely: 5 days
   - Pessimistic: 8 days
   - **PERT Expected**: ~5 days
   - Required skills: napr. "python"

2. **Assignee (Lisa):** 
   - Má veľa RACI rolí → vysoký workload (napr. 120%)
   - RACI-adjusted duration: ~7+ days (>6 days = 20% overhead)
   - Skills: python ✅

3. **Kandidát (doggy1):**
   - Nízky workload (napr. 50%)
   - Skills: python ✅
   - Po reassignmente: <100% workload

**Očakávaný výsledok:**
- ✅ Proposal: "Duration risk: Reassign 'task' to reduce overhead"
- Zobrazí improvement v duration (7d → 5.5d)
- Zobrazí workload impact

### B. Backlog Scenario (STRATEGY 2)

**Cieľ:** Duration overhead + žiadny vhodný kandidát

**Setup:**
1. Task s vysokým PERT overhead (ako vyššie)
2. **Assignee (Lisa):** Prepracovaná (120% workload)
3. **Všetci ostatní členovia:**
   - Buď prepracovaní (>100%)
   - Alebo nemajú potrebné skills
   - Príklad: doggy1 má 50% workload, ale nemá skill "python"

**Očakávaný výsledok:**
- ✅ Proposal: "Duration overhead: 'task' (40% delay)"
- 📝 Title: "Move to next sprint to reduce duration overhead"
- 📝 Reason: "No team member available with required skills and capacity. Consider moving to next sprint"
- 🔧 Action: `sprint_move` s `toSprintId: null` (backlog)

---

## 3. PERT Uncertainty Testing

**Cieľ:** Vysoká variabilita v PERT estimates (CV > 0.33)

**Setup:**
1. Vytvor task s veľkým rozptylom v estimates:

**Example A - High Uncertainty (split):**
- Optimistic: 1 day
- Most Likely: 5 days
- Pessimistic: 20 days
- **Standard Deviation**: ~3.17 days
- **CV (Coefficient of Variation)**: 3.17 / 6.5 = **0.49** ✅ >0.33

**Example B - Medium Uncertainty (buffer):**
- Optimistic: 3 days
- Most Likely: 5 days
- Pessimistic: 9 days
- **Standard Deviation**: 1 day
- **CV**: 1 / 5.33 = **0.19** → Medium (buffer only)

**Example C - Low Uncertainty:**
- Optimistic: 4 days
- Most Likely: 5 days
- Pessimistic: 6 days
- **CV**: <0.2 → No proposal

**Očakávaný výsledok:**
- **High CV (>0.33):** Proposal na **split task**
- **Medium CV (0.2-0.33):** Proposal na **add buffer**
- **Low CV (<0.2):** Žiadny proposal

### Ako vypočítať CV manuálne:
```
Standard Deviation (σ) = (Pessimistic - Optimistic) / 6
Expected Duration (μ) = (Optimistic + 4*MostLikely + Pessimistic) / 6
CV = σ / μ

For CV > 0.33:
Pessimistic should be at least 3x Optimistic
Example: O=2, ML=6, P=12 → CV = 1.67/6.67 = 0.25 (too low)
Example: O=1, ML=5, P=20 → CV = 3.17/6.5 = 0.49 ✅
```

---

## Quick Test Checklist

### RACI Overload:
- [ ] Lisa: 125% workload, doggy1: 50% → Očakávam reassign
- [ ] Lisa: 125%, doggy1: 110% → Očakávam backlog move

### Duration Risk:
- [ ] Task s vysokým PERT expected + prepracovaný assignee → Očakávam reassign
- [ ] Task + všetci prepracovaní → Očakávam reassign + warning

### PERT Uncertainty:
- [ ] Pessimistic/Optimistic ratio > 3:1 → Očakávam split proposal
- [ ] Moderate spread → Očakávam buffer proposal
- [ ] Low spread → Žiadny proposal

---

## RACI Weights Reference:
- **Responsible (R):** 1.0 (plná váha)
- **Accountable (A):** 0.1
- **Consulted (C):** 0.05
- **Informed (I):** 0.01

**Príklad:**
Task 5 SP:
- Lisa: R (5 * 1.0 = 5 weighted SP)
- John: A (5 * 0.1 = 0.5 weighted SP)
- Jane: C (5 * 0.05 = 0.25 weighted SP)

---

## PERT Uncertainty Split - Čo sa skopíruje a čo sa zmení

### ✅ Zostane rovnaké (skopíruje sa do všetkých subtaskov):
- `sprint_id` - Ak je v sprinte, subtasky tam zostanú
- `project_id`
- `priority` (high, medium, low)
- `type` (feature, bug, task)
- `labels`
- `complexity`
- **RACI role** (Responsible, Accountable, Consulted, Informed)
- `required_skills` - Všetky subtasky majú rovnaké skill requirements
- **`due_date`** - Všetky subtasky majú rovnaký deadline ⚠️

### 📊 Rozdelí sa proporcionálne (podľa story points):
- **`story_points`** - Napr. 8 SP → 4 SP + 4 SP
- **`estimated_hours`** - Napr. 80h → 40h + 40h
- **PERT estimates** - S uncertainty reduction factor (1/sqrt(N))

### 🔄 Vygeneruje sa nové:
- `name` - task8 → task8 1, task8 2
- `title` - task8 title → task8 title 1, task8 title 2
- `status` - Resetne sa na "To Do"
- `actual_hours` - Resetne sa na 0

### ❌ Originálny task sa vymaže
Po vytvorení subtaskov sa originálny task úplne odstráni z databázy.

**Príklad split:**
```
Originál: task8
- 8 SP
- 80 estimated_hours
- due_date: 31.12.2024
- PERT: O=8d, ML=12d, P=40d (CV=28.6%)

Po split (2 subtasky):
task8 1:
- 4 SP
- 40 estimated_hours (80 * 4/8)
- due_date: 31.12.2024 (rovnaký!)
- PERT: O=6d, ML=8d, P=14d (CV~20%, nižšia uncertainty)

task8 2:
- 4 SP
- 40 estimated_hours (80 * 4/8)
- due_date: 31.12.2024 (rovnaký!)
- PERT: O=6d, ML=8d, P=14d (CV~20%, nižšia uncertainty)
```

