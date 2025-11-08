# Past Sprints Weighted SP Fix - Documentation

**Dátum**: November 6, 2025  
**Problém**: V minulých šprintoch sa zobrazovali 0 SP namiesto skutočných weighted SP z toho šprintu

## Problém

V tabe "Minulé Šprinty", pri rozkliknutí RACI detailov pre jednotlivých členov, sa zobrazovali **0 SP** namiesto skutočných weighted story points z toho ukončeného šprintu.

### Príčina:
Funkcie `getMemberSprintStoryPointsInProject()` a `getMemberSprintStoryPointsAcrossProjects()` používali `activeSprint.value.id`, ktorý už pre ukončené šprinty nie je relevantný (nie je to ich sprintId).

## Riešenie

### 1. **Vytvorené nové funkcie s parametrom sprintId**

```typescript
// Get member's WEIGHTED SP for a SPECIFIC sprint in current project (for past sprints)
function getMemberSprintStoryPointsInProjectForSprint(
  memberId: number,
  sprintId: number,
): number {
  if (!selectedProject.value) return 0;

  const projectTasks = selectedProject.value.tasks || [];
  let total = 0;

  projectTasks.forEach((task) => {
    if (task.sprintId === sprintId) {
      const sp = task.storyPoints || 0;

      // Add weighted SP based on RACI role
      if (task.raci?.responsible?.includes(memberId)) {
        total += raciWorkloadWeights.responsible * sp;
      }
      if (task.raci?.accountable === memberId) {
        total += raciWorkloadWeights.accountable * sp;
      }
      if (task.raci?.consulted?.includes(memberId)) {
        total += raciWorkloadWeights.consulted * sp;
      }
      if (task.raci?.informed?.includes(memberId)) {
        total += raciWorkloadWeights.informed * sp;
      }
    }
  });

  return Math.round(total);
}

// Get member's WEIGHTED SP for a SPECIFIC sprint ACROSS ALL projects (for past sprints)
function getMemberSprintStoryPointsAcrossProjectsForSprint(
  memberId: number,
  sprintId: number,
): number {
  const weighted = getMemberWeightedStoryPointsInSprint(memberId, sprintId);
  return Math.round(weighted);
}
```

### 2. **Aktualizované všetky RACI sekcie v Past Sprints tabe**

Pre každú RACI rolu (Responsible, Accountable, Consulted, Informed) v Past Sprints tabe boli zmenené volania funkcií:

**Predtým:**
```vue
{{ getMemberSprintStoryPointsInProject(memberId) }}
{{ getMemberSprintStoryPointsAcrossProjects(memberId) }}
```

**Teraz:**
```vue
{{ getMemberSprintStoryPointsInProjectForSprint(memberId, props.row.sprintId) }}
{{ getMemberSprintStoryPointsAcrossProjectsForSprint(memberId, props.row.sprintId) }}
```

### 3. **Aktualizované popisky**

**Predtým:**
```
(vážené podľa RACI rolí)
```

**Teraz:**
```
(vážené podľa RACI rolí v tomto šprinte)
```

## Testovací príklad

### Sprint 2 - Core Backend (completed)
**Task**: Email Notification Service (8 SP)

**RACI:**
- Responsible: Alex Chen (ID: 5)
- Accountable: Lisa Rodriguez (ID: 6)
- Consulted: Sarah Johnson (ID: 2)

**Weighted SP v tomto šprinte:**
- **Alex Chen** (R): 8 SP × 1.0 = **8 weighted SP** ✓
- **Lisa Rodriguez** (A): 8 SP × 0.1 = **0.80 weighted SP** → zaokrúhlené na **1 SP** ✓
- **Sarah Johnson** (C): 8 SP × 0.05 = **0.40 weighted SP** → zaokrúhlené na **0 SP** ✓

**Predtým**: Všade 0 SP (lebo aktívny šprint už neobsahuje tieto tasky)  
**Teraz**: Správne hodnoty z toho ukončeného šprintu!

## Zmeny v súboroch

### `src/pages/PertRaciOptimizationPage.vue`

**Nové funkcie** (riadky 2752-2792):
- `getMemberSprintStoryPointsInProjectForSprint(memberId, sprintId)`
- `getMemberSprintStoryPointsAcrossProjectsForSprint(memberId, sprintId)`

**Aktualizované sekcie v Past Sprints tabe**:
1. **Responsible Members** (riadky 1208-1275)
2. **Accountable Members** (riadky 1312-1402)
3. **Consulted Members** (riadky 1404-1473)
4. **Informed Members** (riadky 1508-1577)

## Výhody

✅ **Presné údaje**: Zobrazujú sa skutočné weighted SP z konkrétneho ukončeného šprintu  
✅ **Lepšia analýza**: Môžeš vidieť historickú záťaž členov v minulých šprintoch  
✅ **Konzistencia**: Všetky 4 RACI role majú rovnaký prístup k dátam  
✅ **Jasnosť**: Popisok "(vážené podľa RACI rolí v tomto šprinte)" objasňuje, že ide o dáta z toho šprintu

## Záver

Fix zabezpečuje, že v minulých šprintoch sa zobrazujú **skutočné weighted story points z toho konkrétneho ukončeného šprintu**, nie 0 alebo hodnoty z iného šprintu. Toto umožňuje lepšiu historickú analýzu a porovnávanie záťaže členov v rôznych šprintoch.

