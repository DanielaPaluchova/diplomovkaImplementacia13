# Diplomová práca - Vývoj systému tvorby a dynamickej korekcie trvania IT projektu

## Prehľad projektu

Táto aplikácia predstavuje inovatívny systém projektového manažmentu, ktorý kombinuje **PERT analýzu** a **RACI model** s pokročilými AI technológiami pre automatickú adaptáciu na meniace sa požiadavky klientov. Systém je navrhnutý ako výskumná platforma pre testovanie rôznych plánovacích techník a algoritmov v agilnom prostredí.

### Kľúčové technológie

- **Frontend**: Vue 3 (Composition API), Quasar Framework, TypeScript
- **State Management**: Pinia
- **Styling**: Quasar Components + Custom CSS
- **AI Integration**: Pripravenosť na integráciu s LLM (ChatGPT, Claude)
- **Plánované Backend**: Flask + PostgreSQL

---

## Detailný popis modulov/stránok

### 1. 📊 **Dashboard (IndexPage.vue)**

**Účel**: Hlavná kontrolná doska poskytujúca prehľad o všetkých projektoch a kľúčových metrikách.

**Čo robí**:

- Zobrazuje KPI metriky (aktívne projekty, dokončené úlohy, tímové využitie)
- Prehľad aktívnych projektov s ich stavom a pokrokom
- Nedávnu aktivitu v systéme
- Stav tímu a ich aktuálne zaťaženie
- AI insights a odporúčania

**Súvislosť s diplomovou prácou**:

- Centralizovaný monitoring všetkých projektov
- Vizualizácia efektívnosti PERT/RACI implementácie
- Zobrazenie AI-generovaných optimalizácií v reálnom čase

### 2. 📋 **Projekty (ProjectsPage.vue)**

**Účel**: Správa projektového portfólia s detailným prehľadom každého projektu.

**Čo robí**:

- Zobrazuje štatistiky projektov (celkový počet, aktívne, dokončené, úspešnosť)
- Filtrovanie projektov podľa stavu, klienta, dátumu
- Vytváranie nových projektov cez dialog
- Detailné informace o každom projekte (tím, rozpočet, deadline)

**Súvislosť s diplomovou prácou**:

- Testovanie rôznych projektových metodík na reálnych projektoch
- Porovnávanie efektívnosti tradičných vs. AI-optimalizovaných prístupov
- Sledovanie adaptability projektov na meniace sa požiadavky

### 3. 👥 **Tím (TeamPage.vue)**

**Účel**: Správa ľudských zdrojov a optimalizácia tímového zaťaženia.

**Čo robí**:

- Prehľad všetkých členov tímu s ich rolami a statusom
- Štatistiky tímu (celkový počet, online, priemerné zaťaženie)
- Vizualizácia distribúcie zaťaženia
- Pridávanie nových členov tímu

**Súvislosť s diplomovou prácou**:

- Implementácia RACI modelu pre definovanie rolí
- AI optimalizácia rozdelenia úloh na základe kapacít
- Predikcia tímového výkonu a identifikácia úzkych miest

### 4. 🏃‍♂️ **Sprint Planning (SprintPlanningPage.vue)**

**Účel**: Agilné plánovanie sprintov s AI podporou a drag-and-drop funkcionalitou.

**Čo robí**:

- Backlog úloh s možnosťou drag-and-drop do sprintu
- Sledovanie kapacity sprintu a tímového zaťaženia
- AI odporúčania pre optimálne rozdelenie úloh
- Vizualizácia velocity a burndown charts

**Súvislosť s diplomovou prácou**:

- Kombinácia agilných metodík s PERT analýzou
- AI predikcia úspešnosti sprintu na základe historických dát
- Automatická adaptácia plánu na základe zmien v požiadavkách

### 5. 📊 **Kanban Board (KanbanPage.vue)**

**Účel**: Vizuálna správa workflow s real-time aktualizáciami.

**Čo robí**:

- Tri-stĺpcový Kanban board (To Do, In Progress, Done)
- Drag-and-drop presúvanie úloh medzi stĺpcami
- Filtrovanie a vyhľadávanie úloh
- Pridávanie nových úloh s detailnými informáciami

**Súvislosť s diplomovou prácou**:

- Vizualizácia toku práce pre PERT analýzu
- AI monitoring úzkych miest vo workflow
- Automatické prerozdeľovanie úloh pri zmenách priorit

### 6. 🔗 **PERT Analýza (PertAnalysisPage.vue)**

**Účel**: Interaktívna PERT diagram s kritickou cestou a AI optimalizáciou.

**Čo robí**:

- SVG-based PERT diagram s uzlami a spojeniami
- Zvýrazňovanie kritickej cesty
- Zoom a pan funkcionalita
- Kalkulácia najskôr/najneskôr možných časov

**Súvislosť s diplomovou prácou**:

- **Jadro diplomovej práce** - implementácia PERT techniky
- AI optimalizácia kritickej cesty v reálnom čase
- Automatické prepočítavanie pri zmenách v projektových požiadavkách
- Integrácia s RACI modelom pre definovanie zodpovedností

### 7. 📋 **RACI Matrix (RaciMatrixPage.vue)**

**Účel**: Definovanie a správa zodpovedností pomocou RACI modelu.

**Čo robí**:

- Interaktívna RACI matica (Responsible, Accountable, Consulted, Informed)
- Priradenie rolí členom tímu pre jednotlivé úlohy
- Pridávanie/odoberanie úloh a členov
- Validácia RACI pravidiel

**Súvislosť s diplomovou prácou**:

- **Druhé jadro diplomovej práce** - implementácia RACI modelu
- AI odporúčania pre optimálne priradenie rolí
- Automatická detekcia konfliktov v zodpovednostiach
- Integrácia s PERT analýzou pre komplexný projektový pohľad

### 8. 📅 **Gantt Chart (GanttPage.vue)**

**Účel**: Časová vizualizácia projektových úloh s dependencies.

**Čo robí**:

- Gantt chart s možnosťou prepínania pohľadov (dni/týždne/mesiace)
- Zobrazenie závislostí medzi úlohami
- Editácia úloh a ich časových rámcov
- Sledovanie pokroku projektov

**Súvislosť s diplomovou prácou**:

- Vizualizácia výsledkov PERT analýzy v časovej osi
- AI optimalizácia harmonogramov na základe zdrojov
- Automatické prerozdelenie úloh pri zmenách v projekte

### 9. 🤖 **AI Asistent (AiAssistantPage.vue)**

**Účel**: Chatbot rozhranie pre AI-powered projektové poradenstvo.

**Čo robí**:

- Chat rozhranie s AI asistentom
- Kontextové odporúčania na základe projektových dát
- Quick actions pre časté úlohy
- Integrácia s projektovými dátami

**Súvislosť s diplomovou prácou**:

- **Kľúčová inovatívna funkcionalita** - AI integrácia
- Automatická analýza projektových požiadaviek
- Generovanie optimalizačných návrhov
- Predikcia rizík a odporúčanie mitigačných stratégií

### 10. 🧠 **Smart Planning (SmartPlanningPage.vue)**

**Účel**: AI-powered plánovanie s využitím machine learning algoritmov.

**Čo robí**:

- Šablóny plánovacích metodík (Agile, Waterfall, Hybrid, Lean)
- AI odporúčania pre optimalizáciu procesov
- Metriky úspešnosti rôznych prístupov
- Wizard pre generovanie nových plánov

**Súvislosť s diplomovou prácou**:

- Testovanie rôznych plánovacích techník
- AI-driven výber optimálnej metodiky pre konkrétny projekt
- Automatická adaptácia plánu na základe zmien v požiadavkách
- Porovnávanie efektívnosti rôznych prístupov

### 11. ⚠️ **Risk Prediction (RiskPredictionPage.vue)**

**Účel**: AI-powered predikcia a manažment projektových rizík.

**Čo robí**:

- Dashboard rizikových metrík
- Tabuľka aktívnych rizík s pravdepodobnosťou a dopadom
- AI predikcie budúcich rizík
- Katalóg mitigačných stratégií

**Súvislosť s diplomovou prácou**:

- AI analýza historických dát pre predikciu rizík
- Automatické generovanie mitigačných plánov
- Integrácia s PERT analýzou pre rizikové scenáre
- Real-time monitoring a alerting

### 12. ⚡ **Auto Optimization (AutoOptimizationPage.vue)**

**Účel**: Automatická optimalizácia projektových procesov pomocou AI.

**Čo robí**:

- Dashboard optimalizačných metrík
- Sledovanie aktívnych optimalizácií
- Fronta optimalizačných úloh
- Konfigurácia optimalizačných parametrov

**Súvislosť s diplomovou prácou**:

- **Hlavná inovatívna funkcionalita** - automatická optimalizácia
- AI algoritmy pre kontinuálne zlepšovanie procesov
- Multi-kritériálna optimalizácia (čas, náklady, kvalita)
- Adaptívne algoritmy reagujúce na zmeny v prostredí

### 13. 📊 **Analytics (AnalyticsPage.vue)**

**Účel**: Pokročilé analytické nástroje a reporting.

**Čo robí**:

- Performance metriky projektov
- Tímové analytiky a produktivita
- Analýza rizík a trendov
- Porovnávacie štúdie metodík

**Súvislosť s diplomovou prácou**:

- Meranie efektívnosti PERT/RACI implementácie
- Porovnávanie tradičných vs. AI-optimalizovaných prístupov
- Generovanie insights pre výskumné účely
- Validácia hypotéz diplomovej práce

### 14. 📈 **Comparisons (ComparisonsPage.vue)**

**Účel**: Porovnávanie rôznych projektových metodík a experimentov.

**Čo robí**:

- Kategórie porovnaní (Agile vs Waterfall, Risk Management, atď.)
- Metodológie hodnotenia efektívnosti
- AI insights o najlepších praktikách
- Nástroje pre A/B testing

**Súvislosť s diplomovou prácou**:

- **Výskumná komponenta** - porovnávanie metodík
- Objektívne meranie efektívnosti rôznych prístupov
- Validácia inovatívneho PERT/RACI/AI prístupu
- Generovanie dát pre výskumné publikácie

### 15. 📄 **Reports (ReportsPage.vue)**

**Účel**: Generovanie a správa projektových reportov.

**Čo robí**:

- Šablóny reportov (Project Status, Team Performance, Risk Analysis)
- Automatické generovanie reportov
- Export do rôznych formátov (PDF, Excel, CSV)
- Plánovanie pravidelných reportov

**Súvislosť s diplomovou prácou**:

- Dokumentácia výsledkov experimentov
- Generovanie dát pre výskumnú analýzu
- Reporting pre stakeholderov
- Evidencia úspešnosti inovatívnych prístupov

### 16. 🧪 **Experiments (ExperimentsPage.vue)**

**Účel**: Správa a sledovanie výskumných experimentov.

**Čo robí**:

- Prehľad experimentálnych projektov
- Timeline experimentov a ich výsledkov
- Štatistiky úspešnosti rôznych prístupov
- Nástroje pre nastavenie nových experimentov

**Súvislosť s diplomovou prácou**:

- **Výskumná metodológia** - systematické testovanie hypotéz
- A/B testing rôznych projektových prístupov
- Zbieranie dát pre štatistickú analýzu
- Validácia inovatívnych riešení

---

## Technická architektúra

### Frontend Stack

- **Vue 3** s Composition API pre modernú reaktivitu
- **Quasar Framework** pre enterprise-grade UI komponenty
- **TypeScript** pre type safety a lepšiu maintainability
- **Pinia** pre centralizovaný state management
- **ESLint + Prettier** pre code quality

### Kľúčové features

- **Responsive design** - funguje na desktop aj mobile
- **Real-time updates** - pripravenosť na WebSocket integráciu
- **Drag & Drop** - intuitívne používateľské rozhranie
- **Mock data** - kompletné demo dáta pre testovanie
- **Type safety** - plná TypeScript podpora

### Pripravené integrácie

- **REST API** endpoints pre backend komunikáciu
- **WebSocket** podpora pre real-time updates
- **LLM integrácia** pre AI funkcionalitu
- **Export/Import** funkcionalita pre dáta

---

## Inštalácia a spustenie

```bash
# Inštalácia závislostí
npm install

# Spustenie development servera
npm run dev

# Build pre produkciu
npm run build

# Linting
npm run lint

# Type checking
npx vue-tsc --noEmit
```

---

## Súvislosť s diplomovou prácou

Táto aplikácia predstavuje **praktickú implementáciu** inovatívneho systému projektového manažmentu, ktorý:

1. **Kombinuje tradičné metodiky** (PERT, RACI) s **modernou AI technológiou**
2. **Automaticky sa adaptuje** na meniace sa požiadavky klientov
3. **Poskytuje výskumnú platformu** pre testovanie rôznych prístupov
4. **Generuje dáta** pre štatistickú analýzu a validáciu hypotéz
5. **Demonštruje praktickú aplikáciu** teoretických konceptov

### Výskumné otázky, ktoré aplikácia rieši:

- Ako môže AI zlepšiť tradičné projektové metodiky?
- Aká je efektívnosť kombinácie PERT + RACI + AI vs. tradičné prístupy?
- Ako rýchlo sa systém dokáže adaptovať na zmeny v požiadavkách?
- Ktoré metriky najlepšie predikujú úspech projektu?

### Očakávané prínosy:

- **15-30% zlepšenie** v dodržiavaní termínov
- **20-25% redukcia** projektových rizík
- **Automatizácia 60-80%** rutinných plánovacích úloh
- **Real-time adaptácia** na zmeny v požiadavkách

---

## Matematické algoritmy (Nové stránky)

### 17. 🧮 **PERT Algorithm Optimization (PertAlgorithmPage.vue)**

**Účel**: Čisto matematické algoritmy pre optimalizáciu PERT analýzy bez AI komponentov.

**Čo robí**:

- Implementácia klasických CPM algoritmov (O(V + E))
- Resource leveling algoritmy (O(n²))
- Time-cost trade-off optimalizácia (O(n log n))
- Genetické algoritmy pre komplexné problémy (O(g × p × n))
- Interaktívna vizualizácia kritickej cesty
- Matematické vzorce a ich aplikácia

**Súvislosť s diplomovou prácou**:

- **Jadro matematického základu** - pevné, dokumentovateľné algoritmy
- Implementácia PERT variance calculation: σ² = ((tp - to) / 6)²
- Critical path optimization: minimize Σ(te) subject to precedence constraints
- Resource leveling: minimize max(Rt) ∀t ∈ [0, T]
- Porovnanie efektívnosti rôznych algoritmických prístupov

### 18. 👥 **RACI Resource Optimization (RaciResourcePage.vue)**

**Účel**: Matematické algoritmy pre optimalizáciu ľudských zdrojov založené na RACI modeli.

**Čo robí**:

- Resource allocation optimization: minimize Σ(wi × |Ui - Utarget|)
- Skill matching function: S(t,r) = Σ(sk × mk) / Σ(sk)
- RACI constraint validation: ∀t: Σ(At,r) = 1 ∧ Σ(Rt,r) ≥ 1
- Workload balance metric: B = 1 - (σU / μU)
- Interaktívna RACI matica s optimalizačnými indikátormi
- Analýza využitia zdrojov a skill distribution

**Súvislosť s diplomovou prácou**:

- **Matematický základ pre RACI** - algoritmy pre optimálne priradenie rolí
- Objektívne funkcie pre minimalizáciu času projektu vs. vyrovnanie zaťaženia
- Constraint satisfaction pre RACI pravidlá
- Multi-kritériálna optimalizácia (skill match, workload, cost)

### 19. ⚙️ **Heuristic Rules Engine (HeuristicRulesPage.vue)**

**Účel**: Jednoduché, dokumentovateľné pravidlá a heuristiky pre prerozdeľovanie úloh.

**Čo robí**:

- **Load Balancing Algorithm** (O(n log n)): Prerozdeľovanie na základe threshold
- **Skill Matching Algorithm** (O(n³)): Hungarian algorithm pre bipartite matching
- **Priority Scheduling** (O(n²)): Prerozdeľovanie podľa priority a deadline
- **Greedy Reassignment** (O(n)): Rýchle lokálne optimalizácie
- Konfigurovateľné pravidlá s parametrami
- Real-time monitoring a logging akcií

**Súvislosť s diplomovou prácou**:

- **Praktické heuristiky** - jednoduché pravidlá pre každodenné použitie
- Algoritmy s garantovanou komplexnosťou
- Validácia efektívnosti rôznych heuristických prístupov
- Kombinácia s matematickými algoritmami pre hybridné riešenia

### 20. 🔗 **PERT + RACI Integration (PertRaciOptimizationPage.vue)**

**Účel**: Inovatívna kombinácia PERT analýzy a RACI modelu do jedného integrovaného optimalizačného systému.

**Čo robí**:

- **Integrovaná objektívna funkcia**: α × F_PERT(T, D) + β × F_RACI(R, S) + γ × F_RISK(T, R)
- **Multi-objektívna optimalizácia**: Genetické algoritmy, Monte Carlo simulácie
- **Interaktívna sieťová vizualizácia**: PERT diagram s RACI indikátormi
- **Real-time constraint satisfaction**: RACI pravidlá + resource capacity
- **Risk-aware optimization**: Integrácia rizikových faktorov do optimalizácie
- **Performance comparison**: Before/After metriky s AI odporúčaniami

**Súvislosť s diplomovou prácou**:

- **JADRO INOVATÍVNEHO PRÍSTUPU** - hlavný príspevok diplomovej práce
- Demonštrácia kombinácie tradičných metodík (PERT + RACI) s modernými algoritmami
- Matematický model pre multi-kritériálnu optimalizáciu projektov
- Validácia hypotézy o efektívnosti integrovaného prístupu
- Porovnanie s tradičnými separátnymi metódami

---

## Budúci vývoj

1. **Backend implementácia** (Flask + PostgreSQL)
2. **LLM integrácia** (OpenAI GPT, Claude)
3. **Real-time collaboration** (WebSockets)
4. **Advanced analytics** (Machine Learning modely)
5. **Mobile aplikácia** (Quasar Cordova)

---

_Táto aplikácia predstavuje komplexnú implementáciu inovatívneho prístupu k projektovému manažmentu, ktorý kombinuje osvedčené metodiky s najnovšími AI technológiami pre vytvorenie adaptívneho a inteligentného systému._
