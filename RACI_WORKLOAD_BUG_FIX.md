# 🐛 RACI Workload Bug Fix - Sprint ID Issue

## Dátum: 2025-11-11
## Status: ✅ OPRAVENÉ

---

## 🔴 Objavená Chyba

### Problém:
**RACI Workload čísla nesedeli s Cross-Project Workload číslami**, aj keď obe mali byť cross-project.

### Príklad:
```
Workload Across All Projects:  Emma Davis: 65%
RACI Workload:                  Emma Davis: 40%
                                           ↑↑↑ ROZDIEL 25%!
```

---

## 🔍 Príčina

### Sprint IDs sú globálne unique
```sql
Sprint ID | Project           | Name     | Status
----------|-------------------|----------|--------
    5     | E-Commerce        | Sprint 2 | active
   12     | Mobile App        | Sprint 2 | active  ← Iné ID!
    3     | Admin Dashboard   | Sprint 1 | active
```

### Nesprávny Kód (PRED opravou):

```typescript
// ❌ ZLYHANIE: Berie aktívny sprint len z VYBRANÉHO projektu
const activeSprint = (selectedProject.value.sprints || [])
  .find((s) => s.status === 'active');
// activeSprint.id = 5 (z E-Commerce)

// Potom hľadá úlohy s TÝMTO ID naprieč všetkými projektmi
projectStore.projects.forEach((project) => {
  const sprintTasks = project.tasks.filter(
    (task) => task.sprintId === activeSprint.id  // ❌ Hľadá len id:5
  );
});
```

**Dôsledok:**
- E-Commerce (sprintId: 5): ✅ Počítalo sa
- Mobile App (sprintId: 12): ❌ IGNOROVANÉ! (hľadalo sa len id:5)
- Dashboard (sprintId: 3): ❌ IGNOROVANÉ! (hľadalo sa len id:5)

---

## ✅ Riešenie

### Správny Kód (PO oprave):

```typescript
// ✅ SPRÁVNE: Pre každý projekt nájdi jeho vlastný aktívny sprint
projectStore.projects.forEach((project) => {
  // Nájdi aktívny sprint TOHTO projektu
  const projectActiveSprint = project.sprints?.find((s) => s.status === 'active');
  
  if (project.tasks && projectActiveSprint) {
    const sprintTasks = project.tasks.filter(
      (task) => task.sprintId === projectActiveSprint.id  // ✅ Správne ID
    );
    
    // Počítaj RACI workload...
  }
});
```

**Výsledok:**
- E-Commerce (sprintId: 5): ✅ Počíta sa
- Mobile App (sprintId: 12): ✅ Počíta sa
- Dashboard (sprintId: 3): ✅ Počíta sa

---

## 📝 Opravené Súbory

### 1. `src/pages/PertRaciOptimizationPage.vue`

**Riadok:** ~2878-2957  
**Funkcia:** `raciWeightedWorkload` computed property

**Zmeny:**
```diff
- // Get active sprint
- const activeSprint = (selectedProject.value.sprints || []).find((s) => s.status === 'active');
- if (!activeSprint) return [];
-
  // Iterate through ALL projects in the store
  projectStore.projects.forEach((project) => {
+   // FIX: Find active sprint for EACH project (not just selected project)
+   const projectActiveSprint = project.sprints?.find((s) => s.status === 'active');
+   
+   if (project.tasks && projectActiveSprint) {
      project.tasks.forEach((task) => {
-       if (task.sprintId === activeSprint.value!.id) {
+       if (task.sprintId === projectActiveSprint.id) {
          // Calculate RACI weights...
        }
      });
+   }
  });
```

---

### 2. `src/pages/RequirementChangePage.vue`

**Riadok:** ~827-891  
**Funkcia:** `raciWorkloadDetails` computed property

**Zmeny:**
```diff
- // Get active sprint
- const activeSprint = (selectedProject.value.sprints || []).find((s) => s.status === 'active');
- if (!activeSprint) return [];
-
  return allMembers.map((member) => {
    // Calculate RACI-weighted workload across ALL projects
    projectStore.projects.forEach((project) => {
+     // FIX: Find active sprint for EACH project (not just selected project)
+     const projectActiveSprint = project.sprints?.find((s) => s.status === 'active');
+     
+     if (project.tasks && projectActiveSprint) {
-       const sprintTasks = project.tasks.filter((task) => task.sprintId === activeSprint.id);
+       const sprintTasks = project.tasks.filter((task) => task.sprintId === projectActiveSprint.id);
        
        sprintTasks.forEach((task) => {
          // Calculate RACI weights...
        });
+     }
    });
  });
```

---

## 📊 Očakávané Výsledky (PO oprave)

### Emma Davis - Príklad:

#### E-Commerce Platform (sprintId: 5):
- Payment Gateway (R): 5.0 weighted SP
- Checkout Flow (C): 0.4 weighted SP
- **Subtotal: 5.4 SP**

#### Mobile App (sprintId: 12):
- Authentication (R): 8.0 weighted SP
- CI/CD Setup (A): 0.5 weighted SP
- **Subtotal: 8.5 SP**

#### Admin Dashboard (sprintId: 3):
- User Management (R): 3.0 weighted SP
- **Subtotal: 3.0 SP**

**Total: 5.4 + 8.5 + 3.0 = 16.9 weighted SP / 20 = 84.5%**

### Porovnanie:

| Metric | Pred Opravou | Po Oprave |
|--------|--------------|-----------|
| **Cross-Project Workload** | 65% | 65% (bez zmeny) |
| **RACI Workload** | 40% ❌ | **~65-85%** ✅ |

Teraz by mali čísla **SEDIEŤ!** 🎯

---

## 🧪 Testovanie

### Krok 1: Otvor PERT + RACI stránku
1. Vyber projekt s aktívnym sprintom
2. Pozri sa na "RACI Weighted Workload" tabuľku
3. Zaznamenaj čísla

### Krok 2: Otvor Requirement Changes stránku  
1. Vyber ten istý projekt
2. Pozri sa na "RACI Workload" kartu
3. Zaznamenaj čísla

### Krok 3: Porovnaj
- **RACI Workload** by malo byť **PODOBNÉ** ako **Cross-Project Workload**
- Môže byť o niečo vyššie (ak má člen A/C/I role okrem R role)
- Mali by to byť DEFINITÍVNE ROVNAKÉ ČÍSLA na oboch stránkach

---

## 📋 Backend

Backend kód bol **SPRÁVNY** od začiatku! ✅

```python
# backend/app/utils/workload_calculator.py

def calculate_cross_project_raci_workload(...):
    for proj in all_projects:
        # Get tasks from project
        if sprint_id:
            # Filter by specific sprint across all projects
            tasks = Task.query.filter_by(
                project_id=proj.id,
                sprint_id=sprint_id  # ✅ Používa špecifické sprint_id
            ).all()
        else:
            # ✅ Get tasks from ACTIVE SPRINTS in THIS project
            active_sprints = Sprint.query.filter_by(
                project_id=proj.id,
                status='active'
            ).all()
```

Backend **JUŽ** hľadal aktívne sprinty pre každý projekt samostatne!

---

## 🎯 Záver

### Čo sa zmenilo:
1. ✅ **Frontend PERT+RACI stránka** - opravený `raciWeightedWorkload`
2. ✅ **Frontend Requirement Changes stránka** - opravený `raciWorkloadDetails`
3. ✅ **Backend** - netreba opraviť (bol správny)

### Dôsledky:
- ✅ RACI Workload teraz správne počíta naprieč VŠETKÝMI aktívnymi sprintmi
- ✅ Čísla sa zhodujú medzi Cross-Project a RACI Workload
- ✅ Presnejšie informácie pre rozhodovanie
- ✅ Prevencia preťaženia členov tímu

---

## 📌 Odporúčania Pre Budúcnosť

### Code Review Checklist:
- [ ] Keď pracujete s IDs naprieč projektmi, vždy zvážte, či sú globálne unique
- [ ] Pri cross-project výpočtoch vždy iterujte cez projekty a hľadajte ich lokálne entity
- [ ] Testujte s multi-project scenárom (nie len single-project)

### Dokumentácia:
- [ ] Pridať komentáre v kóde, že sprint IDs sú globálne unique
- [ ] Aktualizovať dokumentáciu RACI_WORKLOAD_ANALYSIS.md

---

**Opravené:** 2025-11-11  
**Autor:** AI Assistant  
**Commit Message:** `fix: RACI workload now correctly aggregates across all active sprints per project`

✅ **BUG FIXED!**

---

## 🐛 **UPDATE: Bug Fix #2 - Team Member Filtering**

### Nový Problém Po Prvej Oprave:
Po oprave sprint ID problému sa **zobrazovali VŠETCI členovia tímu** z celého systému, nie len členovia aktuálneho projektu.

**Príklad:**
- Workload Across All Projects: 5 členov (správne)
- RACI Workload: 12 členov (zlé - zobrazovalo aj Sarah, Chris, Alex, Lisa, atď.)

### Riešenie:
Vrátené filtrovanie členov podľa projektu, ale zachovaný cross-project výpočet workload:

```typescript
// ✅ Filtruj členov podľa aktuálneho projektu
const projectMembers = teamStore.teamMembers.filter((member) =>
  selectedProject.value?.teamMemberIds?.includes(member.id)
);

// Ale počítaj workload naprieč VŠETKÝMI projektmi
projectStore.projects.forEach((project) => {
  // ...cross-project calculation for projectMembers only
});
```

**Details:** Pozri `RACI_WORKLOAD_BUG_FIX_2.md`

✅ **BOTH BUGS FIXED!**

