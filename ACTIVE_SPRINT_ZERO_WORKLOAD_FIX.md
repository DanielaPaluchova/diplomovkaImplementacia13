# Fix: Zobrazenie 0 SP pre členov keď nie je aktívny sprint

## 🎯 Zmeny

### 1. Odstránená nepoužívaná funkcia
- ❌ Odstránená `getMemberAverageWeightedSpAcrossProjects()` - už sa nepoužívala

### 2. Zobrazenie členov s 0 SP v aktívnom šprinte

**Súbor:** `src/pages/PertRaciOptimizationPage.vue`

**Problém:**
- Keď nie je aktívny sprint, tabuľka RACI Weighted Workload sa nezobrazuje
- Zobrazuje sa len info správa: "Žiadny aktívny šprit - všetci členovia majú 0% workload"
- Užívateľ nemôže vidieť členov s ich 0 SP

**Riešenie:**
- Tabuľka sa **vždy zobrazuje** (ak projekt má členov)
- Členovia sú zobrazení s **0 SP a 0%** keď nie je aktívny sprint
- Separator sa zobrazuje len keď sú nejaké tasky v aktívnom šprinte

## 📊 Pôvodné vs. Nové správanie

### PRED:

**Keď NIE JE aktívny sprint:**
```
┌────────────────────────────────────┐
│ RACI Weighted Workload             │
│ (Aktívny Šprit naprieč projektami) │
├────────────────────────────────────┤
│                                     │
│ Žiadny aktívny šprit - všetci      │
│ členovia majú 0% workload          │
│                                     │
└────────────────────────────────────┘
```

### PO FIXE:

**Keď NIE JE aktívny sprint:**
```
┌────────────────────────────────────┐
│ RACI Weighted Workload             │
│ (Aktívny Šprit naprieč projektami) │
├────────────────────────────────────┤
│ Sarah Johnson    ░░░░░░░░░  0 SP   │ 0%
│ Sophie Taylor    ░░░░░░░░░  0 SP   │ 0%
│ John Smith       ░░░░░░░░░  0 SP   │ 0%
│ Mike Wilson      ░░░░░░░░░  0 SP   │ 0%
│ Lisa Rodriguez   ░░░░░░░░░  0 SP   │ 0%
│                                     │
│ Kapacita: 20 SP na člena           │
└────────────────────────────────────┘
```

**Keď JE aktívny sprint:**
```
┌────────────────────────────────────┐
│ RACI Weighted Workload             │
│ (Aktívny Šprit naprieč projektami) │
├────────────────────────────────────┤
│ Sarah Johnson    ████████░  23 SP  │ 115%
│ Sophie Taylor    █████░░░░  14 SP  │ 69%
│ John Smith       ████░░░░░  13 SP  │ 64%
│ Mike Wilson      ███░░░░░░   9 SP  │ 43%
│ Lisa Rodriguez   ██░░░░░░░   6 SP  │ 29%
│                                     │
│ Kapacita: 20 SP na člena           │
└────────────────────────────────────┘
```

## 🔧 Implementačné detaily

### Computed property `raciWeightedWorkload`

Táto computed property **už existovala** a vracala všetkých členov projektu aj s 0 SP:

```typescript
// Initialize map with project members only
projectMembers.forEach((member) => {
  workloadMap.set(member.id, {
    memberId: member.id,
    memberName: member.name,
    workload: 0,  // ✅ Inicializované na 0
  });
});

// ... výpočet workload z aktívnych taskov ...

// Convert map to array and calculate percentage workload
const workloadArray = Array.from(workloadMap.values())
  .map((item) => {
    // ...
  })
  // Show all project members, even with 0% workload (for consistency)
  .sort((a, b) => b.workload - a.workload);

return workloadArray;  // ✅ Vracia všetkých členov aj s 0 SP
```

### Template zmeny

**PRED:**
```vue
<q-separator v-if="raciWeightedWorkload.length > 0" />
```

**PO:**
```vue
<q-separator v-if="activeSprintTasks.length > 0" />
```

**Dôvod:**
- Separator sa teraz zobrazuje len keď sú tasky v aktívnom šprinte
- Nie keď sú členovia (ktorí sú vždy, aj s 0 SP)

**Info správa:**
- Zmenená z: "Žiadny aktívny šprit - všetci členovia majú 0% workload"
- Na: "Žiadni členovia v projekte"
- Zobrazuje sa len keď projekt nemá vôbec žiadnych členov

## 🎓 Význam pre užívateľa

1. **Konzistentné zobrazenie:** Tabuľka sa zobrazuje vždy (podobne ako v "Minulé Šprinty" a "Budúce Tasky")

2. **Jasnejšie dáta:** Vidíte, že všetci členovia majú 0 SP, nie len správu o tom

3. **Lepšia orientácia:** Viete ktorí členovia sú v projekte aj keď momentálne nie je aktívny sprint

4. **Vizuálna konzistencia:** Všetky tri taby majú rovnakú štruktúru zobrazenia

## 🐛 Opravené ESLint warningy

- ❌ Odstránená nepoužívaná funkcia `getMemberAverageWeightedSpAcrossProjects`
- ✅ Žiadne ESLint chyby

## 📅 Dátum

2025-11-13

## ✍️ Autor

AI Assistant (based on user requirements)

