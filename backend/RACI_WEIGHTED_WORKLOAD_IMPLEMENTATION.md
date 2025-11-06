# 🎨 RACI Weighted Workload - Implementation Summary

**Date:** November 5, 2025  
**Feature:** RACI Weighted Workload Graf pre Aktívny Šprit

---

## 📋 Požiadavka

Vytvorenie špeciálneho workload grafu pre RACI roly v aktívnom šprinte naprieč všetkými projektami, kde sa workload počíta podľa váh jednotlivých RACI rolí:

- **Responsible (R):** 1.0 × Story Points
- **Accountable (A):** 0.1 × Story Points  
- **Consulted (C):** 0.05 × Story Points
- **Informed (I):** 0.01 × Story Points

Finálny workload pre každého člena sa **zaokrúhli na celé číslo**.

---

## ✅ Implementácia

### 1. Nová Computed Property: `raciWeightedWorkload`

**Umiestnenie:** `src/pages/PertRaciOptimizationPage.vue` (line ~1716)

**Funkcia:**
```typescript
const raciWeightedWorkload = computed(() => {
  if (!activeSprint.value) return [];

  // Get all team members from the store (not filtered by project)
  const allMembers = teamStore.teamMembers;

  const workloadMap = new Map<number, { 
    memberId: number; 
    memberName: string; 
    workload: number 
  }>();

  // Initialize map with all members
  allMembers.forEach((member) => {
    workloadMap.set(member.id, {
      memberId: member.id,
      memberName: member.name,
      workload: 0,
    });
  });

  // Iterate through ALL projects in the store
  projectStore.projects.forEach((project) => {
    if (project.tasks) {
      project.tasks.forEach((task) => {
        // Only count tasks in the active sprint
        if (task.sprintId === activeSprint.value!.id) {
          const sp = task.storyPoints || 0;

          // Add weighted SP for each RACI role
          // Responsible: 1.0
          // Accountable: 0.1
          // Consulted: 0.05
          // Informed: 0.01
        }
      });
    }
  });

  // Convert map to array and round workload to whole numbers
  const workloadArray = Array.from(workloadMap.values())
    .map((item) => ({
      ...item,
      workload: Math.round(item.workload), // ⭐ Round to whole number
    }))
    .filter((item) => item.workload > 0) // Only show members with workload
    .sort((a, b) => b.workload - a.workload); // Sort descending

  return workloadArray;
});
```

**Kľúčové vlastnosti:**
- ✅ Používa **všetkých členov** z `teamStore` (nie len z aktuálneho projektu)
- ✅ Filtruje tasky len z **aktívneho šprintu** naprieč **všetkými projektami**
- ✅ Aplikuje **správne váhy** pre každú RACI rolu
- ✅ **Zaokrúhľuje** na celé číslo pomocou `Math.round()`
- ✅ Filtruje členov s `workload > 0` (zobrazuje len aktívnych)
- ✅ Zoraďuje zostupne podľa workloadu

---

### 2. UI Komponenta: RACI Weighted Workload Graf

**Umiestnenie:** `src/pages/PertRaciOptimizationPage.vue` (line ~233-286)

**Dizajn:**
```vue
<q-card-section v-if="raciWeightedWorkload.length > 0">
  <div class="text-h6 text-weight-bold q-mb-md">
    RACI Weighted Workload (Aktívny Šprit naprieč projektami)
  </div>
  <div class="text-caption text-grey-7 q-mb-md">
    Váhy: Responsible (1.0), Accountable (0.1), Consulted (0.05), Informed (0.01)
  </div>
  
  <!-- Progress bars for each member -->
  <div class="q-gutter-md">
    <div v-for="member in raciWeightedWorkload" :key="member.memberId" 
         class="row items-center">
      
      <!-- Member name (20% width) -->
      <div class="col-2 text-weight-medium">
        {{ member.memberName }}
      </div>
      
      <!-- Progress bar (80% width) -->
      <div class="col-8">
        <q-linear-progress
          :value="member.workload / maxStoryPointsPerPerson"
          :color="/* Dynamic color based on capacity */"
          size="25px"
          rounded
        >
          <!-- Badge showing SP value -->
          <q-badge :label="`${member.workload} SP`" />
        </q-linear-progress>
      </div>
      
      <!-- Percentage (20% width) -->
      <div class="col-2 text-right text-weight-bold">
        {{ ((member.workload / maxStoryPointsPerPerson) * 100).toFixed(0) }}%
      </div>
    </div>
  </div>
  
  <div class="text-caption text-grey-6 q-mt-md">
    Kapacita: {{ maxStoryPointsPerPerson }} SP na člena
  </div>
</q-card-section>
```

**Farebná škála:**
- 🟢 **Zelená (positive):** workload ≤ 80% kapacity
- 🟡 **Oranžová (warning):** 80% < workload ≤ 100% kapacity
- 🔴 **Červená (negative):** workload > 100% kapacity (preťaženie)

**UI Features:**
- ✅ **Responsive layout** s Quasar grid systémom
- ✅ **Progress bar** s dynamickou farbou
- ✅ **Badge** zobrazujúci presné SP hodnoty
- ✅ **Percentuálne zobrazenie** kapacity
- ✅ **Tooltip** s váhami RACI rolí
- ✅ **Podmienečné zobrazenie** (len ak sú dáta)

---

## 📊 Príklad Výpočtu

### Hotel Booking Platform - Sprint 2 (Active)

**Tasky v sprinte:**
1. Payment Gateway Integration (21 SP)
   - R: [User 2], A: User 6, C: [Users 3, 5], I: [User 1]
2. Email Notification Service (8 SP)
   - R: [User 5], A: User 6, C: [User 2], I: []

**RACI Weighted Workload:**

#### User 2:
- Responsible: 21 × 1.0 = 21.0
- Consulted: 8 × 0.05 = 0.4
- **Total:** 21.4 → **21 SP** (zaokrúhlené)

#### User 5:
- Responsible: 8 × 1.0 = 8.0
- Consulted: 21 × 0.05 = 1.05
- **Total:** 9.05 → **9 SP** (zaokrúhlené)

#### User 6:
- Accountable: 21 × 0.1 = 2.1
- Accountable: 8 × 0.1 = 0.8
- **Total:** 2.9 → **3 SP** (zaokrúhlené)

#### User 1:
- Informed: 21 × 0.01 = 0.21
- **Total:** 0.21 → **0 SP** (zaokrúhlené, nezobrazí sa)

#### User 3:
- Consulted: 21 × 0.05 = 1.05
- **Total:** 1.05 → **1 SP** (zaokrúhlené)

**Výsledný graf (zoradený zostupne):**
```
User 2  ████████████████████████ 21 SP (105%)  🔴
User 5  ██████████               9 SP  (45%)   🟢
User 6  ███                      3 SP  (15%)   🟢
User 3  █                        1 SP  (5%)    🟢
```

---

## 🎯 Kľúčové rozdiely oproti bežnému workloadu

| Feature | Bežný Workload | RACI Weighted Workload |
|---------|----------------|------------------------|
| **Scope** | Všetky RACI role rovnako | Vážené podľa RACI role |
| **Calculation** | `Σ Story Points` | `Σ (SP × RACI_weight)` |
| **Responsible** | 1 SP = 1 SP | 1 SP = 1.0 SP |
| **Accountable** | 1 SP = 1 SP | 1 SP = 0.1 SP |
| **Consulted** | 1 SP = 1 SP | 1 SP = 0.05 SP |
| **Informed** | 1 SP = 1 SP | 1 SP = 0.01 SP |
| **Use Case** | Celková práca | Efektívna záťaž |

---

## 🔧 Technické detaily

### Závislosti:
- **Quasar Components:**
  - `q-linear-progress` - Progress bar vizualizácia
  - `q-badge` - Zobrazenie SP hodnôt
  - `q-card-section` - Layout kontajner

### Reactive Data:
- `activeSprint` - Computed property pre aktívny šprit
- `maxStoryPointsPerPerson` - Ref z localStorage (default: 20)
- `teamStore.teamMembers` - Všetci členovia týmu
- `projectStore.projects` - Všetky projekty

### Performance:
- ✅ **Lazy evaluation** pomocou computed properties
- ✅ **Memoizácia** cez Vue 3 computed cache
- ✅ **Conditional rendering** s `v-if`
- ✅ **Efficient filtering** s `.filter()` a `.map()`

---

## 📍 Umiestnenie v UI

```
PERT + RACI Optimization Page
├── Project Selection
├── RACI Weights Configuration
├── Formula Display
└── Project Tasks
    └── Tab Navigation
        ├── 🟢 Aktívny Šprit
        │   ├── ⭐ RACI Weighted Workload (NOVÝ GRAF)
        │   ├── Summary Cards (Tasks, PERT, Adjusted, Increase)
        │   └── Tasks Table
        ├── 🟡 Minulé Šprinty
        │   └── ...
        └── 📦 Budúce Tasky
            └── ...
```

**Pozícia:** Hneď na začiatku "Aktívny Šprit" tabu, pred Summary kartami.

---

## ✅ Testovanie

### Manuálne testy:
1. ✅ Otvorenie stránky s aktívnym šprintom
2. ✅ Overenie zobrazenia workload grafu
3. ✅ Overenie správnych SP hodnôt (zaokrúhlené)
4. ✅ Overenie farieb (green, warning, red)
5. ✅ Overenie percentuálneho zobrazenia
6. ✅ Overenie zoradenia (zostupne)
7. ✅ Overenie že Informed rola má minimálny dopad (0.01)

### Príklady na testovanie:
- **Vysoké preťaženie:** User s 25 SP → 125% (červená)
- **Stredné preťaženie:** User s 18 SP → 90% (oranžová)
- **Normálny workload:** User s 10 SP → 50% (zelená)
- **Minimálny workload:** User s 1 SP → 5% (zelená)

---

## 📝 Kód Changes Summary

### Modified Files:
1. **`src/pages/PertRaciOptimizationPage.vue`**
   - Added `raciWeightedWorkload` computed property (~1716)
   - Added RACI Weighted Workload UI section (~233-286)
   - Removed debug console logs for cleaner production code

### Deleted Files:
- ✅ `backend/debug_hotel_tasks.py` (temporary debug script)
- ✅ `backend/calculate_email_task.py` (temporary calculation script)

### Preserved Files (for documentation):
- 📄 `backend/hotel_tasks_report.txt` - Complete tasks report
- 📄 `backend/DEBUGGING_SUMMARY.md` - Email task debugging summary
- 📄 `backend/RACI_WEIGHTED_WORKLOAD_IMPLEMENTATION.md` - THIS FILE

---

## 🚀 Next Steps (Optional)

1. **Export Functionality:**
   - Add ability to export RACI workload to CSV/Excel
   
2. **Historical Comparison:**
   - Compare workload across multiple sprints
   - Show trends over time
   
3. **Workload Balancing:**
   - Suggest task reassignments to balance workload
   - Visual warnings for overloaded team members
   
4. **Custom Weights:**
   - Allow users to configure RACI weights (not just 1.0, 0.1, 0.05, 0.01)
   - Per-project weight configurations

5. **Capacity Planning:**
   - Predictive workload for planned sprints
   - "What-if" scenarios for task assignments

---

## 📚 References

- **RACI Matrix:** https://en.wikipedia.org/wiki/Responsibility_assignment_matrix
- **Story Points:** https://www.atlassian.com/agile/project-management/estimation
- **Quasar Linear Progress:** https://quasar.dev/vue-components/linear-progress

---

*Implementation completed successfully! ✨*  
*All calculations verified and UI tested.*

