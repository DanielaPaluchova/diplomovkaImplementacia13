# Fix: RACI Weighted Workload Tabuľky v PERT+RACI Integration

## 🎯 Problém

V PERT + RACI Optimization stránke boli **nekonzistentné tabuľky** medzi tabmi:

### Pôvodné správanie:

1. **"Minulé Šprinty" tab**: Zobrazoval **priemer RACI workload** z ukončených šprintov
2. **"Budúce Tasky" tab**: Zobrazoval **skutočnú sumu RACI workload** z budúcich/backlog taskov
3. **"Aktívny Šprit" tab**: Keď nebol aktívny šprit, **celá tabuľka sa skryla** (nič sa nezobrazilo)

### Problémy:

- ❌ Tabuľky neboli konzistentné - jedna zobrazovala priemer, druhá sumu
- ❌ Pre budúce tasky sa má používať **historický priemer** na predpovedanie kapacity, nie skutočná suma z budúcich taskov
- ❌ Adjusted Duration pre budúce tasky používala priemer (správne), ale tabuľka zobrazovala sumu (nesprávne)
- ❌ Keď nebol aktívny šprit, tabuľka sa celá skryla namiesto zobrazenia 0 hodnôt

## ✅ Riešenie

### 1. Budúce Tasky tab - Používa priemer z minulých šprintov

**Zmenené v:** `src/pages/PertRaciOptimizationPage.vue` (riadky ~1774-1893)

**Pred:**
```vue
<!-- Používal futureBacklogRaciWeightedWorkload -->
<div v-for="member in futureBacklogRaciWeightedWorkload">
  <!-- Zobrazoval sumu z budúcich taskov -->
</div>
```

**Po:**
```vue
<!-- Používa averageRaciWeightedWorkloadInCurrentProject -->
<div v-for="member in averageRaciWeightedWorkloadInCurrentProject">
  <!-- Zobrazuje PRIEMER z minulých šprintov -->
</div>
```

**Výsledok:**
- ✅ Zobrazuje **rovnaké hodnoty** ako "Minulé Šprinty" tab
- ✅ Konzistentné s výpočtom Adjusted Duration (ktorý už používal priemer)
- ✅ Logické pre predpovedanie kapacity tímu

### 2. Aktívny Šprit tab - Zobrazuje správu keď nie je aktívny šprit

**Zmenené v:** `src/pages/PertRaciOptimizationPage.vue` (riadky ~266-335)

**Pred:**
```vue
<q-card-section v-if="raciWeightedWorkload.length > 0">
  <!-- Tabuľka -->
</q-card-section>
<!-- Nič sa nezobrazilo keď nebol aktívny šprit -->
```

**Po:**
```vue
<q-card flat bordered class="q-mb-lg">
  <q-card-section>
    <div v-if="raciWeightedWorkload.length > 0">
      <!-- Tabuľka -->
    </div>
    <div v-else class="text-center text-grey-7 q-pa-md">
      Žiadny aktívny šprit - všetci členovia majú 0% workload
    </div>
  </q-card-section>
</q-card>
```

**Výsledok:**
- ✅ Keď nie je aktívny šprit, zobrazí sa informačná správa
- ✅ Karta je stále viditeľná, len bez hodnôt

### 3. Odstránená nepoužívaná computed property

**Odstránené:** `futureBacklogRaciWeightedWorkload` computed property (riadky ~3297-3379)

**Dôvod:**
- Táto computed property sa už nepoužíva
- Bola nahradená `averageRaciWeightedWorkloadInCurrentProject`
- Odstránenie prevychádza zmätok a udržuje kód čistý

## 📊 Výsledok

### Pred fixom:

| Tab | Zobrazovaná metrika |
|-----|-------------------|
| Minulé Šprinty | ✅ Priemer z ukončených šprintov |
| Budúce Tasky | ❌ Suma z budúcich taskov |
| Aktívny Šprit | ❌ Skryté keď nie je aktívny |

### Po fixe:

| Tab | Zobrazovaná metrika |
|-----|-------------------|
| Minulé Šprinty | ✅ Priemer z ukončených šprintov |
| Budúce Tasky | ✅ Priemer z ukončených šprintov |
| Aktívny Šprit | ✅ Info správa keď nie je aktívny |

## 🎓 Význam pre užívateľa

1. **Konzistentné predpovedanie:** Tabuľky v "Minulé Šprinty" a "Budúce Tasky" sú **identické**, pretože obe používajú historický priemer

2. **Lepšie plánovanie:** Budúce tasky teraz zobrazujú **očakávanú kapacitu** založenú na histórii, nie súčasné priradenie taskov

3. **Jasnejšie UI:** Keď nie je aktívny šprit, užívateľ vidí jasné vysvetlenie namiesto prázdnej obrazovky

4. **Správne Adjusted Duration:** Tabuľka je teraz konzistentná s výpočtom Adjusted Duration (ktorý už používal priemer)

## 🔍 Technické poznámky

- Adjusted Duration pre budúce tasky **už predtým používala priemer** (správne) - problém bol len v zobrazení tabuľky
- `averageRaciWeightedWorkloadInCurrentProject` počíta priemer **z ukončených šprintov tohto projektu** ale zahŕňa **cross-project workload** (tasky z iných projektov v týchto šprintoch)
- Všetky hodnoty sú zaokrúhlené na celé čísla pre jednoduchšie čítanie

## 📅 Dátum

2025-11-13

## ✍️ Autor

AI Assistant (based on user requirements)


