# Combined Formula Update - Documentation

**Dátum**: November 6, 2025  
**Úloha**: Aktualizácia vysvetlenia "Combined Formula" v UI

## Čo bolo aktualizované

### 1. **Vysvetlenie L_R, L_A, L_C, L_I premenných**

**Predtým:**
- Jednoduché vysvetlenie: "Preťaženie z [rola] rolí nad 20 SP"

**Teraz:**
- Presné vysvetlenie s výpočtom: "Preťaženie z [rola] rolí nad 20 weighted SP"
- Pridaný vzorec: `max(0, (priemerné weighted SP členov / 20) - 1.0)`
- Rozlíšenie medzi rolami s jedným členom (Accountable) a viacerými členmi (R, C, I)

### 2. **Nová sekcia: RACI Workload Weights**

Pridaná nová sekcia vysvetľujúca váženie Story Points:

```
RACI Workload Weights (váženie SP)

- Weighted SP = Story Points vážené podľa RACI rolí člena v tasku
- Responsible: 1.0 × SP (plná váha)
- Accountable: 0.1 × SP (10% váha)
- Consulted: 0.05 × SP (5% váha)
- Informed: 0.01 × SP (1% váha)

Príklad: Ak má člen 8 SP ako Responsible a 21 SP ako Consulted,
         jeho weighted SP = (8 × 1.0) + (21 × 0.05) = 8 + 1.05 = 9.05 SP
```

### 3. **Nová sekcia: Dôležité pravidlá**

Pridané 4 kľúčové pravidlá s praktickými príkladmi:

```
⚠️ Dôležité pravidlá

1. Čas sa zvyšuje LEN ak je RACI rola preťažená (weighted SP > 20)

2. Do vzorca vstupuje len EXCESS overload (nad 100% kapacity)

3. Ak weighted SP = 21.4, overload = 21.4/20 = 1.07, excess = 1.07 - 1.0 = 0.07 (7% nárast času)

4. Ak weighted SP = 15, overload = 15/20 = 0.75, excess = 0 (bez vplyvu na čas)
```

## Overenie správnosti

### Testovací prípad: Payment Gateway Integration

**Údaje:**
- Task: Payment Gateway Integration (21 SP)
- Sprint: Sprint 2 - Core Backend (aktívny)
- PERT Duration: 72 dní

**RACI priradenia:**
- Responsible: Sarah Johnson (ID: 2)
- Accountable: Lisa Rodriguez (ID: 6)
- Consulted: Mike Wilson (ID: 3), Alex Chen (ID: 5)
- Informed: John Smith (ID: 1)

**Weighted SP v šprinte:**

| Člen             | Weighted SP | Overload | Excess  | Stav            |
|------------------|-------------|----------|---------|-----------------|
| Sarah Johnson    | 21.40       | 1.0700   | 0.0700  | ⚠️ Preťažená    |
| Lisa Rodriguez   | 2.90        | 0.1450   | 0.0000  | ✅ OK           |
| Mike Wilson      | 1.05        | 0.0525   | 0.0000  | ✅ OK           |
| Alex Chen        | 9.05        | 0.4525   | 0.0000  | ✅ OK           |
| John Smith       | 0.21        | 0.0105   | 0.0000  | ✅ OK           |

**Výpočet:**

```
LR = 0.0700 (Sarah je preťažená)
LA = 0.0000 (Lisa nie je preťažená)
LC = 0.0000 (Mike a Alex nie sú preťažení)
LI = 0.0000 (John nie je preťažený)

RACI Adjustment = (1.0 × 0.0700) + (0.1 × 0.0000) + (0.05 × 0.0000) + (0.01 × 0.0000)
                = 0.0700

Adjusted Duration = 72.00 × (1 + 0.0700)
                  = 72.00 × 1.0700
                  = 77.04 dní

Increase: +7.00% (+5.04 dní)
```

**✅ Výsledok potvrdený ako správny!**

## Kľúčové zmeny v logike

1. **Weighted SP namiesto obyčajných SP**
   - Každá RACI rola má inú váhu (R: 1.0, A: 0.1, C: 0.05, I: 0.01)
   - Člen môže mať viacero rolí v tom istom tasku - váhy sa sčítavajú

2. **Excess overload formula**
   - `max(0, (weighted_SP / 20) - 1.0)`
   - Iba preťaženie nad 100% kapacity (nad 20 weighted SP) zvyšuje čas
   - Pod 100% kapacity nemá žiadny vplyv na duration

3. **Priemerné preťaženie pre role s viacerými členmi**
   - Responsible, Consulted, Informed môžu mať viacero členov
   - Berie sa priemer ich weighted SP pre výpočet L hodnoty

## Súbory zmenené

- `src/pages/PertRaciOptimizationPage.vue` (riadky 156-270)
  - Aktualizovaná sekcia "Podrobné vysvetlenie vzorcov"
  - Pridané sekcie: "RACI Workload Weights" a "Dôležité pravidlá"

## Technické detaily implementácie

### Funkcie pre weighted SP:

1. **`getMemberWeightedStoryPointsInSprint(memberId, sprintId)`**
   - Vypočíta weighted SP pre člena v konkrétnom šprinte naprieč všetkými projektami
   - Používa `raciWorkloadWeights` konštanty

2. **`calculateAdjustedDuration(task, sprintId, useAverage)`**
   - Vypočíta adjusted duration s použitím weighted SP
   - Aplikuje `max(0, overload - 1.0)` pre každú RACI rolu

### RACI Workload Weights (konštanty v kóde):

```typescript
const raciWorkloadWeights: RaciWorkloadWeights = {
  responsible: 1.0,
  accountable: 0.1,
  consulted: 0.05,
  informed: 0.01,
};
```

### RACI Adjustment Weights (konfigurovateľné cez UI):

```typescript
const raciWeights = ref<RaciWeights>({
  responsible: 1.0,
  accountable: 0.1,
  consulted: 0.05,
  informed: 0.01,
});
```

## Záver

Combined Formula bola úspešne aktualizovaná tak, aby presne odrážala:
- ✅ Použitie weighted SP namiesto obyčajných SP
- ✅ Excess overload logiku (iba nad 100% kapacity)
- ✅ Rozdiel medzi workload weights a formula weights
- ✅ Praktické príklady výpočtov
- ✅ Jasné vizuálne oddelenie sekcií

Dokumentácia je teraz kompletná a presná pre používateľov systému.

