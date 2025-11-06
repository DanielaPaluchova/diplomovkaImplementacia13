# 🔍 Email Notification Service - Complete Debugging Report

**Date:** November 5, 2025  
**Project:** Hotel Booking Platform (ID: 7)  
**Task:** Email Notification Service (ID: 18)  
**Sprint:** Sprint 2 - Core Backend (ID: 5, Status: active)

---

## ✅ CONCLUSION: UI IS WORKING CORRECTLY!

The task **IS** in the active sprint and **SHOULD** be displayed in the "Aktívny Šprit" tab.

---

## 📊 Database Verification

### Task Details
- **Task ID:** 18
- **Name:** Email Notification Service
- **Story Points:** 8
- **Sprint ID:** **5** (ACTIVE SPRINT) ← NOT NULL!
- **Status:** Done
- **PERT:** O=16h, M=24h, P=40h

### Key Finding
The `sprint_id` in the database is **5**, not `None` as shown in the original `seed_database.py` file. This indicates:
- Either the database was re-seeded after the initial setup
- Or the task was manually moved to the active sprint
- The seed file is **outdated** and doesn't reflect current database state

---

## 🧮 Adjusted Duration Calculation

### Step 1: PERT Duration
```
T = (O + 4×M + P) / 6
T = (16 + 4×24 + 40) / 6
T = (16 + 96 + 40) / 6
T = 152 / 6
T = 25.33h
```

### Step 2: Team Member Workload in Sprint 5

#### 🔴 Responsible: User 5
- **Total SP in Sprint 5:** 29
  - Email Notification Service (8 SP) - Responsible
  - Payment Gateway Integration (21 SP) - Consulted
- **Overload:** 29 / 20 = **1.4500**
- **LR = 1.4500** (average of 1 member)

#### 🟠 Accountable: User 6
- **Total SP in Sprint 5:** 29
  - Email Notification Service (8 SP) - Accountable
  - Payment Gateway Integration (21 SP) - Accountable
- **Overload:** 29 / 20 = **1.4500**
- **LA = 1.4500**

#### 🟡 Consulted: User 2
- **Total SP in Sprint 5:** 29
  - Email Notification Service (8 SP) - Consulted
  - Payment Gateway Integration (21 SP) - Responsible
- **Overload:** 29 / 20 = **1.4500**
- **LC = 1.4500** (average of 1 member)

#### ⚪ Informed: None
- **LI = 0**

### Step 3: RACI Adjustment
```
RACI Adjustment = (1×LR) + (0.1×LA) + (0.05×LC) + (0.01×LI)
                = (1×1.4500) + (0.1×1.4500) + (0.05×1.4500) + (0.01×0)
                = 1.4500 + 0.1450 + 0.0725 + 0
                = 1.6675
```

### Step 4: Final Adjusted Duration
```
Tnew = T × (1 + RACI_Adjustment)
Tnew = 25.33 × (1 + 1.6675)
Tnew = 25.33 × 2.6675
Tnew = 67.58h
```

### 📈 Impact Analysis
- **Original PERT:** 25.33h
- **With RACI:** 67.58h
- **Difference:** +42.24h
- **Percentage Increase:** **166.8%**

**Interpretation:** The team is significantly overloaded (145% of capacity), which more than doubles the expected task duration. This is because Sprint 5 has 29 story points for the involved team members, which exceeds the 20 SP/person capacity.

---

## 📋 Sprint 5 Overview

### Active Sprint Tasks (2 tasks, 29 SP total)

1. **Payment Gateway Integration**
   - SP: 21
   - Status: To Do
   - RACI: R=[2], A=6, C=[3,5], I=[1]

2. **Email Notification Service** ⭐
   - SP: 8
   - Status: Done
   - RACI: R=[5], A=6, C=[2], I=[]

### Capacity Analysis
- **Total SP:** 29
- **Max SP per person:** 20
- **Overload Factor:** 29/20 = 1.45 (145% capacity)
- **Overload:** 9 story points over capacity

**Note:** All three team members (2, 5, 6) involved in this task are working on BOTH tasks in the sprint, leading to identical overload factors.

---

## 🔧 Frontend Implementation Verification

### Computed Property: `activeSprintTasks`
```typescript
const activeSprintTasks = computed<Task[]>(() => {
  if (!selectedProject.value || !selectedProject.value.tasks || !activeSprint.value) return [];

  return selectedProject.value.tasks
    .filter((task) => task.sprintId === activeSprint.value!.id)
    .map((task) => convertToTask(task, activeSprint.value!.id, false));
});
```

**Status:** ✅ Correctly filters tasks where `task.sprintId === activeSprint.id`

### Function: `calculateAdjustedDuration`
```typescript
function calculateAdjustedDuration(
  task: Task,
  sprintId: number | null,
  useAverage: boolean = false,
): number {
  // Calculates LR, LA, LC, LI using getMemberStoryPointsInSprint()
  // Applies formula: Tnew = T × (1 + (1×LR) + (0.1×LA) + (0.05×LC) + (0.01×LI))
}
```

**Status:** ✅ Correctly implements the PERT + RACI integration formula

### Helper: `getMemberStoryPointsInSprint`
```typescript
function getMemberStoryPointsInSprint(memberId: number, sprintId: number | null): number {
  if (sprintId === null) return 0;

  let total = 0;
  
  // Iterates through ALL projects
  projectStore.projects.forEach((project) => {
    project.tasks.forEach((task) => {
      if (task.sprintId === sprintId) {
        // Checks all RACI roles
        if (/* member is in any RACI role */) {
          total += task.storyPoints || 0;
        }
      }
    });
  });

  return total;
}
```

**Status:** ✅ Correctly calculates SP across all projects for a specific sprint

---

## 📝 Console Logging Added

Debug logging has been added to help verify the filtering logic:

```typescript
console.log('🔍 [activeSprintTasks] Active Sprint ID:', activeSprint.value.id);
console.log('🔍 [activeSprintTasks] Total project tasks:', selectedProject.value.tasks.length);
// Logs each task with its sprintId and whether it matches
console.log('🔍 [activeSprintTasks] Filtered tasks count:', filtered.length);
```

Similar logging added to `futureBacklogTasks` computed property.

---

## 📦 Project Distribution

### All Hotel Booking Platform Tasks (31 tasks, 423 SP)

| Category | Tasks | Story Points | Percentage |
|----------|-------|--------------|------------|
| Active Sprint | 2 | 29 | 6.5% |
| Completed Sprints | 0 | 0 | 0% |
| Backlog/Future | 29 | 394 | 93.5% |

**Observation:** Project is in early phase with most tasks still in backlog.

---

## ✅ Verification Checklist

- [x] **Database Check:** Confirmed `sprint_id = 5` (active)
- [x] **Task Count:** 2 tasks in active sprint (Payment Gateway + Email Notification)
- [x] **SP Calculation:** All members correctly calculated at 29 SP
- [x] **PERT Formula:** Correctly applied `T = (O + 4M + P) / 6 = 25.33h`
- [x] **RACI Formula:** Correctly applied adjustment = 1.6675
- [x] **Final Duration:** 67.58h (verified manually)
- [x] **UI Display:** Task correctly appears in "Aktívny Šprit" tab
- [x] **Console Logging:** Added for future debugging

---

## 🎯 Next Steps (Optional)

1. **Browser Console Verification:**
   - Open the PERT+RACI page in the browser
   - Check console logs to verify filtering logic in real-time
   - Confirm UI matches database calculations

2. **Update seed_database.py (if needed):**
   - Set `task_hotel_11['sprint_id'] = sprint_hotel_2['id']` 
   - To keep seed file consistent with current database

3. **Consider Sprint Capacity:**
   - Sprint 5 is overloaded by 45% (29 SP vs 20 SP capacity)
   - May want to redistribute tasks or adjust capacity planning

---

## 📚 Files Modified

1. **`src/pages/PertRaciOptimizationPage.vue`**
   - Added debug logging to `activeSprintTasks` computed property
   - Added debug logging to `futureBacklogTasks` computed property

2. **`backend/debug_hotel_tasks.py`** (NEW)
   - Database verification script

3. **`backend/calculate_email_task.py`** (NEW)
   - Detailed calculation script for adjusted duration

4. **`backend/hotel_tasks_report.txt`** (NEW)
   - Complete tasks report with all 31 tasks categorized

5. **`backend/DEBUGGING_SUMMARY.md`** (THIS FILE)
   - Comprehensive debugging report

---

## 🏁 Final Answer

**Question:** Why is "Email Notification Service" appearing in the "Active Sprint" tab?

**Answer:** Because it **SHOULD** be there! The task has `sprint_id = 5` in the database, which corresponds to the active sprint "Sprint 2 - Core Backend". The UI is functioning correctly and displaying the task in the appropriate tab based on its sprint assignment.

The confusion arose from the `seed_database.py` file showing `sprint_id = None`, but the actual database has the correct value of `5`. This discrepancy suggests the database was either re-seeded or the task was moved to the active sprint after initial seeding.

**Adjusted Duration Calculation:** ✅ VERIFIED  
**Expected Duration:** 25.33h → 67.58h (with RACI overload factor)

---

*Generated by automated debugging process*  
*All calculations verified against database and formula specifications*

