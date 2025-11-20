# Fix: Adjusted Duration pre Budúce Tasky - Konzistencia s Tabuľkou

## 🎯 Problém

V PERT + RACI Integration stránke mal **Adjusted Duration pre budúce tasky vždy 0% increase** napriek tomu, že tabuľka zobrazovala preťaženie členov (napr. Sarah Johnson 115%).

### Príklad problému:

**V tabuľke:**
- Sarah Johnson: **23 SP (115%)** - priemer z minulých šprintov

**V budúcich taskoch:**
- Všetky tasky: **0% increase** v Adjusted Duration oproti PERT Duration

### Príčina:

1. **Tabuľka** (`averageRaciWeightedWorkloadInCurrentProject`):
   - Počítala priemer z **šprintov TOHTO projektu**
   - Ale zahŕňala **cross-project workload** (tasky z iných projektov v týchto šprintoch)

2. **Adjusted Duration** (`calculateAdjustedDuration` s `useAverage = true`):
   - Používala `getAverageMemberWeightedStoryPoints()`
   - Ktorá počítala priemer **naprieč VŠETKÝMI projektmi a VŠETKÝMI šprintmi**
   - Rozdielne hodnoty = 0% increase

## ✅ Riešenie

### 1. Upravená funkcia `getMemberAverageWeightedSpInProject`

**Súbor:** `src/pages/PertRaciOptimizationPage.vue` (riadky ~3834-3889)

**Zmeny:**
```typescript
// PRED: Počítala len tasky z TOHTO projektu
if (project.id === selectedProject.value!.id && project.sprints) {
  project.sprints.forEach((sprint) => {
    // ...
    if (project.tasks) {  // ❌ Len tasky z tohto projektu
      project.tasks.forEach((task) => {
```

**PO: Počíta cross-project workload (rovnako ako tabuľka)**
```typescript
// Find completed sprints in the selected project
const currentProject = selectedProject.value;
if (currentProject.sprints) {
  currentProject.sprints.forEach((sprint) => {
    // ...
    // Calculate weighted SP for this member in this sprint across ALL projects (cross-project)
    projectStore.projects.forEach((proj) => {  // ✅ Všetky projekty
      if (proj.tasks) {
        proj.tasks.forEach((task) => {
          if (task.sprintId === sprint.id) {  // ✅ Tasky v šprinte tohto projektu
```

**Kľúčová logika:**
- Iteruje cez **šprinty tohto projektu**
- Ale pre každý šprit počíta **tasky zo všetkých projektov** ktoré sú v tomto šprinte
- To je **cross-project workload** - rovnaký princíp ako v tabuľke

### 2. Zmenená funkcia `calculateAdjustedDuration`

**Súbor:** `src/pages/PertRaciOptimizationPage.vue` (riadky ~3554-3603)

**PRED:**
```typescript
const memberWeightedSP = useAverage
  ? getAverageMemberWeightedStoryPoints(memberId)  // ❌ Všetky projekty a všetky šprinty
  : getMemberWeightedStoryPointsInSprint(memberId, sprintId);
```

**PO:**
```typescript
const memberWeightedSP = useAverage
  ? getMemberAverageWeightedSpInProject(memberId)  // ✅ Šprinty tohto projektu s cross-project workload
  : getMemberWeightedStoryPointsInSprint(memberId, sprintId);
```

**Zmeny sa týkajú všetkých 4 RACI rolí:**
- Responsible (R)
- Accountable (A)
- Consulted (C)
- Informed (I)

## 📊 Výsledok

### Pred fixom:

| Komponenta | Výpočet priemeru |
|-----------|-----------------|
| Tabuľka | Šprinty tohto projektu + cross-project workload |
| Adjusted Duration | Všetky projekty a všetky šprinty |
| **Výsledok** | **Nesúlad → 0% increase** |

### Po fixe:

| Komponenta | Výpočet priemeru |
|-----------|-----------------|
| Tabuľka | Šprinty tohto projektu + cross-project workload |
| Adjusted Duration | Šprinty tohto projektu + cross-project workload |
| **Výsledok** | **Konzistencia → Správny increase %** |

## 🎓 Význam pre užívateľa

1. **Správne predpovedanie:** Adjusted Duration pre budúce tasky teraz **správne zohľadňuje preťaženie** členov

2. **Konzistentné dáta:** Tabuľka zobrazuje **rovnaké hodnoty** aké sa používajú na výpočet Adjusted Duration

3. **Cross-project awareness:** Oba výpočty teraz správne zohľadňujú, že členovia môžu pracovať na taskoch v iných projektoch počas šprintov tohto projektu

4. **Lepšie plánovanie:** Keď Sarah Johnson má 115% workload v tabuľke, jej budúce tasky **budú mať vyšší Adjusted Duration**

## 🔍 Technické detaily

### Čo je cross-project workload?

Predstavte si:
- **Projekt A** má **Sprint 1** (24.11 - 8.12)
- **Projekt B** má **Sprint 5** (24.11 - 8.12) - rovnaké dátumy!
- **Sarah Johnson** je v Projekte A

Keď počítame jej priemer v Projekte A:
- ✅ **SPRÁVNE:** Započítame tasky z **Sprint 1 (Projekt A)** + **Sprint 5 (Projekt B)** 
  - Pretože oba šprinty bežia v tom istom čase
- ❌ **NESPRÁVNE:** Započítame len tasky z **Sprint 1 (Projekt A)**

### Prečo to má zmysel?

Ak Sarah pracuje na taskoch v iných projektoch počas šprintov tohto projektu, ovplyvňuje to jej kapacitu. Preto musíme zohľadniť **celý workload** počas týchto šprintov.

### Implementačné detaily:

1. **Logika šprintov:**
   ```typescript
   // 1. Nájdi ukončené šprinty TOHTO projektu
   currentProject.sprints.forEach((sprint) => {
     if (sprint.status === 'completed') {
       
       // 2. Pre každý šprit, nájdi všetky tasky zo VŠETKÝCH projektov
       projectStore.projects.forEach((proj) => {
         proj.tasks.forEach((task) => {
           if (task.sprintId === sprint.id) {  // Task je v tomto šprinte
             // Započítaj do workload
           }
         });
       });
     }
   });
   ```

2. **Filtrovanie šprintov:**
   - Len šprinty s `status === 'completed'`
   - Len šprinty kde člen mal workload `>= 1 SP` (rovnako ako tabuľka)

3. **Priemer:**
   - Súčet workload zo všetkých započítaných šprintov / počet šprintov
   - Neokrúhľuje sa hneď - presnosť sa zachová pre výpočet Adjusted Duration

## 📅 Dátum

2025-11-13

## 🔗 Súvisiace fixe

- `RACI_WORKLOAD_TABS_FIX.md` - Oprava tabuľky v Budúce Tasky tab

## ✍️ Autor

AI Assistant (based on user requirements)


