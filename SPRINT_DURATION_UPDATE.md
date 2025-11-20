# Zmena zobrazenia Sprint Duration na Average Task Increase

## 🎯 Problém

Na úrovni sprintu sa zobrazovala **suma PERT Duration** a **suma Adjusted Duration** všetkých taskov, čo je **misleading metrika**, pretože:

- Predpokladá **sekvenčné vykonávanie** taskov (jeden po druhom)
- V realite tasky bežia **paralelne** (viac členov tímu = viac taskov súčasne)
- Skutočná dĺžka sprintu je daná **critical path** + dependencies, nie súčtom
- Napríklad: 3 tasky po 50 dní = 150 dní (nezmysel pre 2-týždňový sprint)

## ✅ Riešenie

Nahradené sumárne duration metriky jednou jasnou metrikou:

### **Average Task Increase %**

Priemerný percentuálny nárast duration taskov kvôli RACI overhead.

**Vzorec:**
```
Average Increase = (Σ Adjusted Duration - Σ PERT Duration) / Σ PERT Duration × 100%
```

**Príklad:**
- PERT suma: 170d
- Adjusted suma: 187d  
- Increase: (187 - 170) / 170 × 100% = **+10.0%**

**Význam:**
Kvôli RACI koordinácii (meetings, code reviews, konzultácie) trvajú tasky v priemere o 10% dlhšie.

---

## 📊 Implementované zmeny

### 1. Active Sprint Summary
**Pred:**
```
┌─────────┬───────────────┬──────────────────┬──────────┐
│ 3 Tasks │ 170.00d PERT │ 170.00d Adjusted │ 0.0%     │
└─────────┴───────────────┴──────────────────┴──────────┘
```

**Po:**
```
┌─────────┬────────────────────────┐
│ 3 Tasks │ +10.0% Avg Increase    │
└─────────┴────────────────────────┘
```

### 2. Past Sprints Summary
Rovnaká zmena aj pre completed sprints.

### 3. Tooltip vysvetlenie
Pri hover na "Average Task Increase":
> "Priemerný percentuálny nárast duration taskov v sprinte kvôli RACI overhead.  
> Počíta sa ako (Σ Adjusted - Σ PERT) / Σ PERT × 100%"

---

## 🎓 Akademické zdôvodnenie pre DP

### Prečo nie suma duration?

> "Na úrovni sprintu nezobrazujeme celkovú duration z dôvodu **paralelného vykonávania taskov**. 
> Suma duration všetkých taskov predpokladá sekvenčné vykonávanie, čo neodráža realitu agilného tímu, 
> kde viacerí členovia pracujú na rôznych taskoch súčasne.
>
> Namiesto toho používame **Average Task Increase %**, ktorý ukazuje celkový trend RACI overhead 
> bez misleading predpokladov o poradí vykonávania taskov."

### Výhody pre výskum:

1. **Merateľný impact RACI koordinácie**
   - Jednoznačná metrika vplyvu overhead
   - Porovnateľná naprieč rôznymi tímami/projektami

2. **Nezávislá od veľkosti tímu**
   - 5-členný tím: +10% increase
   - 10-členný tím: +10% increase (rovnaký overhead)
   - Suma duration by bola kompletne iná

3. **Prediktívna hodnota**
   - Ak priemerný increase = +15%, môžeš očakávať 15% overhead v budúcich šprintoch
   - Užitočné pre capacity planning

---

## 📝 Technická implementácia

### Zmenené súbory:
- `src/pages/PertRaciOptimizationPage.vue`

### Upravené sekcie:
1. **Active Sprint Summary** (riadky ~330-363)
   - Odstránené: PERT Duration card, Adjusted Duration card
   - Ponechané: Tasks card, Average Task Increase card (s novým názvom)

2. **Past Sprints Summary** (riadky ~1142-1178)
   - Rovnaké zmeny ako v Active Sprint

### Computed properties (nezmenené):
- `activeSprintSummary` - už počítal `durationIncrease` správne
- `pastSprintsSummary` - už počítal `durationIncrease` správne

Iba sme zmenili **UI zobrazenie**, výpočty zostali rovnaké.

---

## ✅ Výsledok

### Pred zmenou:
- ❌ Zavádzajúce čísla (170d pre 14-dňový sprint)
- ❌ Nevhodné pre akademickú prezentáciu
- ❌ Ťažko interpretovateľné pre stakeholderov

### Po zmene:
- ✅ Jasná, zrozumiteľná metrika (+10% overhead)
- ✅ Akademicky korektná
- ✅ Vhodná pre výskum a porovnávanie
- ✅ Nezavádzajúca

---

## 🔄 Alternatívne riešenia (neimplementované)

### 1. Critical Path Duration
- Najdlhšia cesta cez dependencies
- Akademicky najpresnejšie, ale zložité na implementáciu

### 2. Maximum Task Duration
- Duration najdlhšieho tasku
- Konzervatívne, ale ignoruje paralelizáciu

### 3. Žiadna duration metrika
- Iba Story Points
- Príliš zjednodušené pre PERT analýzu

---

**Dátum implementácie:** 2025-01-09  
**Implementované pre:** Diplomová práca - PERT + RACI integrácia  
**Autor zmeny:** Na základe analýzy paralelného vykonávania



