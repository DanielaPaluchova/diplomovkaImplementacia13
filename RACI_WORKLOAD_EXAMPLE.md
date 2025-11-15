# RACI Workload - Praktický Príklad

## Scenár: Sarah's Workload Analýza

### Setup

**Team Member:** Sarah Johnson  
**Max Story Points:** 20 SP  
**Projects:** E-Commerce Platform, Mobile App, Admin Dashboard

---

## Situácia: Active Sprint (Sprint 2)

### 📦 Project 1: E-Commerce Platform (Aktuálne zobrazený projekt)

**Sprint:** Sprint 2 (Active)  
**Sarah's Tasks:**

| Task | SP | RACI Role | Weight | Weighted SP |
|------|----|-----------| -------|-------------|
| Implement Payment Gateway | 5 | **Responsible** (R) | 1.0 | **5.0** |
| Design Checkout Flow | 8 | **Consulted** (C) | 0.05 | **0.4** |
| Review Security Audit | 3 | **Informed** (I) | 0.01 | **0.03** |

**Subtotal E-Commerce:** 5.0 + 0.4 + 0.03 = **5.43 weighted SP**

---

### 📱 Project 2: Mobile App

**Sprint:** Sprint 2 (Active)  
**Sarah's Tasks:**

| Task | SP | RACI Role | Weight | Weighted SP |
|------|----|-----------| -------|-------------|
| Implement Authentication | 8 | **Responsible** (R) | 1.0 | **8.0** |
| Setup CI/CD Pipeline | 5 | **Accountable** (A) | 0.1 | **0.5** |
| API Integration Review | 5 | **Consulted** (C) | 0.05 | **0.25** |

**Subtotal Mobile App:** 8.0 + 0.5 + 0.25 = **8.75 weighted SP**

---

### 🖥️ Project 3: Admin Dashboard

**Sprint:** Sprint 2 (Active)  
**Sarah's Tasks:**

| Task | SP | RACI Role | Weight | Weighted SP |
|------|----|-----------| -------|-------------|
| User Management UI | 3 | **Responsible** (R) | 1.0 | **3.0** |
| Database Schema Update | 8 | **Consulted** (C) | 0.05 | **0.4** |
| Deployment Notification | 2 | **Informed** (I) | 0.01 | **0.02** |

**Subtotal Admin Dashboard:** 3.0 + 0.4 + 0.02 = **3.42 weighted SP**

---

## 🎯 Výsledky - Co Vidí Užívateľ

### 1. Na Stránke "E-Commerce Platform" (Project Detail)

#### ❌ NESPRÁVNE (Keby bol workload len pre jeden projekt):
```
Project Workload: 27%
Calculation: (5.43 weighted SP / 20 max SP) × 100 = 27%
```

#### ✅ SPRÁVNE (Cross-Project):
```
Cross-Project Workload: 86%
Calculation: ((5.43 + 8.75 + 3.42) / 20) × 100 = 86%
```

---

### 2. Na Stránke "PERT + RACI Optimization"

#### RACI Weighted Workload Card:
```
Sarah Johnson
Workload: 86%
Weighted SP: 17.6
```

**Breakdown:**
- E-Commerce Platform: 5.43 SP (27%)
- Mobile App: 8.75 SP (44%)
- Admin Dashboard: 3.42 SP (17%)
- **Total: 17.6 SP (86%)**

**Status:** 🔴 Near Capacity (>85%)

---

### 3. Na Stránke "Requirement Changes / PERT+RACI Optimization"

#### Current Project State:

```
┌─────────────────────────────────────────┐
│  Project Workload: 27%                  │  ← Only E-Commerce Platform
│  (Active sprint only)                   │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  Cross-Project Workload: 86%            │  ← Across ALL projects
│  (All active sprints)                   │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  RACI Workload: 86%                     │  ← Across ALL projects
│  (Active sprint across all projects)   │
└─────────────────────────────────────────┘
```

**Tooltip Detail:**
```
RACI-Weighted Workload
Active sprint across all projects

Sarah Johnson: 86%
█████████████████░░░  17.6 weighted SP

John Smith: 55%
███████████░░░░░░░░░  11.0 weighted SP

Emily Chen: 92%
██████████████████▓░  18.4 weighted SP
```

---

## 📊 Porovnanie Metód Výpočtu

### Metóda 1: Simple Workload (len Responsible v jednom projekte)
```
Calculation: Responsible SP / Max SP
Sarah: 5 SP / 20 SP = 25%
```
❌ **Problém:** Ignoruje ostatné RACI role a ostatné projekty

---

### Metóda 2: Project Workload (všetky RACI role v jednom projekte)
```
Calculation: Weighted SP (single project) / Max SP
Sarah: 5.43 weighted SP / 20 SP = 27%
```
❌ **Problém:** Ignoruje workload v ostatných projektoch

---

### Metóda 3: Cross-Project Workload (len Responsible naprieč projektami)
```
Calculation: Total Responsible SP (all projects) / Max SP
Sarah: (5 + 8 + 3) SP / 20 SP = 80%
```
⚠️ **Problém:** Ignoruje ostatné RACI role (Accountable, Consulted, Informed)

---

### Metóda 4: **RACI Cross-Project Workload** ✅ (POUŽÍVA SA)
```
Calculation: Total Weighted SP (all projects, all RACI) / Max SP
Sarah: 17.6 weighted SP / 20 SP = 86%

Breakdown:
  E-Commerce (R):  5.0 SP
  E-Commerce (C):  0.4 SP
  E-Commerce (I):  0.03 SP
  Mobile (R):      8.0 SP
  Mobile (A):      0.5 SP
  Mobile (C):      0.25 SP
  Dashboard (R):   3.0 SP
  Dashboard (C):   0.4 SP
  Dashboard (I):   0.02 SP
  ─────────────────────
  TOTAL:          17.6 weighted SP
```
✅ **Správne:** Zohľadňuje všetky RACI role a všetky projekty

---

## 🎯 Prečo Je To Dôležité?

### Scenár: Plánujem nový Sprint pre E-Commerce Platform

#### Ak by som používal Project Workload (27%):
```
Sarah má 27% workload v E-Commerce
→ Môžem jej prideliť ešte 73% kapacity (14.6 SP)
→ Pridelím jej 13 SP nových úloh
→ ✅ Zdá sa v poriadku
```

#### Realita s RACI Cross-Project Workload (86%):
```
Sarah má 86% workload naprieč všetkými projektmi
→ Má len 14% voľnej kapacity (2.8 SP)
→ Ak jej pridelím 13 SP:
   → 17.6 + 13 = 30.6 weighted SP
   → 30.6 / 20 = 153% workload
   → 🔴 KRITICKÉ PREŤAŽENIE!
```

### Dôsledky ignorovania cross-project workload:
1. ❌ **Preťaženie členov tímu** → vyhorenie, kvalita klesá
2. ❌ **Nezodpovedné odhady** → sprinty zlyhávajú
3. ❌ **Bottlenecks** → celý projekt sa spomaľuje
4. ❌ **Nespokojný klient** → termíny sa posúvajú

---

## 🛠️ Ako To Funguje V Aplikácii

### 1. **PERT + RACI Optimization Page**

#### Tab: "Active Sprint"

**Zobrazuje:**
- RACI Weighted Workload (naprieč všetkými projektmi)
- Tasks from active sprint (len aktuálny projekt)
- Adjusted Duration (zohľadňuje cross-project overload)

**Príklad:**
```
┌─────────────────────────────────────────────────────┐
│ RACI Weighted Workload (All Projects)               │
├─────────────────────────────────────────────────────┤
│ Sarah Johnson    86%  █████████████████░░░  17.6 SP │
│ Emily Chen       92%  ██████████████████▓░  18.4 SP │
│ John Smith       55%  ███████████░░░░░░░░░  11.0 SP │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ Active Sprint Tasks (E-Commerce Only)               │
├─────────────────────────────────────────────────────┤
│ Implement Payment Gateway                           │
│ Assigned: Sarah (R)                                 │
│ PERT: 3d → Adjusted: 3.6d (+20% delay)             │
│ Reason: Sarah is 86% loaded (overload overhead)    │
└─────────────────────────────────────────────────────┘
```

**Interpretácia:**
- Sarah má 86% workload naprieč všetkými projektmi
- Keď je over 85%, jej úlohy sa dokončia pomalšie (overhead)
- PERT duration 3d sa zmení na Adjusted duration 3.6d

---

#### Tab: "Future/Backlog"

**Zobrazuje:**
- Average RACI Weighted Workload z minulých sprintov (naprieč všetkými projektmi)
- Tasks v backlogu (len aktuálny projekt)
- Optimálne priradenia na základe historických dát

**Príklad:**
```
┌─────────────────────────────────────────────────────┐
│ Historical Average Workload (All Projects)          │
├─────────────────────────────────────────────────────┤
│ Sarah Johnson    AVG: 78%  (Last 3 sprints)        │
│ Emily Chen       AVG: 85%  (Last 3 sprints)        │
│ John Smith       AVG: 62%  (Last 3 sprints)        │
└─────────────────────────────────────────────────────┘

Future capacity prediction:
→ Sarah can handle: 4.4 weighted SP (22% remaining)
→ Emily can handle: 3.0 weighted SP (15% remaining)
→ John can handle: 7.6 weighted SP (38% remaining)
```

---

### 2. **Requirement Changes Page**

#### Current State Cards:

```
┌────────────────────┐  ┌────────────────────┐  ┌────────────────────┐
│ Project Workload   │  │ Cross-Project      │  │ RACI Workload      │
│                    │  │ Workload           │  │                    │
│      27%           │  │      86%           │  │      86%           │
│                    │  │                    │  │                    │
│ Active sprint      │  │ All active sprints │  │ Active sprint      │
│ (This project)     │  │ (All projects)     │  │ (All projects)     │
└────────────────────┘  └────────────────────┘  └────────────────────┘
```

**Interpretácia:**
- **Project Workload (27%):** Sarah má 27% workload v aktuálnom projekte
- **Cross-Project Workload (86%):** Sarah má 86% workload naprieč všetkými projektmi (Responsible len)
- **RACI Workload (86%):** Sarah má 86% workload naprieč všetkými projektmi (všetky RACI role)

---

#### PERT+RACI Analysis:

Keď kliknete na "PERT+RACI Analysis", aplikácia:

1. **Analyzuje cross-project RACI workload**
2. **Detekuje overload členov tímu**
3. **Generuje návrhy:**

```
┌─────────────────────────────────────────────────────────────────┐
│ 🔴 CRITICAL: RACI Overload                                      │
├─────────────────────────────────────────────────────────────────┤
│ Reassign 'Implement Payment Gateway' from Sarah Johnson         │
│                                                                  │
│ Reason:                                                          │
│ Sarah is overloaded with RACI-weighted workload at 86% capacity │
│ (17.6 weighted SP / 20 max SP). Reassign to John Smith.        │
│                                                                  │
│ Impact:                                                          │
│ • Sarah: 86% → 61% (-25%)                                       │
│ • John: 55% → 80% (+25%)                                        │
│ • Better balance across team                                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🧮 Formula Detail

### RACI Weights:
```python
RACI_WEIGHTS = {
    'responsible': 1.0,   # 100% - doing the work
    'accountable': 0.1,   # 10%  - oversight, approval
    'consulted':   0.05,  # 5%   - providing input, meetings
    'informed':    0.01   # 1%   - kept in the loop, emails
}
```

### Calculation:
```python
for each member:
    weighted_sp = 0
    
    for each project:
        for each task in active_sprint:
            
            if member is Responsible:
                weighted_sp += task.story_points × 1.0
            
            if member is Accountable:
                weighted_sp += task.story_points × 0.1
            
            if member is Consulted:
                weighted_sp += task.story_points × 0.05
            
            if member is Informed:
                weighted_sp += task.story_points × 0.01
    
    workload_percentage = (weighted_sp / member.max_story_points) × 100
```

---

## ✅ Záver

### Sarah's Real Situation:

| Metric | Value | Interpretation |
|--------|-------|----------------|
| **Simple Workload** | 25% | ❌ Misleading - only one role in one project |
| **Project Workload** | 27% | ❌ Misleading - all RACI roles but only one project |
| **Cross-Project Workload** | 80% | ⚠️ Better - but missing RACI overhead |
| **RACI Cross-Project Workload** | **86%** | ✅ **ACCURATE - Complete picture** |

### Key Takeaways:

1. ✅ **RACI Workload je CROSS-PROJECT** - zohľadňuje všetky projekty
2. ✅ **Zahŕňa všetky RACI role** - Responsible, Accountable, Consulted, Informed
3. ✅ **Váhy zodpovedajú realite** - Consulted a Informed majú nižšie váhy, ale sú dôležité
4. ✅ **Používa sa v celej aplikácii konzistentne** - frontend aj backend
5. ✅ **Kritické pre správne rozhodnutia** - prevencia preťaženia a optimálna alokácia

---

**Pamätajte:** Člen tímu môže mať nízky workload v jednom projekte, ale byť preťažený naprieč všetkými projektmi. RACI Cross-Project Workload vám dáva pravdivý obraz! 🎯


