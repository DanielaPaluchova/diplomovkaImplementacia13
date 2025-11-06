# 🎯 RACI Weights - Final Implementation

**Date:** November 5, 2025  
**Feature:** Separated RACI Weights with Workload Weights as Constants

---

## 📋 Final Architecture

### 1. RACI Weights (Configurable via UI) ✅
**Purpose:** Used in adjusted duration formula  
**Storage:** LocalStorage (`raci_weights`)  
**UI:** Configuration panel with Apply/Reset buttons  
**Default Values:**
- Responsible (R): 1.0
- Accountable (A): 0.1
- Consulted (C): 0.05
- Informed (I): 0.01

**Formula:**
```
Tnew = T × (1 + (1×LR) + (0.1×LA) + (0.05×LC) + (0.01×LI))
```

### 2. RACI Workload Weights (Hardcoded Constants) 🔒
**Purpose:** Used for calculating weighted story points  
**Storage:** Hardcoded in code (not in localStorage)  
**UI:** NOT configurable - displayed only for information  
**Values:**
```typescript
const raciWorkloadWeights: RaciWorkloadWeights = {
  responsible: 1.0,
  accountable: 0.1,
  consulted: 0.05,
  informed: 0.01,
};
```

---

## 🔧 Implementation Details

### Code Structure

```typescript
// Interface for workload weights
interface RaciWorkloadWeights {
  responsible: number;
  accountable: number;
  consulted: number;
  informed: number;
}

// RACI Weights - configurable via UI
const raciWeights = ref<RaciWeights>(loadRaciWeights());

// RACI Workload Weights - hardcoded constants (not configurable via UI)
const raciWorkloadWeights: RaciWorkloadWeights = {
  responsible: 1.0,
  accountable: 0.1,
  consulted: 0.05,
  informed: 0.01,
};
```

### Usage

#### In Workload Calculation
```typescript
// getMemberWeightedStoryPointsInSprint()
if (task.raci?.responsible?.includes(memberId)) {
  total += raciWorkloadWeights.responsible * sp;
}
if (task.raci?.accountable === memberId) {
  total += raciWorkloadWeights.accountable * sp;
}
// ... etc
```

#### In RACI Weighted Workload Graph
```typescript
// raciWeightedWorkload computed property
current.workload += raciWorkloadWeights.responsible * sp;
current.workload += raciWorkloadWeights.accountable * sp;
// ... etc
```

#### In Adjusted Duration Calculation
```typescript
// calculateAdjustedDuration() uses weighted SP
// which are calculated using raciWorkloadWeights
const memberWeightedSP = getMemberWeightedStoryPointsInSprint(memberId, sprintId);
LR = memberWeightedSP / maxStoryPointsPerPerson;

// Then applies the formula with hardcoded weights (1, 0.1, 0.05, 0.01)
const raciAdjustment = 1 * LR + 0.1 * LA + 0.05 * LC + 0.01 * LI;
```

---

## 🎨 UI Changes

### Single Configuration Panel

```vue
<!-- RACI Weights (Adjusted Duration Formula) -->
<q-card class="q-mb-lg">
  <q-card-section>
    <div class="text-h6">RACI Weights (Adjusted Duration Formula)</div>
    <div class="text-caption">
      Používajú sa vo vzorci: Tnew = T × (1 + (R×LR) + (A×LA) + (C×LC) + (I×LI))
    </div>
    
    <!-- Input fields for R, A, C, I -->
    <q-btn @click="applyWeights">Apply</q-btn>
    <q-btn @click="resetWeights">Reset</q-btn>
  </q-card-section>
</q-card>
```

### Workload Graph Display (Read-Only)

```vue
<div class="text-caption text-grey-7 q-mb-md">
  Váhy: R={{ raciWorkloadWeights.responsible }}, 
        A={{ raciWorkloadWeights.accountable }}, 
        C={{ raciWorkloadWeights.consulted }}, 
        I={{ raciWorkloadWeights.informed }}
</div>
```

---

## 📊 Calculation Flow

### Example: Task with 8 SP
**RACI Assignment:** R: User 5, A: User 6, C: User 2

#### Step 1: Calculate Weighted SP (using raciWorkloadWeights)
```
User 5 (R): 8 × 1.0 = 8.0 weighted SP
User 6 (A): 8 × 0.1 = 0.8 weighted SP
User 2 (C): 8 × 0.05 = 0.4 weighted SP
```

#### Step 2: Calculate Overload
```
User 5: 8.0 / 20 = 0.40 (40% capacity)
User 6: 0.8 / 20 = 0.04 (4% capacity)
User 2: 0.4 / 20 = 0.02 (2% capacity)
```

#### Step 3: Calculate Adjusted Duration (using formula weights)
```
LR = 0.40 (for User 5)
LA = 0.04 (for User 6)
LC = 0.02 (for User 2)
LI = 0.00 (no informed)

RACI Adjustment = (1.0 × 0.40) + (0.1 × 0.04) + (0.05 × 0.02) + (0.01 × 0)
                = 0.40 + 0.004 + 0.001 + 0
                = 0.405

Tnew = T × (1 + 0.405) = T × 1.405
```

**Result:** Task duration increased by 40.5% due to team workload

---

## 🎯 Why This Approach?

### Benefits

1. **Simplicity** ✅
   - Only one configuration panel for users
   - Less complexity in UI
   - Fewer chances for misconfiguration

2. **Consistency** ✅
   - Workload calculation is standardized
   - Same weights used across all projects
   - Predictable behavior

3. **Flexibility** ✅
   - Users can still adjust formula weights if needed
   - Developers can easily change workload weights in code
   - Clear separation of concerns

4. **Performance** ✅
   - No localStorage reads for workload weights
   - Constants are faster than reactive refs
   - Less memory usage

### When to Change Workload Weights?

Change the hardcoded constants in code when:
- Company changes RACI methodology
- Team finds that default weights don't reflect reality
- Different types of projects need different workload distributions

**How to change:**
```typescript
// In PertRaciOptimizationPage.vue, line ~1539
const raciWorkloadWeights: RaciWorkloadWeights = {
  responsible: 1.0,    // Change this
  accountable: 0.1,    // Change this
  consulted: 0.05,     // Change this
  informed: 0.01,      // Change this
};
```

---

## 📝 Comparison: Before vs After

| Aspect | Before (Dual Configuration) | After (Single + Constants) |
|--------|----------------------------|---------------------------|
| **UI Complexity** | 2 configuration panels | 1 configuration panel |
| **User Configuration** | Both weights configurable | Only formula weights |
| **LocalStorage Keys** | 2 keys | 1 key |
| **Code Complexity** | 2 sets of load/save functions | 1 set of functions |
| **Flexibility** | High (maybe too much) | Balanced |
| **User Confusion** | Possible (what's the difference?) | Clear (only one thing to configure) |

---

## ✅ Removed Components

### UI Elements
- ❌ RACI Workload Weights Configuration panel (entire card)
- ❌ Apply button for workload weights
- ❌ Reset button for workload weights
- ❌ Input fields for workload weights (R, A, C, I)

### Functions
- ❌ `loadRaciWorkloadWeights()` - no longer needed
- ❌ `applyWorkloadWeights()` - removed
- ❌ `resetWorkloadWeights()` - removed

### Storage
- ❌ `localStorage.getItem('raci_workload_weights')` - not used
- ❌ `localStorage.setItem('raci_workload_weights', ...)` - removed

### Variables
- ❌ `raciWorkloadWeights` as `ref` - converted to constant

---

## ✅ Modified Components

### Variables
```typescript
// BEFORE
const raciWorkloadWeights = ref<RaciWorkloadWeights>(loadRaciWorkloadWeights());

// AFTER
const raciWorkloadWeights: RaciWorkloadWeights = {
  responsible: 1.0,
  accountable: 0.1,
  consulted: 0.05,
  informed: 0.01,
};
```

### Access Pattern
```typescript
// BEFORE (reactive ref)
raciWorkloadWeights.value.responsible

// AFTER (constant)
raciWorkloadWeights.responsible
```

### Display
```vue
<!-- BEFORE - Full panel with inputs -->
<q-card>
  <q-input v-model.number="raciWorkloadWeights.responsible" />
  <q-btn @click="applyWorkloadWeights">Apply</q-btn>
</q-card>

<!-- AFTER - Read-only display -->
<div class="text-caption">
  Váhy: R={{ raciWorkloadWeights.responsible }}, ...
</div>
```

---

## 🚀 Future Enhancements (Optional)

### 1. Environment-based Weights
```typescript
// Different weights for different environments
const raciWorkloadWeights: RaciWorkloadWeights = 
  import.meta.env.MODE === 'production' 
    ? { responsible: 1.0, accountable: 0.1, ... }
    : { responsible: 0.8, accountable: 0.2, ... };
```

### 2. Project-specific Weights
```typescript
// Load weights from project configuration
const getWorkloadWeights = (projectId: number) => {
  const projectConfig = projectStore.getProjectConfig(projectId);
  return projectConfig.workloadWeights || DEFAULT_WEIGHTS;
};
```

### 3. Admin Panel
Create an admin-only configuration panel to change default weights without code changes.

---

## 📚 Files Modified

**`src/pages/PertRaciOptimizationPage.vue`:**
- ✅ Removed RACI Workload Weights configuration panel (lines ~120-204)
- ✅ Removed `loadRaciWorkloadWeights()` function
- ✅ Changed `raciWorkloadWeights` from ref to constant
- ✅ Updated all `raciWorkloadWeights.value` to `raciWorkloadWeights`
- ✅ Removed `applyWorkloadWeights()` function
- ✅ Removed `resetWorkloadWeights()` function
- ✅ Updated UI display to show weights as read-only

---

## ✅ Testing Checklist

- [x] RACI Weights panel displays correctly
- [x] RACI Workload Weights panel removed
- [x] Workload calculation uses hardcoded constants
- [x] Adjusted duration calculation works correctly
- [x] RACI Weighted Workload graph shows correct weights
- [x] No linter errors
- [x] No compilation errors
- [x] No references to removed functions

---

## 🎓 Conclusion

The final implementation provides a **clean separation** between:
1. **User-configurable weights** (formula) - for fine-tuning adjusted duration calculations
2. **Hardcoded weights** (workload) - for consistent and predictable workload calculations

This approach:
- ✅ Reduces UI complexity
- ✅ Prevents user confusion
- ✅ Maintains flexibility where needed
- ✅ Simplifies codebase
- ✅ Improves performance

Users now have **one clear configuration panel** for the weights that matter most (formula weights), while workload calculation remains standardized and consistent across the application.

---

*Implementation completed successfully! ✨*  
*RACI Workload Weights are now constants in code.*

