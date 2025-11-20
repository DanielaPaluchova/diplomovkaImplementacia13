# RACI Weights Database Setup

## Prehľad zmien

Implementoval som ukladanie **RACI weights** do databázy namiesto hardcoded konštánt. Teraz sú všetky RACI váhy (pre workload aj adjusted duration) uložené v databáze a možné konfigurovať cez API.

## Čo bolo zmenené

### Backend

1. **Nový model**: `backend/app/models/raci_weights_config.py`
   - Globálna konfigurácia RACI váh pre všetky projekty
   - 2 sady váh:
     - **Workload weights**: Pre výpočet RACI weighted workload (R, A, C, I)
     - **Duration weights**: Pre výpočet adjusted duration (R, A, C, I)
   - Predvolené hodnoty: R=1.0, A=0.1, C=0.05, I=0.01

2. **Nové API routes**: `backend/app/routes/raci_weights.py`
   - `GET /api/raci-weights` - Načítanie konfigurácie
   - `PUT /api/raci-weights` - Aktualizácia konfigurácie
   - Validácia vstupných dát

3. **Migration script**: `backend/create_raci_weights_table.py`
   - Vytvorenie tabuľky `raci_weights_config`
   - Inicializácia s predvolenými hodnotami

### Frontend

1. **API služba**: `src/services/api.ts`
   - `raciWeightsApi.getRaciWeights()` - Načítanie váh
   - `raciWeightsApi.updateRaciWeights()` - Uloženie váh
   - TypeScript interface `RaciWeightsConfig`

2. **Komponenta**: `src/pages/PertRaciOptimizationPage.vue`
   - Načítanie váh z API pri inicializácii
   - Automatické ukladanie váh do databázy pri kliknutí na "Apply"
   - Reset váh aktualizuje databázu
   - Reaktívne váhy (zmeny sa okamžite prejavia vo výpočtoch)

## Ako spustiť migration

### Krok 1: Aktivovať virtuálne prostredie

```powershell
cd backend
.\venv\Scripts\Activate.ps1
```

### Krok 2: Spustiť migration script

```powershell
python create_raci_weights_table.py
```

**Výstup by mal byť:**
```
✓ RACI Weights Configuration table created
✓ Default RACI Weights Configuration created:
  Workload weights: R=1.0, A=0.1, C=0.05, I=0.01
  Duration weights: R=1.0, A=0.1, C=0.05, I=0.01
```

### Krok 3: Reštartovať backend server

```powershell
python run.py
```

## Ako to funguje

### Pri načítaní stránky
1. Frontend zavolá `GET /api/raci-weights`
2. Backend načíta konfiguráciu z databázy (alebo vytvorí predvolenú)
3. Frontend aktualizuje reaktívne premenné `raciWeights` a `raciWorkloadWeights`
4. Všetky výpočty sa automaticky prepočítajú s novými váhami

### Pri zmene váh
1. Užívateľ upraví váhy v UI
2. Klikne na "Apply"
3. Frontend zavolá `PUT /api/raci-weights` s novými hodnotami
4. Backend uloží do databázy a vráti aktualizovanú konfiguráciu
5. Výpočty sa automaticky prepočítajú

### Pri resete váh
1. Užívateľ klikne na "Reset"
2. Frontend nastaví váhy na predvolené hodnoty (R=1.0, A=0.1, C=0.05, I=0.01)
3. Zavolá `PUT /api/raci-weights` na uloženie do databázy
4. Výpočty sa automaticky prepočítajú

## Výhody

1. **Centralizovaná konfigurácia**: Váhy sú uložené na jednom mieste (databáza)
2. **Konzistentnosť**: Všetci užívatelia vidia rovnaké váhy
3. **Flexibilita**: Rôzne váhy pre workload vs. duration
4. **Perzistencia**: Váhy prežijú reštart servera aj prehliadača
5. **Jednoduchá správa**: API pre čítanie/zápis váh

## Migrácia z localStorage

Staré váhy z localStorage (pre duration) sa už nepoužívajú. Pri prvom načítaní sa použijú váhy z databázy.

## Testovanie

### Backend API test
```bash
# Získať aktuálne váhy
curl -X GET http://localhost:5000/api/raci-weights \
  -H "Authorization: Bearer YOUR_TOKEN"

# Aktualizovať váhy
curl -X PUT http://localhost:5000/api/raci-weights \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "workload": {
      "responsible": 1.0,
      "accountable": 0.15,
      "consulted": 0.08,
      "informed": 0.02
    },
    "duration": {
      "responsible": 1.0,
      "accountable": 0.2,
      "consulted": 0.1,
      "informed": 0.05
    }
  }'
```

### Frontend test
1. Otvor stránku PERT + RACI Integration
2. Skontroluj, že váhy sa načítajú z databázy (konzola: `✅ RACI weights loaded from database`)
3. Zmeň váhy a klikni "Apply"
4. Skontroluj notifikáciu "RACI váhy boli úspešne uložené"
5. Refresh stránku a over, že váhy sú zachované

## Databázová schéma

```sql
CREATE TABLE raci_weights_config (
  id INTEGER PRIMARY KEY,
  responsible_workload FLOAT NOT NULL DEFAULT 1.0,
  accountable_workload FLOAT NOT NULL DEFAULT 0.1,
  consulted_workload FLOAT NOT NULL DEFAULT 0.05,
  informed_workload FLOAT NOT NULL DEFAULT 0.01,
  responsible_duration FLOAT NOT NULL DEFAULT 1.0,
  accountable_duration FLOAT NOT NULL DEFAULT 0.1,
  consulted_duration FLOAT NOT NULL DEFAULT 0.05,
  informed_duration FLOAT NOT NULL DEFAULT 0.01,
  created_at DATETIME NOT NULL,
  updated_at DATETIME NOT NULL
);
```

**Poznámka**: V tabuľke je vždy len jeden záznam (singleton pattern), ktorý obsahuje globálnu konfiguráciu váh pre celú aplikáciu.


