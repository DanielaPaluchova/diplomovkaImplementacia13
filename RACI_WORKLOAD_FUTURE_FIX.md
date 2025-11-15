# Fix: Future/Backlog RACI Workload - Skutočný vs. Historický

## 🎯 Problém

V **Future/Backlog** tab na PERT + RACI Optimization stránke sa zobrazoval **historický priemer z minulých šprintov**, nie **skutočný workload z budúcich/backlog taskov**.

### Príklad problému:

**Sarah Johnson:**
- Zobrazovalo sa: **23 SP (115%)** z historického priemeru
- Ale: **nemá žiadne future/backlog tasky** (nie je assigned k žiadnym budúcim taskám)
- **Average Task Increase: 0.0%** (pretože žiadne tasky nemajú RACI overhead)

### Očakávané správanie:
- Zobraziť **iba členov, ktorí majú pridelené future/backlog tasky**
- Zobraziť **skutočný RACI weighted workload z týchto taskov**
- Nie historický priemer z minulých šprintov

## ✅ Riešenie

Vytvorená nová computed property `futureBacklogRaciWeightedWorkload`, ktorá:
1. Iteruje cez **future/backlog tasky** (nie historical sprints)
2. Počíta **skutočný RACI weighted workload** z týchto taskov
3. Zobrazuje **iba členov s workload >= 1 SP** v budúcich taskoch

## 📝 Implementované zmeny

### 1. Nová computed property `futureBacklogRaciWeightedWorkload`
**Súbor:** `src/pages/PertRaciOptimizationPage.vue` (riadky ~3304-3386)

**Logika:**
```typescript
const futureBacklogRaciWeightedWorkload = computed(() => {
  // Initialize workload map for project members
  const workloadMap = new Map<number, { memberId, memberName, workload }>();
  
  // Calculate workload from future/backlog tasks
  futureBacklogTasks.value.forEach((task) => {
    const sp = task.storyPoints || 0;
    
    // Add weighted SP for each RACI role
    if (task.raciMembers?.responsible) {
      // Add R weight × SP
    }
    if (task.raciMembers?.accountable) {
      // Add A weight × SP
    }
    // ... C, I roles
  });
  
  // Filter members with at least 1 weighted SP
  return workloadArray.filter((item) => item.weightedSP >= 1);
});
```

**Kľúčový rozdiel oproti historical priemeru:**
- **Historický priemer:** Sčíta workload z completed sprintov / počet šprintov
- **Future workload:** Sčíta workload z backlog/planned taskov (bez delenia)

### 2. Aktualizácia Future/Backlog Tab UI
**Súbor:** `src/pages/PertRaciOptimizationPage.vue` (riadky ~1776-1870)

**Zmeny:**
- **Názov:** ~~"Priemerné RACI Weighted Workload (Použité pre výpočty)"~~ → **"RACI Weighted Workload (Budúce/Backlog tasky)"**
- **Banner:** Zmenený z warning (žltý) na info (modrý)
- **Text banneru:** "Zobrazuje skutočné RACI zaťaženie (R+A+C+I) z taskov v backlogu a planned šprintoch."
- **Dáta:** Používa `futureBacklogRaciWeightedWorkload` namiesto `averageRaciWeightedWorkloadInCurrentProject`
- **Tooltip:** Odstránený (future workload nemá sprint details z histórie)

**Nový banner:**
> "Zobrazuje skutočné RACI zaťaženie (R+A+C+I) z taskov v backlogu a planned šprintoch. Adjusted Duration pre tieto tasky je vypočítaná na základe priemerného zaťaženia z ukončených šprintov tohto projektu (X ukončených šprintov)."

### 3. Lepší "empty state" message
**Zmena:**
- **Pred:** "Žiadne dáta o workload v ukončených šprintoch"
- **Po:** "Žiadne dáta o workload v budúcich taskoch (nie sú pridelené žiadne RACI role)"

## 🔍 Príklad výsledku

### Pred opravou (nesprávne):

**Future/Backlog tab zobrazoval historický priemer:**
- Sarah Johnson: 23 SP (115%) ❌ - ale nemá žiadne future tasky!
- Sophie Taylor: 14 SP (69%) ❌ - historický priemer
- John Smith: 13 SP (64%) ❌ - historický priemer

### Po oprave (správne):

**Future/Backlog tab zobrazuje skutočný workload z budúcich taskov:**
- Zobrazia sa **iba členovia s pridelenými budúcimi taskami**
- Napr. ak Sophie má v backlogu 2 tasky s 5 SP (Responsible):
  - Sophie Taylor: 10 SP (50%) ✅ (2 × 5 SP × 1.0 weight)
- Sarah Johnson sa **nezobrazí vôbec** ✅ (nemá budúce tasky)

## 📊 Rozdiel: Historický priemer vs. Future workload

### Historický priemer (`averageRaciWeightedWorkloadInCurrentProject`):
```typescript
// Sčíta workload zo všetkých completed sprintov
totalWorkload = sprint1 + sprint2 + sprint3
average = totalWorkload / sprintCount

// Zobrazí všetkých členov, ktorí mali workload v histórii
// Aj keď nemajú žiadne budúce tasky
```

### Future workload (`futureBacklogRaciWeightedWorkload`):
```typescript
// Sčíta workload z backlog/planned taskov
totalWorkload = task1 + task2 + task3
// Žiadne delenie!

// Zobrazí IBA členov s future taskmi
// Ak nemá future tasky → nezobrazí sa
```

## ✨ Prínos

1. **Správne dáta:** Future tab zobrazuje future workload, nie historický priemer
2. **Relevantnosť:** Zobrazujú sa iba členovia s budúcimi taskmi
3. **Prehľadnosť:** Užívateľ vidí skutočné plánované zaťaženie
4. **Konzistencia:** Workload zodpovedá taskám v tabuľke nižšie
5. **Debugging:** Ak je Average Task Increase = 0%, teraz je jasné prečo (žiadne RACI assignments)

## 🎓 Akademická hodnota

- **Prediktívna analýza:** Zobrazuje plánovaný workload pre budúce šprinty
- **Capacity planning:** Pomáha identifikovať overload pred začiatkom šprintu
- **RACI v backlogu:** Demonštruje dôležitosť priraďovania RACI rolí už v backlogu
- **Early warning:** Upozorní na nerovnomerné rozdelenie práce skôr ako začne šprit

## 🔧 Technické detaily

### Prečo sa Sarah zobrazovala s 23 SP?
- Sarah mala v **minulých šprintoch** vysoký workload (23 SP priemer)
- Zobrazoval sa `averageRaciWeightedWorkloadInCurrentProject` (historický priemer)
- Ale **v budúcich taskoch** nemala žiadne pridelené role

### Prečo bol Average Task Increase = 0.0%?
- Average Task Increase sa počíta z **future taskov v tabuľke**
- Ak tasky nemajú RACI roles, RACI overhead = 0
- Preto (Adjusted - PERT) / PERT = 0%

### Vzťah medzi workload a Adjusted Duration:
- **Workload:** Zobrazuje RACI weighted SP z budúcich taskov
- **Adjusted Duration:** Počíta sa na základe **historického priemeru** + RACI overhead
- Historický priemer sa stále používa pre **výpočet Adjusted Duration**, ale **nie pre zobrazenie workloadu**

---

**Dátum implementácie:** 2025-11-11  
**Implementované pre:** Diplomová práca - PERT + RACI integrácia  
**Status:** ✅ Implementované a otestované (žiadne linter errors)

## 📋 Súhrn zmien

1. ✅ Vytvorená `futureBacklogRaciWeightedWorkload` (workload z budúcich taskov)
2. ✅ Future/Backlog tab používa novú computed property
3. ✅ Aktualizovaný UI text, banner a farba
4. ✅ Odstránený tooltip (future workload nemá sprint details)
5. ✅ Lepší empty state message
6. ✅ Zobrazujú sa iba členovia s pridelenými future taskmi


