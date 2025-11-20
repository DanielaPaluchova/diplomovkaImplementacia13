# Zjednodušenie Detailov Člena v PERT+RACI Integration

## 🎯 Zmena

V PERT + RACI Integration stránke, v rozbalených detailoch členov (pri každej RACI role), sa **odstránili dve metriky**:

1. ❌ **Priemerné Weighted SP v tomto projekte**
2. ❌ **Priemerné Weighted SP naprieč projektami**

## ✅ Čo zostalo

V detailoch členov sa teraz zobrazujú iba:
- ✅ **Aktívne projekty** - zoznam projektov kde má člen aktívne tasky
- ✅ **Aktívne šprinty** - zoznam šprintov kde má člen aktívne tasky

## 📝 Dôvody

1. **Jednoduchšie UI** - menej informácií = prehľadnejšie
2. **Relevantné dáta** - aktívne projekty a šprinty sú aktuálnejšie a užitočnejšie
3. **Menej zmätku** - dve podobné metriky (v tomto projekte vs. naprieč projektami) mohli byť mätúce

## 📍 Kde sa zmena prejavila

**Súbor:** `src/pages/PertRaciOptimizationPage.vue`

**Ovplyvnené sekcie:**
- ✅ Responsible (R) - rozbalené detaily členov
- ✅ Accountable (A) - rozbalené detaily člena
- ✅ Consulted (C) - rozbalené detaily členov
- ✅ Informed (I) - rozbalené detaily členov

**Celkovo:** 4 sekcie (jedna pre každú RACI rolu)

## 🎨 Príklad rozbalených detailov po zmene

```
┌─────────────────────────────────────┐
│ Sarah Johnson                        │
│ ID: 4                                │
├─────────────────────────────────────┤
│ Aktívne projekty:                   │
│ Mobile Banking App, Social Media... │
│                                      │
│ Aktívne šprinty:                    │
│ Mobile Banking App: Sprint 4...     │
└─────────────────────────────────────┘
```

**PRED:**
```
┌─────────────────────────────────────┐
│ Sarah Johnson                        │
│ ID: 4                                │
├─────────────────────────────────────┤
│ Priemerné Weighted SP v tomto proj: │
│ 22.92 SP                             │
│ (priemer z minulých šprintov)       │
│                                      │
│ Priemerné Weighted SP naprieč proj: │
│ 10 SP                                │
│ (priemer z minulých šprintov)       │
│                                      │
│ Aktívne projekty:                   │
│ Mobile Banking App, Social Media... │
│                                      │
│ Aktívne šprinty:                    │
│ Mobile Banking App: Sprint 4...     │
└─────────────────────────────────────┘
```

## 🔍 Technické poznámky

- Funkcie `getMemberAverageWeightedSpInProject()` a `getMemberAverageWeightedSpAcrossProjects()` **zostávajú v kóde** - používajú sa na výpočet Adjusted Duration
- Len sa **nezobruzujú v UI** v rozbalených detailoch
- Zmena je čisto vizuálna - žiadna zmena v logike výpočtov

## 📅 Dátum

2025-11-13

## ✍️ Autor

AI Assistant (based on user requirements)


