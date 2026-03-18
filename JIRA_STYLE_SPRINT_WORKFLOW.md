# Jira-Style Sprint Workflow Implementation

## Overview
Implementovaný bol Jira-style prístup k správe šprintov, ktorý umožňuje plánovanie šprintov vopred pred ich spustením.

## Hlavné zmeny

### 1. Backend Changes (Python)

#### `backend/app/routes/smart_sprint.py`
- **Zmena:** AI Sprint Planner teraz vytvára šprinty so statusom `'planned'` namiesto `'active'`
- **Riadok 309-322:** Sprint sa vytára s `status='planned'`
- **Riadok 289-301:** Odstránená validácia, ktorá zabraňovala vytvoriť nový šprinť keď existuje aktívny šprinť (keďže teraz vytvárame planned šprinty)

### 2. Frontend Changes (Vue/TypeScript)

#### `src/pages/ProjectDetailPage.vue`

##### Template Changes (Backlog Tab)
- **Nový design:** Zmena z 2-stĺpcového layoutu na single-column layout s expandable sekciami
- **Pridané sekcie:**
  1. **Product Backlog** - Expandable, predvolene otvorený
  2. **Active Sprint** - Expandable, zobrazuje sa len ak existuje aktívny šprinť
  3. **Planned Sprints** - Každý plánovaný šprinť je samostatná expandable karta
  
- **Nové funkcie:**
  - "Create Sprint" button v hlavičke Backlog view
  - Expandable/collapsible sekcie pre backlog a všetky šprinty
  - Drag & drop support pre všetky šprinty (active aj planned)
  - Vizuálne odlíšenie:
    - Backlog: sivé pozadie (bg-grey-3)
    - Active sprint: zelené pozadie (bg-green-1)
    - Planned sprints: modré pozadie (bg-blue-1)

##### Script Changes
**Nové reactive variables:**
```typescript
const dragTarget = ref<number | string | null>(null);
const backlogExpanded = ref(true);
const activeSprintExpanded = ref(true);
const expandedPlannedSprints = ref<Set<number>>(new Set());
```

**Nové helper funkcie:**
```typescript
togglePlannedSprint(sprintId: number)
isPlannedSprintExpanded(sprintId: number): boolean
getSprintTasks(sprintId: number): Task[]
```

**Upravené funkcie:**
- `onDragOver(target)` - Teraz prijíma target parameter (sprint ID alebo 'active')
- `onDrop(sprintId)` - Teraz prijíma špecifické sprint ID
- `startSprint(sprint)` - Zmenené na async, pridané reloading projektu

## Sprint Lifecycle

### 1. BACKLOG
- Tasky bez priradeného šprintu
- `task.sprintId === null`

### 2. PLANNED SPRINT (status: 'planned')
- Šprinť vytvorený, ale nebeží
- Môžem pridávať/odoberať tasky
- Môžem upraviť šprinť (edit)
- Môžem spustiť šprinť (start button)
- Vizuálne: modrá farba, ikona "schedule"

### 3. ACTIVE SPRINT (status: 'active')
- Šprinť beží
- Zobrazuje progress bar
- Môžem pridávať/odoberať tasky
- Môžem ukončiť šprinť (complete button)
- Vizuálne: zelená farba, ikona "play_circle"

### 4. COMPLETED SPRINT (status: 'completed')
- Šprinť ukončený
- Zobrazuje sa v Sprint Management tab
- Viditeľný report a velocity

## Používateľský workflow

### Vytvorenie šprintu:
1. Kliknúť na "Create Sprint" v Backlog view (alebo v Sprint Management tab)
2. Vyplniť názov, cieľ, dátumy
3. Šprinť sa vytvorí ako PLANNED

### Pridanie taskov do šprintu:
1. Expandnúť plánovaný šprinť
2. Drag & drop tasky z backlogu do šprintu
3. ALEBO: Right-click na task → "Move to Sprint"

### Spustenie šprintu:
1. Kliknúť na "Start" button pri plánovanom šprinte
2. Šprinť sa zmení na ACTIVE
3. Len jeden šprinť môže byť aktívny naraz

### Ukončenie šprintu:
1. Kliknúť na "Complete" button pri aktívnom šprinte
2. Nedokončené tasky sa automaticky presunú do backlogu
3. Šprinť sa zmení na COMPLETED

## AI Sprint Planner Integration

- AI Sprint Planner teraz vytvára **PLANNED** šprinty
- Po vygenerovaní plánu môžete:
  1. Upraviť tasky v šprinte (pridať/odobrať)
  2. Upraviť šprinť (názov, dátumy, cieľ)
  3. Spustiť šprinť keď ste pripravení

## Výhody nového workflow

1. **Flexibilita:** Môžete naplánovať viacero šprintov dopredu
2. **Kontrola:** Upraviť plán pred spustením šprintu
3. **Prehľadnosť:** Jasné vizuálne odlíšenie backlog / planned / active / completed
4. **Jira-like UX:** Známy workflow z Jira
5. **AI Planning:** AI môže plánovať šprint bez okamžitého spustenia

## Technické detaily

### Drag & Drop
- Každý šprinť (planned aj active) má vlastnú drop zone
- `dragTarget` sleduje aktuálny cieľ drag operácie
- Visual feedback cez `drag-over` CSS class

### Expand/Collapse
- Backlog: defaultne expanded
- Active sprint: defaultne expanded
- Planned sprints: defaultne collapsed, state v `Set<number>`
- Používa `q-slide-transition` pre smooth animácie

### Status Flow
```
CREATE → 'planned' → START → 'active' → COMPLETE → 'completed'
```

## Migrácia existujúcich dát

- Existujúce šprinty so statusom 'active' budú fungovať normálne
- Žiadna databázová migrácia nie je potrebná
- Sprint model už podporoval všetky 3 statusy

## Testing Checklist

- [ ] Vytvorenie nového šprintu (manual + AI planner)
- [ ] Expandovanie/kolapsovanie sekcií
- [ ] Drag & drop do planned šprintov
- [ ] Drag & drop do active šprintu
- [ ] Spustenie planned šprintu
- [ ] Ukončenie active šprintu
- [ ] Úprava planned šprintu
- [ ] Zmazanie planned šprintu
- [ ] Cross-project workload consideration v AI planneri
