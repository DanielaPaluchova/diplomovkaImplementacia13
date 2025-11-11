# Analýza Smart Sprint Planning - Problém s Apply Button

## 🔍 Diagnostika tvojho problému

Popísala si tento scenár:

> "v tom projekte aktívne prebiehal sprint a ked som klikla na ten projekt, nič mi nevytvorilo, ani v plánovaných nebol"

### Čo sa stalo:

**Vznikli TI 2 aktívne sprinty súčasne, ale frontend zobrazuje len prvý!**

### Prečo sa to stalo:

1. Mal si aktívny sprint v projekte
2. Klikla si na "Generate Plan" bez zaškrtnutia "Close Active Sprint"
3. Backend vygeneroval plán s úlohami, ktoré NIE SÚ v aktívnom sprinte
4. Klikla si "Apply"
5. Backend **NEZATVORIL** starý sprint a vytvoril **nový aktívny sprint**
6. Teraz máš 2 sprinty so statusom `'active'`
7. Frontend zobrazuje len **prvý** aktívny sprint (používa `.find()`)
8. Tasky sú ale priradené k **druhému** sprintu
9. **Preto ich nevidíš!**

---

## ✅ Ako to overiť

Otvor databázový klient a spusti tento query:

```sql
-- Zobraz všetky sprinty v tvojom projekte
SELECT
    id,
    name,
    status,
    start_date,
    end_date,
    planned_story_points,
    created_at
FROM sprints
WHERE project_id = [TVOJ_PROJECT_ID]  -- Nahraď skutočným ID
ORDER BY created_at DESC;
```

**Očakávaný výsledok:**
Uvidíš 2 riadky so statusom `'active'`

---

## 🔧 Okamžité riešenie

### Spôsob 1: Cez databázu (najrýchlejší)

```sql
-- 1. Najprv zisti ID starého sprintu (ten s nižším ID alebo starším created_at)
SELECT id, name, status, created_at
FROM sprints
WHERE project_id = [TVOJ_PROJECT_ID] AND status = 'active'
ORDER BY id ASC;

-- 2. Uzavri starý sprint
UPDATE sprints
SET status = 'completed'
WHERE id = [ID_STAREHO_SPRINTU];

-- 3. Refreshni stránku v prehliadači
```

### Spôsob 2: Cez aplikáciu

1. Prejdi do projektu
2. Klikni na tab "Sprints"
3. Nájdi starší sprint
4. Označ ho ako "Completed"

---

## 🛡️ Riešenie pre budúcnosť - Implementované FIXy

### ✅ FIX 1: Backend validácia (IMPLEMENTOVANÉ)

Zmenil som súbor `backend/app/routes/smart_sprint.py`:

**ČO SA ZMENILO:**

- Backend teraz kontroluje, či už existuje aktívny sprint
- Ak existuje a `closeActiveSprint` je `false`, **vráti chybu 400**
- Zabráni vytvoriť druhý aktívny sprint

**KÓD:**

```python
# Ak existuje aktívny sprint a closeActiveSprint je false, vráti error
if active_sprint and not close_active_sprint:
    return jsonify({
        'error': 'Cannot create new active sprint while another sprint is active',
        'message': f'Sprint "{active_sprint.name}" is currently active. Please close it first or enable "Close Active Sprint" option.',
        'activeSprint': active_sprint.to_dict()
    }), 400
```

### ✅ FIX 2: Frontend - Zablokovanie Apply tlačidla (IMPLEMENTOVANÉ)

Zmenil som súbor `src/pages/SmartSprintPlanningPage.vue`:

**ČO SA ZMENILO:**

1. **Apply tlačidlo je ZABLOKOVANÉ** ak existuje aktívny sprint a nemáš zaškrtnuté "Close Active Sprint"
2. Pri hover nad zablokovaným tlačidlom sa zobrazí tooltip s vysvetlením
3. Warning banner jasne komunikuje, že MUSÍŠ zaškrtnúť checkbox
4. Checkbox má tiež tooltip s vysvetlením

**VÝSLEDOK:**

- ✅ Nie je možné omylom vytvoriť druhý aktívny sprint
- ✅ Jasná vizuálna spätná väzba (zablokované tlačidlo)
- ✅ Tooltip vysvetlí prečo nemôžeš kliknúť Apply
- ✅ Banner ťa navádza k správnemu riešeniu

**Vizuálna komunikácia:**

- Apply button: **zablokovaný** (šedý) ak `!canApplyPlan`
- Tooltip: "Cannot apply: Sprint 'XYZ' is currently active. Please enable 'Close active sprint when applying' option..."
- Banner: Jasný text "To apply a new sprint plan, you must close the active sprint first."

---

## 📊 Všetky možné situácie pri kliknutí "Apply"

| Situácia                       | Close Active Sprint | Čo sa stane                          | Tasky viditeľné? |
| ------------------------------ | ------------------- | ------------------------------------ | ---------------- |
| **1. Žiadny aktívny sprint**   | false               | ✅ Vytvorí sa nový aktívny sprint    | ✅ Áno           |
| **2. Žiadny aktívny sprint**   | true                | ✅ Vytvorí sa nový aktívny sprint    | ✅ Áno           |
| **3. Existuje aktívny sprint** | **false**           | 🚫 **Apply tlačidlo ZABLOKOVANÉ**    | -                |
| **4. Existuje aktívny sprint** | true                | ✅ Starý sa uzavrie, vytvorí sa nový | ✅ Áno           |

### PRED FIXOM (tvoja situácia):

Situácia #3 vytvorila 2 aktívne sprinty → tasky neboli viditeľné

### PO FIXE:

Situácia #3: **Apply tlačidlo je zablokované**, nemôžeš na neho kliknúť → musíš zaškrtnúť "Close Active Sprint" aby sa tlačidlo aktivovalo

---

## 🎯 Odporúčania

### Pre používanie:

1. **Vždy zaškrtni "Close Active Sprint"** ak chceš vytvoriť nový sprint a už máš aktívny sprint
2. Ak nechceš zatvoriť aktívny sprint, aplikácia ti teraz **nedovolí** vytvoriť nový
3. Môžeš ale vygenerovať plán pre budúcnosť (na prezeranie) a aplikovať ho neskôr

### Pre testovanie:

1. Otestuj scenár: aktívny sprint existuje, Close Active Sprint = false → malo by to vrátiť error
2. Otestuj scenár: aktívny sprint existuje, Close Active Sprint = true → malo by to uzavrieť starý a vytvoriť nový
3. Skontroluj v databáze, že nikdy nie sú 2 sprinty so statusom 'active'

---

## 📁 Zmenené súbory

1. **`backend/app/routes/smart_sprint.py`** (riadky 290-309)
   - Pridaná validácia pre dvojitý aktívny sprint
2. **`src/pages/SmartSprintPlanningPage.vue`** (riadky 954-965)
   - Zlepšený warning dialóg pred apply

---

## 🔍 Technické detaily

### Prečo frontend zobrazoval len prvý sprint:

```typescript
// ProjectDetailPage.vue, riadok 2074
const activeSprint = computed(() => project.value.sprints?.find((s) => s.status === 'active'));
```

Metóda `.find()` vráti **len prvý** nájdený aktívny sprint.

### Prečo backend vytváral vždy 'active' sprint:

```python
# smart_sprint.py, riadok 303-309
new_sprint = Sprint(
    project_id=project_id,
    name=sprint_name,
    # ...
    status='active',  # ⚠️ VŽDY 'active', nezávisle od existujúceho sprintu
    # ...
)
```

Pred fixom sa nekontrolovalo, či už aktívny sprint existuje.

---

## ✨ Záver

Tvoj problém bol spôsobený tým, že v jednom projekte vznikli 2 aktívne sprinty.

**Implementované riešenia:**

1. ✅ Backend teraz zabráni vytvoriť druhý aktívny sprint
2. ✅ Frontend jasne upozorní pred problemom
3. ✅ Dokumentácia pre overenie a opravu existujúcich problémov

**Najbližšie kroky:**

1. Oprav existujúci problém v databáze (uzavri starý sprint)
2. Restartuj backend server (aby sa načítal nový kód)
3. Vyskúšaj vytvoriť sprint s aktívnym sprintom - malo by to vrátiť error
4. Zaškrtni "Close Active Sprint" a skús znova - malo by to fungovať

---

Ak máš ďalšie otázky alebo potrebuješ pomoc s implementáciou, daj vedieť! 🚀
