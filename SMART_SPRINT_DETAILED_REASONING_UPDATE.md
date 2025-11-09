# Smart Sprint Planning - Detailed Capacity Reasoning Update

## 🎯 Problém

Keď bol checkbox "Consider workload from other projects" zapnutý a členovia tímu boli preťažení, systém odmietol priradiť tasky s generickou správou:
```
"No team member has sufficient capacity"
```

**Problém**: Používateľ nevedel:
- Ktorí členovia tímu boli zvažovaní
- Prečo nemohli dostať task
- Koľko majú práce v iných projektoch
- Koľko kapacity im zostáva

## ✨ Riešenie

### 1. **Helper Funkcia**
Vytvoril som `_build_capacity_rejection_reason()` ktorá generuje **detailné vysvetlenie**:

```python
def _build_capacity_rejection_reason(
    self,
    task_sp: int,
    team_members: List[TeamMember],
    member_workloads: Dict[int, float],
    cross_project_workload: Dict[int, float],
    consider_cross_project: bool
) -> Dict:
    """Build detailed reason why task cannot be assigned due to capacity"""
```

### 2. **Čo Teraz Ukazuje**

#### Bez Cross-Project Consideration:
```
Cannot assign - all team members at/over capacity. Team workload: 
John Doe: 20/20 SP (needs 8 SP more); 
Jane Smith: 18/20 SP (needs 8 SP more); 
Bob Johnson: 19/20 SP (needs 8 SP more)
```

#### S Cross-Project Consideration:
```
Cannot assign - all team members at/over capacity. Team workload across all projects: 
John Doe: 20/20 SP (12 SP in other projects, needs 8 SP more); 
Jane Smith: 18/20 SP (10 SP in other projects, needs 8 SP more); 
Bob Johnson: 19/20 SP (15 SP in other projects, needs 8 SP more)
```

### 3. **Aktualizované Algoritmy**

Všetkých **8 algoritmov** teraz používa túto helper funkciu:
- ✅ Priority-Based
- ✅ Workload-Balanced
- ✅ Skill-Match (implicitné cez TeamScoringService)
- ✅ Dependency-Aware
- ✅ Velocity-Based (implicitné)
- ✅ Risk-Optimized
- ✅ Value-Driven
- ✅ Hybrid

## 📊 Príklad Output

### Scenár: 3 tasky, všetci členovia preťažení

**Task 1 (8 SP)** - Selected ✅
```json
{
  "selected": true,
  "reason": "Priority: High. John Doe has 12 SP in other projects",
  "assignedTo": "John Doe",
  "crossProjectSP": 12,
  "crossProjectHighPriority": 2
}
```

**Task 2 (8 SP)** - Rejected ❌
```json
{
  "selected": false,
  "reason": "Cannot assign - all team members at/over capacity. Team workload across all projects: John Doe: 20/20 SP (12 SP in other projects, needs 8 SP more); Jane Smith: 18/20 SP (10 SP in other projects, needs 8 SP more); Bob Johnson: 19/20 SP (15 SP in other projects, needs 8 SP more)",
  "teamCapacityDetails": [
    "John Doe: 20/20 SP (12 SP in other projects, needs 8 SP more)",
    "Jane Smith: 18/20 SP (10 SP in other projects, needs 8 SP more)",
    "Bob Johnson: 19/20 SP (15 SP in other projects, needs 8 SP more)"
  ]
}
```

**Task 3 (5 SP)** - Rejected ❌
```json
{
  "selected": false,
  "reason": "Cannot assign - all team members at/over capacity. Team workload across all projects: John Doe: 20/20 SP (12 SP in other projects, needs 5 SP more); Jane Smith: 18/20 SP (10 SP in other projects, needs 5 SP more); Bob Johnson: 19/20 SP (15 SP in other projects, needs 5 SP more)",
  "teamCapacityDetails": [...]
}
```

## 🎨 UI Display

V tabuľke taskov v kolónke "Reasoning" sa teraz zobrazí:

### Selected Tasks:
- **Task Name**: User Authentication
- **Assigned To**: John Doe
- **Reasoning**: *"Priority: High. John Doe has 12 SP in other projects"*

### Rejected Tasks (s červeným indikátorom):
- **Task Name**: Payment Integration  
- **Assigned To**: —
- **Reasoning**: *"Cannot assign - all team members at/over capacity. Team workload across all projects: John Doe: 20/20 SP..."*

**Tooltip** na hover ukazuje:
- Úplný zoznam všetkých členov tímu
- Ich aktuálne zaťaženie
- Workload z iných projektov
- Potrebné SP pre tento task

## 💡 Benefity

### 1. **Transparentnosť**
- Používateľ presne vie prečo task nebol vybraný
- Vidí konkrétne mená a čísla
- Rozumie workload situácii

### 2. **Actionable Insights**
Používateľ môže:
- Identifikovať najmenej zaťaženého člena
- Vidieť koľko kapacity treba uvoľniť
- Rozhodnúť sa či zatiahnuť ďalšieho člena do projektu
- Upraviť task (rozdeliť na menšie časti)

### 3. **Debug Information**
Pri problémoch s plánovaním:
- Jasne vidieť bottlenecky
- Identifikovať preťažených členov
- Zistiť či je problém v cross-project workload

### 4. **Better UX**
- Žiadne záhadné chybové správy
- Konkrétne dáta namiesto generických správ
- Pomáha pri rozhodovaní

## 🔧 Implementačné Detaily

### Helper Funkcia Features:
1. **Sortovanie**: Členovia zoradení od najmenej zaťaženého
2. **Top 3 Display**: V reason texte len prví 3 (aby nebolo príliš dlhé)
3. **Full Details**: Kompletný zoznam v `teamCapacityDetails`
4. **Conditional Info**: Cross-project info len ak je zapnuté
5. **Clear Format**: `Name: Current/Max SP (Cross-project SP, needs X SP more)`

### Performance:
- **O(n log n)** pre sortovanie členov (typicky 5-10 členov)
- **Minimal Overhead**: Len keď task nie je vybraný
- **Cached Data**: Používa už vypočítané workloads

### Data Structure:
```python
{
  'selected': False,
  'reason': 'Human readable explanation...',
  'teamCapacityDetails': [
    'Member1: X/Y SP (Z SP in other projects, needs N SP more)',
    'Member2: ...',
    ...
  ]
}
```

## 📈 Príklady Použitia

### Use Case 1: Identifikácia Bottleneck
**Situácia**: Plán obsahuje len 2 tasky namiesto 10

**Pred aktualizáciou**:
- 8 taskov: "No team member has sufficient capacity" 🤷

**Po aktualizácii**:
- 8 taskov: "John: 20/20 (15 in others), Jane: 19/20 (12 in others)..."
- **Insight**: Tím je preťažený kvôli iným projektom! ✅

### Use Case 2: Kapacitné Plánovanie
**Situácia**: Potrebujem vedieť koľko členov pridať

**Reasoning ukazuje**:
- Každý člen má 18-20/20 SP
- Cross-project: 10-15 SP každý
- **Rozhodnutie**: Potrebujem +2 členov alebo redukcia v iných projektoch ✅

### Use Case 3: Task Splitting
**Situácia**: 13 SP task nie je vybraný

**Reasoning**:
- Najviac dostupné: 8 SP (u Jane)
- **Rozhodnutie**: Split task na 2x 6-7 SP ✅

## 🎯 Výsledok

### Pred:
```
"No team member has sufficient capacity"
```
❌ Neužitočná informácia
❌ Používateľ nevie čo robiť
❌ Žiadny kontext

### Po:
```
"Cannot assign - all team members at/over capacity. 
Team workload across all projects: 
John Doe: 20/20 SP (12 SP in other projects, needs 8 SP more); 
Jane Smith: 18/20 SP (10 SP in other projects, needs 8 SP more); 
Bob Johnson: 19/20 SP (15 SP in other projects, needs 8 SP more)"
```
✅ Konkrétne mená
✅ Presné čísla
✅ Cross-project context
✅ Actionable informácia

## 🚀 Zhrnutie

Systém teraz poskytuje **profesionálne, detailné vysvetlenia** prečo tasky nemôžu byť priradené:

- 📊 **Konkrétne dáta** namiesto generických správ
- 👥 **Mená členov** s ich aktuálnym workloadom
- 🌐 **Cross-project info** keď je relevantné
- 💡 **Actionable insights** pre rozhodovanie
- 🎯 **Transparentnosť** v algoritme

**Výsledok**: Lepšie rozhodnutia, jasnejšie porozumenie, spokojnejší používatelia! 🎉

---

*Implementované: 2024 | All 8 algorithms updated*

