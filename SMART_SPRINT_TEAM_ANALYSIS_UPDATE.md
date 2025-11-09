# Smart Sprint Planning - Team Analysis Feature

## 🎯 Problém

Keď bol zapnutý "Consider workload from other projects" a niektorí členovia tímu boli preťažení:
- ✅ Videli sa len členovia ktorí **DOSTALI** tasky (napr. 2 z 5)
- ❌ **NEVIDELI** sa členovia ktorí **NEDOSTALI** tasky (3 z 5)
- ❌ Nebolo jasné **PREČO** títo členovia nedostali nič
- ❌ Nebolo jasné **KOĽKO** majú práce v iných projektoch

**Používateľ nevedel:**
- Prečo len 2 členovia dostali tasky
- Čo sa deje s ostatnými 3 členmi
- Koľko majú práce v iných projektoch
- Či sú preťažení alebo nie

## ✨ Riešenie

### Nová Sekcia: **Team Capacity Analysis**

Pridaná úplne nová sekcia ktorá zobrazuje **VŠETKÝCH** členov tímu (nielen tých čo dostali tasky).

### 1. Backend - `teamAnalysis` v Response

```python
"teamAnalysis": {
  "members": [
    {
      "memberId": 1,
      "memberName": "John Doe",
      "maxCapacity": 20,
      "assignedInThisSprint": 8,        # Koľko dostal v TOMTO šprinte
      "crossProjectWorkload": 12,        # Koľko má v INÝCH projektoch
      "totalWorkload": 20,               # Celkovo
      "availableCapacity": 0,            # Koľko mu zostáva
      "utilizationPercentage": 100,
      "status": "at_capacity",           # available/assigned/nearly_full/at_capacity
      "taskCount": 3,
      "reason": "Assigned 8 SP (considering 12 SP from other projects)"
    },
    {
      "memberId": 2,
      "memberName": "Jane Smith",
      "maxCapacity": 20,
      "assignedInThisSprint": 0,         # NEDOSTALA NI Č!
      "crossProjectWorkload": 18,
      "totalWorkload": 18,
      "availableCapacity": 2,
      "utilizationPercentage": 90,
      "status": "nearly_full",
      "taskCount": 0,
      "reason": "Not assigned - has 18 SP in other projects (2 high-priority tasks)"
    },
    // ... všetci ostatní členovia
  ],
  "summary": {
    "totalMembers": 5,
    "assignedMembers": 2,
    "atCapacity": 2,
    "available": 1
  }
}
```

### 2. UI - Nová Vizualizácia

#### Sekcia "Team Capacity Analysis"

Pre **KAŽDÉHO** člena tímu sa zobrazí:

1. **Meno a Status Badge**
   - Available (zelený)
   - Assigned (modrý)
   - Nearly Full (oranžový)
   - At Capacity (červený)

2. **Reasoning Text**
   ```
   "Assigned 8 SP (considering 12 SP from other projects)"
   ```
   alebo
   ```
   "Not assigned - has 18 SP in other projects (2 high-priority tasks)"
   ```

3. **Vizuálny Progress Bar**
   - **Oranžová časť**: SP z iných projektov
   - **Modrá/Zelená časť**: SP z tohto šprintu
   - **Spolu**: Celková záťaž

4. **Kapacita Info**
   ```
   20/20 SP (100% utilized)
   ```

5. **Available Capacity**
   - Zelená: "✓ 5 SP available"
   - Červená: "⚠ At capacity"

#### Summary Stats
```
┌─────────────────┬──────────────┬─────────────┐
│ 2 Assigned Tasks│ 2 At Capacity│ 1 Available │
└─────────────────┴──────────────┴─────────────┘
```

## 🎨 Príklad UI

### Člen Ktorý Dostal Tasky:
```
┌────────────────────────────────────────────────────┐
│ John Doe [Assigned]                    20/20 SP    │
│ Assigned 8 SP (considering 12 SP from other...)    │
│                                                     │
│ ████████████ (orange: 12 SP other)                 │
│ ████████ (blue: +8 SP this) = 20 SP total         │
│                                                     │
│ ⚠ At capacity                                      │
└────────────────────────────────────────────────────┘
```

### Člen Ktorý NEDOSTAL Tasky (Cross-Project Preťažený):
```
┌────────────────────────────────────────────────────┐
│ Jane Smith [Nearly Full]               18/20 SP    │
│ Not assigned - has 18 SP in other projects         │
│ (2 high-priority tasks)                            │
│                                                     │
│ ███████████████ (orange: 18 SP other)              │
│ (no tasks assigned this sprint)                    │
│                                                     │
│ ✓ 2 SP available                                   │
└────────────────────────────────────────────────────┘
```

### Člen Ktorý NEDOSTAL Tasky (Lepší Match):
```
┌────────────────────────────────────────────────────┐
│ Bob Johnson [Available]                8/20 SP     │
│ Not assigned - tasks matched better with others    │
│                                                     │
│ ████ (only 8 SP from other projects)               │
│ (no tasks assigned this sprint)                    │
│                                                     │
│ ✓ 12 SP available                                  │
└────────────────────────────────────────────────────┘
```

## 💡 Benefity

### 1. **Úplná Transparentnosť**
- Vidíš **VŠETKÝCH** členov tímu
- Nie len tých čo dostali tasky
- Jasné dôvody prečo niekto nedostal nič

### 2. **Cross-Project Visibility**
- Presne vidíš koľko má kto v iných projektoch
- Stacked bar chart ukazuje distribúciu
- Oranžová (iné projekty) + Modrá (tento šprint) = Total

### 3. **Actionable Insights**
```
Vidím že:
- John: 20/20 SP (12 z iných projektov) → Preťažený ✓
- Jane: 18/20 SP (všetko z iných projektov) → Preto nedostala nič ✓
- Bob: 8/20 SP (z iných projektov) → Má kapacitu, ale tasky lepšie pasovali iným ✓
```

### 4. **Status na Prvý Pohľad**
- **Zelený badge** "Available" → Má kapacitu
- **Modrý badge** "Assigned" → Dostal tasky
- **Oranžový badge** "Nearly Full" → Takmer plný (>90%)
- **Červený badge** "At Capacity" → Preťažený

### 5. **Lepšie Rozhodovanie**
Používateľ môže:
- Identifikovať kto má kapacitu
- Vidieť kto je preťažený v iných projektoch
- Rozhodnúť sa či znížiť záťaž v iných projektoch
- Alebo pridať nových členov do tímu

## 📊 Data Flow

```
Backend: _build_team_analysis()
    ↓
Pre každého člena vypočíta:
- Cross-project SP
- This sprint SP
- Total workload
- Available capacity
- Status
- Reasoning
    ↓
Frontend: teamAnalysis section
    ↓
Zobrazí VŠETKÝCH členov
s vizuálnymi progress barmi
```

## 🎯 Kedy sa Zobrazuje

1. **Vždy** - Po vygenerovaní plánu
2. **Zvlášť užitočné** keď:
   - Je zapnuté "Consider cross-project workload"
   - Niektorí členovia sú preťažení
   - Nie všetci dostali tasky
   - Chceš vedieť prečo

## 🔧 Technické Detaily

### Backend
- Nová helper funkcia: `_build_team_analysis()`
- Volaná pre každý plán
- Minimálny performance overhead
- Sortované od najviac zaťaženého

### Frontend
- Nová sekcia v UI
- TypeScript interfaces pre type safety
- Responzívny dizajn
- Stacked progress bars
- Status badges s farbami

### Status Logic
```python
if total_sp >= max_capacity:
    status = 'at_capacity'
elif total_sp > max_capacity * 0.9:
    status = 'nearly_full'
elif sprint_sp > 0:
    status = 'assigned'
else:
    status = 'available'
```

### Reasoning Logic
```python
if sprint_sp == 0:  # Nedostal tasky
    if cross_proj_sp > 0:
        "Not assigned - has X SP in other projects"
    elif at_capacity:
        "Not assigned - at maximum capacity"
    else:
        "Not assigned - tasks matched better with others"
else:  # Dostal tasky
    if cross_proj_sp > 0:
        "Assigned X SP (considering Y SP from other projects)"
    else:
        "Assigned X SP"
```

## 📈 Príklady Použitia

### Use Case 1: Prečo Len 2 z 5?
**Pred:**
- Vidím len 2 členov s taskami
- Neviem čo sa deje s ostatnými 3 🤷

**Po:**
- Vidím všetkých 5
- 2 dostali tasky (assigned)
- 2 sú preťažení v iných projektoch (at_capacity)
- 1 má kapacitu ale tasky lepšie pasovali iným (available) ✅

### Use Case 2: Rebalancing Decision
**Situácia:**
```
John: 20/20 SP (12 z iných + 8 tento)
Jane: 18/20 SP (18 z iných + 0 tento)  
Bob: 8/20 SP (8 z iných + 0 tento)
```

**Insight:** Jane a Bob majú minimum v tomto projekte, ale sú zaťažení inde.
**Rozhodnutie:** Treba rebalancovať iné projekty alebo pridať členov ✅

### Use Case 3: Capacity Planning
**Vidím:**
- 3/5 členov at_capacity
- 1/5 nearly_full
- 1/5 available

**Rozhodnutie:** Potrebujem +2 členov alebo znížiť scope ✅

## 🎉 Výsledok

### Pred:
```
Výsledok: 2 členovia dostali tasky
          3 členovia... neviem čo sa deje 🤷
```

### Po:
```
┌─────────────────────────────────────────┐
│ Team Capacity Analysis (Cross-Project)  │
├─────────────────────────────────────────┤
│ John Doe [Assigned]                     │
│ → 8 SP this sprint + 12 SP other        │
│ ████████████████████ 20/20 SP          │
│                                         │
│ Jane Smith [At Capacity]                │
│ → 0 SP this sprint + 18 SP other        │
│ ████████████████ 18/20 SP              │
│                                         │
│ Bob Johnson [Available]                 │
│ → 0 SP this sprint + 8 SP other         │
│ ████████ 8/20 SP                       │
│                                         │
│ [+ 2 more members...]                   │
└─────────────────────────────────────────┘
```

**Všetko je jasné! ✅**

## 🚀 Zhrnutie

✅ **Zobrazuje VŠETKÝCH členov tímu** (nie len assigned)
✅ **Jasné dôvody** prečo niekto nedostal tasky
✅ **Cross-project visibility** cez farebné progress bary
✅ **Status badges** na rýchle zistenie stavu
✅ **Summary stats** pre celkový prehľad
✅ **Actionable insights** pre rozhodovanie

**Výsledok**: Úplná transparentnosť workloadu naprieč celým tímom! 🎉

---

*Implementované: 2024 | Full team visibility with cross-project workload*

