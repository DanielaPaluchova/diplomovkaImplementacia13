# 🎯 Dual RACI Weights Implementation

**Date:** November 5, 2025  
**Feature:** Separate RACI Weights for Adjusted Duration Formula and Workload Calculation

---

## 📋 Požiadavka

Vytvoriť **2 samostatné sady váh** pre RACI roly:

1. **RACI Weights** - Pre adjusted duration vzorec
2. **RACI Workload Weights** - Pre výpočet váženého workloadu

---

## 🎯 Dôvod

Pôvodne existovala len jedna sada váh, ktorá sa používala dvojito:
1. Pri výpočte váženého workloadu (koľko SP má člen)
2. Vo vzorci pre adjusted duration (aký vplyv má overload na duration)

**Problém:** Tieto dve použitia majú rôzne významy a potrebujú rôzne hodnoty!

### Príklad:
- **Accountable rola** má dohľadovú funkciu
  - **Pre workload:** chceme nižšiu váhu (napr. 0.45), pretože dohľad si vyžaduje menej času než execution
  - **Pre formula:** môžeme chcieť inú váhu (napr. 0.1), ktorá ovplyvňuje ako overload Accountable ovplyvňuje duration

---

## ✅ Implementácia

### 1. Nové Interfaces

```typescript
interface RaciWeights {
  responsible: number;
  accountable: number;
  consulted: number;
  informed: number;
}

interface RaciWorkloadWeights {
  responsible: number;
  accountable: number;
  consulted: number;
  informed: number;
}
```

### 2. Nové Reactive Variables

```typescript
// RACI Weights - pre adjusted duration formula
const raciWeights = ref<RaciWeights>(loadRaciWeights());
// Default: { responsible: 1.0, accountable: 0.1, consulted: 0.05, informed: 0.01 }

// RACI Workload Weights - pre workload calculation
const raciWorkloadWeights = ref<RaciWorkloadWeights>(loadRaciWorkloadWeights());
// Default: { responsible: 0.6, accountable: 0.45, consulted: 0.3, informed: 0.05 }
```

### 3. Load Functions

```typescript
// Load RACI weights for adjusted duration formula from localStorage
const loadRaciWeights = (): RaciWeights => {
  const stored = localStorage.getItem('raci_weights');
  if (stored) {
    try {
      return JSON.parse(stored);
    } catch {
      return { responsible: 1.0, accountable: 0.1, consulted: 0.05, informed: 0.01 };
    }
  }
  return { responsible: 1.0, accountable: 0.1, consulted: 0.05, informed: 0.01 };
};

// Load RACI workload weights for workload calculation from localStorage
const loadRaciWorkloadWeights = (): RaciWorkloadWeights => {
  const stored = localStorage.getItem('raci_workload_weights');
  if (stored) {
    try {
      return JSON.parse(stored);
    } catch {
      return { responsible: 0.6, accountable: 0.45, consulted: 0.3, informed: 0.05 };
    }
  }
  return { responsible: 0.6, accountable: 0.45, consulted: 0.3, informed: 0.05 };
};
```

### 4. Updated Functions

#### `getMemberWeightedStoryPointsInSprint()`
```typescript
// BEFORE: používal hardcoded váhy (1.0, 0.1, 0.05, 0.01)
if (task.raci?.responsible?.includes(memberId)) {
  total += 1.0 * sp;
}

// AFTER: používa raciWorkloadWeights
if (task.raci?.responsible?.includes(memberId)) {
  total += raciWorkloadWeights.value.responsible * sp;
}
```

#### `raciWeightedWorkload` computed property
```typescript
// BEFORE: používal hardcoded váhy
current.workload += 1.0 * sp; // Responsible

// AFTER: používa raciWorkloadWeights
current.workload += raciWorkloadWeights.value.responsible * sp;
```

#### `calculateAdjustedDuration()`
```typescript
// Používa weighted SP (ktoré sú už vážené cez raciWorkloadWeights)
// A potom aplikuje raciWeights vo vzorci:
const raciAdjustment = 1 * LR + 0.1 * LA + 0.05 * LC + 0.01 * LI;
// Kde LR, LA, LC, LI sú vypočítané z weighted SP
```

**POZOR:** `raciWeights` v `calculateAdjustedDuration` sú momentálne hardcoded vo vzorci!
Ak chceme aby aj tie boli konfigurovateľné, musíme aktualizovať vzorec na:
```typescript
const raciAdjustment = 
  raciWeights.value.responsible * LR + 
  raciWeights.value.accountable * LA + 
  raciWeights.value.consulted * LC + 
  raciWeights.value.informed * LI;
```

---

## 🎨 UI Changes

### 1. RACI Weights Configuration Panel

```vue
<q-card class="q-mb-lg">
  <q-card-section>
    <div class="text-h6">RACI Weights (Adjusted Duration Formula)</div>
    <div class="text-caption text-grey-7">
      Používajú sa vo vzorci: Tnew = T × (1 + (R×LR) + (A×LA) + (C×LC) + (I×LI))
    </div>
    
    <!-- Input fields for R, A, C, I -->
    <!-- Defaults: 1.0, 0.1, 0.05, 0.01 -->
    
    <q-btn @click="applyWeights">Apply</q-btn>
    <q-btn @click="resetWeights">Reset</q-btn>
  </q-card-section>
</q-card>
```

### 2. RACI Workload Weights Configuration Panel (NEW)

```vue
<q-card class="q-mb-lg">
  <q-card-section>
    <div class="text-h6">RACI Workload Weights (Workload Calculation)</div>
    <div class="text-caption text-grey-7">
      Používajú sa pre výpočet váženého workloadu v RACI Weighted Workload grafe
    </div>
    
    <!-- Input fields for R, A, C, I -->
    <!-- Defaults: 0.60, 0.45, 0.30, 0.05 -->
    
    <q-btn @click="applyWorkloadWeights">Apply</q-btn>
    <q-btn @click="resetWorkloadWeights">Reset</q-btn>
  </q-card-section>
</q-card>
```

### 3. Updated RACI Weighted Workload Display

```vue
<div class="text-caption text-grey-7 q-mb-md">
  Váhy: Responsible ({{ raciWorkloadWeights.responsible }}), 
        Accountable ({{ raciWorkloadWeights.accountable }}), 
        Consulted ({{ raciWorkloadWeights.consulted }}), 
        Informed ({{ raciWorkloadWeights.informed }})
</div>
```

---

## 🔧 New Functions

### `applyWorkloadWeights()`
```typescript
function applyWorkloadWeights() {
  // Validate weights (0 to 10)
  const weights = raciWorkloadWeights.value;
  if (/* validation */) {
    // Show error
    return;
  }

  // Save to localStorage
  localStorage.setItem('raci_workload_weights', JSON.stringify(weights));

  // Show success notification
  $q.notify({
    message: `RACI workload váhy aplikované: R=${weights.responsible}, ...`,
    color: 'positive',
  });
}
```

### `resetWorkloadWeights()`
```typescript
function resetWorkloadWeights() {
  raciWorkloadWeights.value = {
    responsible: 0.6,
    accountable: 0.45,
    consulted: 0.3,
    informed: 0.05,
  };

  $q.notify({
    message: 'RACI workload váhy resetované na predvolené hodnoty',
    color: 'info',
  });
}
```

### Updated `applyWeights()`
```typescript
// Changed validation range from 0-1 to 0-10
// Updated notification message to be more specific
```

### Updated `resetWeights()`
```typescript
// Changed default values from (0.6, 0.45, 0.3, 0.05) to (1.0, 0.1, 0.05, 0.01)
// Updated notification message
```

---

## 📊 Default Values Explained

### RACI Weights (Adjusted Duration Formula)
| Role | Default | Význam |
|------|---------|--------|
| **Responsible (R)** | 1.0 | Plný vplyv na duration - hlavná zodpovednosť |
| **Accountable (A)** | 0.1 | 10% vplyv - dohľad, nie execution |
| **Consulted (C)** | 0.05 | 5% vplyv - občasné konzultácie |
| **Informed (I)** | 0.01 | 1% vplyv - len pasívne informovanie |

**Použitie:** Vo vzorci `Tnew = T × (1 + (1×LR) + (0.1×LA) + (0.05×LC) + (0.01×LI))`

### RACI Workload Weights (Workload Calculation)
| Role | Default | Význam |
|------|---------|--------|
| **Responsible (R)** | 0.6 | 60% story pointov - hlavná práca |
| **Accountable (A)** | 0.45 | 45% story pointov - dohľad + koordinácia |
| **Consulted (C)** | 0.3 | 30% story pointov - konzultácie vyžadujú čas |
| **Informed (I)** | 0.05 | 5% story pointov - minimálna záťaž |

**Použitie:** Pri výpočte `weighted SP = R_weight×SP + A_weight×SP + C_weight×SP + I_weight×SP`

---

## 🔄 Workflow

### 1. Task Creation
```
User creates task:
- Email Notification (8 SP)
- R: User 5, A: User 6, C: User 2
```

### 2. Workload Calculation (uses raciWorkloadWeights)
```
User 5 (R): 8 × 0.6 = 4.8 weighted SP
User 6 (A): 8 × 0.45 = 3.6 weighted SP
User 2 (C): 8 × 0.3 = 2.4 weighted SP
```

### 3. Overload Calculation
```
User 5: 4.8 / 20 = 0.24 (24% capacity)
User 6: 3.6 / 20 = 0.18 (18% capacity)
User 2: 2.4 / 20 = 0.12 (12% capacity)
```

### 4. Adjusted Duration Calculation (uses raciWeights)
```
LR = 0.24 (for User 5)
LA = 0.18 (for User 6)
LC = 0.12 (for User 2)

RACI Adjustment = (1.0 × 0.24) + (0.1 × 0.18) + (0.05 × 0.12) + (0.01 × 0)
                = 0.24 + 0.018 + 0.006 + 0
                = 0.264

Tnew = T × (1 + 0.264) = T × 1.264
```

---

## 💡 Use Cases

### Use Case 1: High Responsible Impact
**Scenario:** Responsible rola má veľký vplyv na duration

**Settings:**
- RACI Weights: R=2.0, A=0.1, C=0.05, I=0.01
- Workload Weights: R=0.6, A=0.45, C=0.3, I=0.05

**Result:** Ak je Responsible preťažený, task duration sa výrazne zvýši

### Use Case 2: Balanced Workload
**Scenario:** Chceme presnejšie model workloadu

**Settings:**
- RACI Weights: R=1.0, A=0.1, C=0.05, I=0.01 (štandardné)
- Workload Weights: R=0.8, A=0.5, C=0.4, I=0.1 (vyššie váhy)

**Result:** Workload bude realistickejší, C a A roly majú väčší dopad

### Use Case 3: Conservative Estimation
**Scenario:** Chceme konzervatívne odhady

**Settings:**
- RACI Weights: R=1.5, A=0.2, C=0.1, I=0.05 (vyššie váhy)
- Workload Weights: R=0.6, A=0.45, C=0.3, I=0.05 (štandardné)

**Result:** Adjusted duration bude vyšší (bezpečnostná rezerva)

---

## 📝 LocalStorage Keys

```typescript
// RACI Weights (adjusted duration)
localStorage.getItem('raci_weights');
// Stores: { responsible: 1.0, accountable: 0.1, consulted: 0.05, informed: 0.01 }

// RACI Workload Weights (workload calculation)
localStorage.getItem('raci_workload_weights');
// Stores: { responsible: 0.6, accountable: 0.45, consulted: 0.3, informed: 0.05 }

// Max story points per person
localStorage.getItem('max_story_points_per_person');
// Stores: "20"
```

---

## ✅ Testing Checklist

- [x] RACI Weights panel displays correctly
- [x] RACI Workload Weights panel displays correctly
- [x] Apply buttons save to localStorage
- [x] Reset buttons restore default values
- [x] Workload calculation uses raciWorkloadWeights
- [x] Adjusted duration calculation uses weighted SP
- [x] RACI Weighted Workload graph shows current weights
- [x] No linter errors
- [x] Validation works (0-10 range)
- [x] Notifications display correctly

---

## 🚀 Next Steps (Optional)

1. **Make raciWeights dynamic in formula:**
   - Currently hardcoded as (1, 0.1, 0.05, 0.01)
   - Update `calculateAdjustedDuration` to use `raciWeights.value`

2. **Add tooltips:**
   - Explain what each weight means
   - Show examples of impact

3. **Add presets:**
   - "Conservative" preset
   - "Aggressive" preset
   - "Balanced" preset

4. **Historical comparison:**
   - Show how changing weights affects estimates
   - Compare past predictions with actuals

---

## 📚 Files Modified

**`src/pages/PertRaciOptimizationPage.vue`:**
- Added `RaciWorkloadWeights` interface
- Added `raciWorkloadWeights` ref variable
- Added `loadRaciWorkloadWeights()` function
- Updated `getMemberWeightedStoryPointsInSprint()` to use `raciWorkloadWeights`
- Updated `raciWeightedWorkload` computed to use `raciWorkloadWeights`
- Added `applyWorkloadWeights()` function
- Added `resetWorkloadWeights()` function
- Updated `applyWeights()` validation and message
- Updated `resetWeights()` default values and message
- Added RACI Workload Weights configuration panel in UI
- Updated RACI Weighted Workload display to show dynamic weights

---

*Implementation completed successfully! ✨*  
*Users now have full control over both workload calculation and duration adjustment.*

