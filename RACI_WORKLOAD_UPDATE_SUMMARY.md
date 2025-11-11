# Súhrn úpravy výpočtu RACI Weighted Workloadu

## ✅ Implementované zmeny

### 1. Computed property `averageRaciWeightedWorkload`
**Súbor:** `src/pages/PertRaciOptimizationPage.vue` (riadky ~2944-3056)

**Čo sa zmenilo:**
- Pridaná mapa `hasResponsibleRole` na sledovanie či má člen Responsible rolu v sprinte
- Pri výpočte RACI workloadu sa teraz označuje keď má člen Responsible rolu
- Sprint sa započíta do priemeru **IBA ak** má člen aspoň 1 task s Responsible rolou
- V započítanom sprinte sa ale **zahŕňa celé RACI zaťaženie** (R×1.0 + A×0.1 + C×0.05 + I×0.01)

**Kľúčový kód:**
```typescript
// Track if member has Responsible role in this sprint
const hasResponsibleRole = new Map<number, boolean>();

// When processing Responsible tasks:
hasResponsibleRole.set(memberId, true);

// When adding to average:
if (workload > 0 && hasResponsible) {
  memberData.totalWorkload += workload;
  memberData.sprintCount += 1;
}
```

### 2. Helper funkcia `memberHasResponsibleRoleInSprint`
**Súbor:** `src/pages/PertRaciOptimizationPage.vue` (riadky ~3255-3270)

**Účel:**
- Kontroluje či má člen Responsible rolu v konkrétnom sprinte
- Používa sa v `getAverageMemberWeightedStoryPoints`

### 3. Funkcia `getAverageMemberWeightedStoryPoints`
**Súbor:** `src/pages/PertRaciOptimizationPage.vue` (riadky ~3272-3303)

**Čo sa zmenilo:**
- Pridaná kontrola pomocou `memberHasResponsibleRoleInSprint`
- Iba šprinty kde má member Responsible sa započítajú do priemeru
- Pridaný komentár vysvetľujúci logiku

### 4. UI aktualizácie
**Súbor:** `src/pages/PertRaciOptimizationPage.vue`

**Miesta zmien:**

#### A) Past Sprints Tab (riadky ~1042-1045)
**Info banner:**
> "Priemer vypočítaný iba zo šprintov kde má člen aspoň jednu úlohu s rolou Responsible,
> ale zahŕňa celé RACI zaťaženie (R+A+C+I) z týchto šprintov."

#### B) Future/Backlog Tab (riadky ~1777-1780)
**Warning banner:**
> "Adjusted Duration pre budúce tasky je vypočítaná na základe priemerného
> zaťaženia zo šprintov kde mal člen rolu Responsible. Zahŕňa celé RACI zaťaženie (R+A+C+I)."

---

## 🎯 Výsledok pre Sarah Johnson (ID=4)

### PRED zmenou:
- Sprint 1 (E-commerce): 14.05 - má Responsible ✅
- Sprint 2 (E-commerce): 14.45 - má Responsible ✅
- Sprint 3 (Banking): 1.9 - iba Consulted ✅
- Sprint 4 (Healthcare): 2.0 - iba Consulted ✅

**Priemer:** (14.05 + 14.45 + 1.9 + 2.0) / 4 = **8.1 ≈ 8**

### PO zmene:
- Sprint 1 (E-commerce): 14.05 - má Responsible ✅ ZAPOČÍTANÝ
- Sprint 2 (E-commerce): 14.45 - má Responsible ✅ ZAPOČÍTANÝ
- Sprint 3 (Banking): 1.9 - iba Consulted ❌ IGNOROVANÝ
- Sprint 4 (Healthcare): 2.0 - iba Consulted ❌ IGNOROVANÝ

**Nový priemer:** (14.05 + 14.45) / 2 = **14.25 ≈ 14**

---

## 📊 Prínos pre diplomovú prácu

### 1. Lepšia presnosť capacity planning
- Filtruje "pozorovateľské" šprinty (iba Consulted/Informed)
- Priemer reflektuje skutočnú kapacitu keď člen aktívne pracuje

### 2. Zachováva výhody RACI modelu
- Stále započítava overhead (A, C, I role)
- Ukazuje celkové zaťaženie vrátane konzultácií a meetings
- Integrácia PERT + RACI je zachovaná

### 3. Realistickejšie metriky
- Senior developer s 12 SP Responsible + 3 SP Consulted = 15 SP workload
- Odráža skutočný čas strávený na projekte
- Lepšia predikcia pre budúce šprinty

### 4. Akademická hodnota
- Inovatívny prístup - nie štandardný Agile
- Experimentálne možnosti (váhy, filtre)
- Porovnateľné s tradičnými metódami

---

## ✅ Verifikácia

### Testovanie:
1. Otvor PERT + RACI Optimization stránku
2. Prejdi na tab "Past Sprints"
3. Skontroluj sekciu "Priemerné RACI Weighted Workload (Minulé Šprinty naprieč projektami)"
4. Sarah Johnson by mala mať priemer **~14** namiesto ~8

### Očakávané správanie:
- Členy s iba Consulted/Informed rolami v sprinte majú tento sprint ignorovaný
- Členy s Responsible rolou majú započítaný celý RACI workload
- Info bannery správne vysvetľujú výpočet

---

## 📝 Dokumentácia

Dokumentačné súbory (ponechané pre referenciu):
- `SARAH_WORKLOAD_ANALYSIS.md` - Detailný návod ako sa počíta priemer
- `SARAH_MANUAL_CALCULATION.md` - Manuálna analýza zo seed dát
- `RACI_WORKLOAD_UPDATE_SUMMARY.md` - Tento súhrn

---

## 🎨 Tooltip so detailmi šprintov

### 5. Interaktívny tooltip (NOVÉ!)
**Súbor:** `src/pages/PertRaciOptimizationPage.vue` (riadky ~1056-1085, 1819-1848)

**Čo sa pridalo:**
- Tooltip pri hover na meno člena
- Zobrazuje zoznam všetkých šprintov použitých v priemere
- Pre každý sprint: názov projektu, názov šprintu, workload
- Celková suma a priemer

**Príklad tooltip obsahu:**
```
Priemer z 2 šprintov:

E-commerce Platform Redesign
Sprint 1 - Foundation: 14 SP

E-commerce Platform Redesign
Sprint 2 - User Management: 14 SP

─────────────────────
Celkom: 28 SP
Priemer: 14 SP
```

**Implementácia:**
- Rozšírený TypeScript typ o `sprintDetails` array
- Pri každom započítanom sprinte sa ukladá: `projectName`, `sprintName`, `workload`
- UI s `q-tooltip` komponentom a `cursor-pointer` class

---

## 🔄 Budúce možnosti rozšírenia

1. **Konfigurovateľné filtre:**
   - UI nastavenie: "Count sprints with: R only / R+A / All roles"
   
2. **Viacero metrík:**
   - Zobraziť obe metriky vedľa seba (s filtrom / bez filtra)
   - Porovnanie pre akademickú analýzu

3. **Experimentovanie s váhami:**
   - UI pre nastavenie RACI váh
   - A/B testovanie rôznych konfigurácií

4. **Rozšírený tooltip:**
   - Graf workloadu v čase
   - Percentuálne rozdelenie R/A/C/I v každom sprinte

---

**Dátum implementácie:** 2025-01-09  
**Posledná aktualizácia:** 2025-01-09 (pridaný tooltip)  
**Implementované pre:** Diplomová práca - PERT + RACI integrácia

