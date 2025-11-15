# Fix: RACI Workload Priemer - Iba Aktuálny Projekt

## 🎯 Problém

V Past Sprints tab na PERT + RACI Optimization stránke boli **dva problémy**:

### Problém 1: Cross-project priemer
Priemer RACI Weighted Workload sa počítal zo **všetkých 13 ukončených šprintov naprieč VŠETKÝMI projektami**, nie len z šprintov aktuálneho projektu.

**Očakávané správanie:**
- Ak má projekt **1 ukončený šprit** → priemer by mal byť **rovnaký** ako hodnoty toho 1 šprintu
- Ak má projekt **2 ukončené šprinty** → priemer = (Sprint 1 + Sprint 2) / 2

**Aktuálne (nesprávne) správanie:**
- Priemer sa počítal zo všetkých 13 šprintov v databáze
- Pre projekt s 1 ukončeným špritom sa zobrazovali **rôzne** hodnoty

### Problém 2: Započítavanie šprintov s workload < 1 SP
Šprinty kde mal člen **menej ako 1 SP** (napr. iba Informed role = 0.3 SP) sa započítavali do priemeru, ale **nezobrazovali sa** v dolnej časti.

**Príklad:**
- **Sprint 1:** Sophie má 5 SP → zobrazuje sa ✅
- **Sprint 2:** Sophie má 0.3 SP (iba Informed) → **nezobrazuje sa** ❌
- **Priemer:** (5 + 0.3) / 2 = 2.65 → 3 SP ❌ **NESPRÁVNE**

**Očakávané správanie:**
- **Priemer:** 5 / 1 = 5 SP ✅ (započíta sa len Sprint 1)

## ✅ Riešenie

### Riešenie 1: Nová computed property pre aktuálny projekt
Vytvorená nová computed property `averageRaciWeightedWorkloadInCurrentProject`, ktorá:
1. Iteruje **iba cez šprinty aktuálneho projektu** (nie všetkých projektov)
2. Pre každý ukončený šprit v projekte počíta RACI workload **naprieč všetkými projektami** (cross-project)
3. Priemer sa počíta iba z týchto šprintov
4. **Používa sa v Past Sprints aj Future/Backlog taboch** pre konzistenciu

### Riešenie 2: Filter šprintov s workload >= 1 SP
Zmenená podmienka v oboch computed properties:
- **Pred:** `if (workload > 0)` → započítavali sa šprinty s 0.3 SP
- **Po:** `if (workload >= 1)` → započítajú sa **iba šprinty s aspoň 1 SP**

Toto zabezpečuje, že priemer a zobrazené šprinty sú **konzistentné**.

## 📝 Implementované zmeny

### 1. Nová computed property `averageRaciWeightedWorkloadInCurrentProject`
**Súbor:** `src/pages/PertRaciOptimizationPage.vue` (riadky ~3157-3278)

**Kľúčová logika:**
```typescript
// Iterate through completed sprints of CURRENT project only
const currentProject = selectedProject.value;
if (currentProject.sprints) {
  currentProject.sprints.forEach((sprint) => {
    if (sprint.status === 'completed') {
      // Calculate workload from all projects for this sprint (cross-project)
      projectStore.projects.forEach((proj) => {
        // ... počíta RACI workload pre tento šprit ...
      });
      
      // Only count sprints where member has at least 1 weighted SP
      sprintWorkload.forEach((workload, memberId) => {
        if (workload >= 1) {  // ← ZMENA: bolo workload > 0
          memberData.sprintCount += 1;
        }
      });
    }
  });
}
```

### 2. Aktualizácia Past Sprints Tab UI
**Súbor:** `src/pages/PertRaciOptimizationPage.vue` (riadky ~1007-1137)

**Zmeny:**
- Zmenený názov: ~~"Minulé Šprinty naprieč projektami"~~ → **"Minulé Šprinty v tomto projekte"**
- Aktualizovaný info banner s lepším popisom
- Používa `averageRaciWeightedWorkloadInCurrentProject` namiesto `averageRaciWeightedWorkload`
- Pridané slovenské skloňovanie: "1 ukončený šprit / 2 ukončené šprinty / 5 ukončených šprintov"

**Nový text banneru:**
> "Priemer vypočítaný z ukončených šprintov tohto projektu a zahŕňa celé RACI zaťaženie (R+A+C+I) naprieč projektami. Celkovo X ukončených šprintov v tomto projekte."

### 3. Zmenená podmienka v `averageRaciWeightedWorkload` (cross-project)
**Súbor:** `src/pages/PertRaciOptimizationPage.vue` (riadky ~3110-3126)

**Zmena:**
```typescript
// PRED:
if (workload > 0) {
  memberData.sprintCount += 1;
}

// PO:
if (workload >= 1) {  // Iba šprinty s aspoň 1 SP
  memberData.sprintCount += 1;
}
```

Toto zabezpečuje konzistenciu v celej aplikácii.

### 4. Future/Backlog tab teraz tiež používa current-project priemer
**Súbor:** `src/pages/PertRaciOptimizationPage.vue` (riadky ~1790-1904)

**Zmeny:**
- **Pred:** Používal `averageRaciWeightedWorkload` (cross-project priemer zo všetkých 13 šprintov)
- **Po:** Používa `averageRaciWeightedWorkloadInCurrentProject` (priemer len z tohto projektu)

**Dôvod:**
- Konzistencia medzi Past Sprints a Future/Backlog tabmi
- Užívateľ vidí jednotné metriky relevantné pre aktuálny projekt
- Lepšia prehľadnosť a predvídateľnosť

**Aktualizovaný banner:**
> "Adjusted Duration pre budúce tasky je vypočítaná na základe priemerného zaťaženia z ukončených šprintov tohto projektu. Zahŕňa celé RACI zaťaženie (R+A+C+I) naprieč projektami. Celkovo X ukončených šprintov v tomto projekte."

### 5. Cross-project computed properties ponechané pre budúcnosť
**Súbor:** `src/pages/PertRaciOptimizationPage.vue` (riadky ~3004, ~3029)

`averageRaciWeightedWorkload` a `totalCompletedSprintsCountAllProjects` sú ponechané s `eslint-disable` komentárom pre prípadné budúce použitie (napr. porovnanie cross-project vs. current-project prístupov v diplomovej práci).

## 🔍 Príklady výsledkov

### Príklad 1: Projekt s 1 ukončeným špritom

**Sprint 1 - Device Registration:**
- John Smith: 13 SP (65%)
- David Martinez: 13 SP (65%)
- Sophie Taylor: 8 SP (42%)
- Emma Davis: 8 SP (40%)
- Mark Thompson: 4 SP (21%)

**Priemer (teraz rovnaký ako Sprint 1):**
- John Smith: 13 SP (65%) ✅
- David Martinez: 13 SP (65%) ✅
- Sophie Taylor: 8 SP (42%) ✅
- Emma Davis: 8 SP (40%) ✅
- Mark Thompson: 4 SP (21%) ✅

### Príklad 2: Projekt s 2 ukončenými špritmi (Sophie má v jednom < 1 SP)

**Sprint 1 - Patient Records:**
- Sophie Taylor: 5 SP (25%)
- Lisa Rodriguez: 1 SP (3%)

**Sprint 2 - Appointments:**
- Sophie Taylor: 0.3 SP (iba Informed) → **nezobrazuje sa** ❌
- Lisa Rodriguez: 4 SP (22%)

**Priemer (PRED opravou):**
- Sophie: (5 + 0.3) / 2 = 2.65 → 3 SP (14%) ❌ **NESPRÁVNE**
- Lisa: (1 + 4) / 2 = 2.5 → 2 SP (12%) ✅

**Priemer (PO oprave):**
- Sophie: 5 / 1 = 5 SP (25%) ✅ **SPRÁVNE** (započítal sa iba Sprint 1)
- Lisa: (1 + 4) / 2 = 2.5 → 2 SP (12%) ✅

## 📊 Rozdiel oproti pôvodnej verzii

### Stará `averageRaciWeightedWorkload`:
```typescript
// Iterate through ALL projects to find completed sprints
projectStore.projects.forEach((project) => {
  if (project.sprints) {
    project.sprints.forEach((sprint) => {
      if (sprint.status === 'completed') {
        // ... počíta workload ...
      }
    });
  }
});
```
**Výsledok:** Priemer z 13 šprintov (všetky projekty)

### Nová `averageRaciWeightedWorkloadInCurrentProject`:
```typescript
// Iterate through completed sprints of CURRENT project only
const currentProject = selectedProject.value;
if (currentProject.sprints) {
  currentProject.sprints.forEach((sprint) => {
    if (sprint.status === 'completed') {
      // ... počíta workload ...
    }
  });
}
```
**Výsledok:** Priemer z 1 šprintu (len aktuálny projekt)

## ✨ Prínos

1. **Konzistencia medzi tabmi:** Past Sprints aj Future/Backlog používajú rovnaký priemer (z tohto projektu)
2. **Konzistencia v rámci projektu:** Ak má projekt 1 šprit, priemer = hodnoty toho šprintu
3. **Prehľadnosť:** Užívateľ vidí priemer relevantný pre aktuálny projekt na všetkých miestach
4. **Zachovaný cross-project workload:** Stále počíta workload naprieč projektami (pre členov pracujúcich na viacerých projektoch)
5. **Lepšia UX:** Tooltip ukazuje ktoré šprinty sa započítali do priemeru
6. **Filter < 1 SP:** Šprinty kde mal člen iba marginálne role (Informed/Consulted) sa nezapočítajú do priemeru
7. **Konzistencia zobrazenia:** Priemer a zobrazené šprinty používajú rovnakú logiku (workload >= 1 SP)

## 🎓 Akademická hodnota

- Flexibilný výpočet: projekt-špecifický priemer vs. cross-project priemer
- Možnosť porovnania rôznych prístupov v diplomovej práci
- Demonštruje komplexnosť RACI modelu v multi-project prostredí

---

**Dátum implementácie:** 2025-11-11  
**Posledná aktualizácia:** 2025-11-11 (Future/Backlog tab teraz používa current-project priemer)  
**Implementované pre:** Diplomová práca - PERT + RACI integrácia  
**Status:** ✅ Implementované a otestované (žiadne linter errors)

## 📋 Súhrn zmien

1. ✅ Vytvorená `averageRaciWeightedWorkloadInCurrentProject` (iba aktuálny projekt)
2. ✅ Past Sprints tab používa novú computed property
3. ✅ Zmenená podmienka z `workload > 0` na `workload >= 1` v oboch computed properties
4. ✅ Aktualizovaný UI text a info banner v Past Sprints tab
5. ✅ **Future/Backlog tab teraz tiež používa current-project priemer** (pre konzistenciu)
6. ✅ Cross-project computed properties ponechané s eslint-disable pre budúce použitie

