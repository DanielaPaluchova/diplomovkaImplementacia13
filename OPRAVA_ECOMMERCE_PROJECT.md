# 🔧 Oprava problému s E-commerce Platform Redesign

## 🔍 Čo sa pravdepodobne stalo

Pred opravou si spustila smart sprint planning **bez zaškrtnutia "Close Active Sprint"**, čo vytvorilo **2 aktívne sprinty**:
- Sprint 4 (pôvodný aktívny)
- Sprint 5 (nový, ktorý sa mal vytvoriť)

Frontend zobrazuje len **prvý aktívny sprint** (Sprint 4), preto nevidíš Sprint 5.

---

## 📋 Krok za krokom - Diagnostika a oprava

### KROK 1: Otvor databázový klient

Použi napr. DBeaver, SQLite Browser, alebo príkazový riadok:

```bash
# Ak používaš SQLite
sqlite3 backend/project_management.db
```

### KROK 2: Nájdi ID projektu

```sql
SELECT id, name, status
FROM projects
WHERE name LIKE '%E-commerce%' OR name LIKE '%Redesign%';
```

**Zapíš si ID projektu** (napr. `id = 3`)

### KROK 3: Zisti všetky sprinty v projekte

```sql
-- NAHRAĎ 3 skutočným ID projektu z predchádzajúceho kroku
SELECT 
    id,
    name,
    status,
    created_at
FROM sprints
WHERE project_id = 3
ORDER BY created_at DESC;
```

**Očakávaný výsledok:**

```
id | name     | status  | created_at
---|----------|---------|--------------------
9  | Sprint 5 | active  | 2025-11-09 14:30:00
8  | Sprint 4 | active  | 2025-11-09 10:00:00  <- TOTO JE PROBLÉM!
7  | Sprint 3 | completed | 2025-11-08 ...
```

### KROK 4: Over koľko aktívnych sprintov máš

```sql
SELECT 
    COUNT(*) as active_sprint_count,
    GROUP_CONCAT(name) as sprint_names
FROM sprints
WHERE project_id = 3 AND status = 'active';
```

**Ak vidíš:**
- `active_sprint_count = 2` → Máš problém (2 aktívne sprinty)
- `active_sprint_count = 1` → OK (ale možno Sprint 5 neexistuje)

---

## ✅ RIEŠENIE - Oprav databázu

### Variant A: Máš 2 aktívne sprinty (Sprint 4 a Sprint 5)

**RIEŠENIE:** Uzavri Sprint 4

```sql
-- 1. Over ID Sprint 4
SELECT id FROM sprints 
WHERE project_id = 3 AND name = 'Sprint 4';

-- Zapíš si ID (napr. id = 8)

-- 2. Uzavri Sprint 4
UPDATE sprints 
SET status = 'completed', 
    updated_at = CURRENT_TIMESTAMP
WHERE id = 8 AND project_id = 3;

-- 3. Over že máš len 1 aktívny sprint (Sprint 5)
SELECT id, name, status 
FROM sprints 
WHERE project_id = 3 AND status = 'active';
```

**Očakávaný výsledok:** Mal by si vidieť len Sprint 5 ako active

---

### Variant B: Sprint 5 sa vytvoril ako 'planned' namiesto 'active'

```sql
-- 1. Over stav Sprint 5
SELECT id, name, status 
FROM sprints 
WHERE project_id = 3 AND name = 'Sprint 5';

-- Ak je status = 'planned', oprav to:

-- 2. Uzavri Sprint 4
UPDATE sprints 
SET status = 'completed', 
    updated_at = CURRENT_TIMESTAMP
WHERE id = 8 AND project_id = 3;

-- 3. Aktivuj Sprint 5
UPDATE sprints 
SET status = 'active', 
    updated_at = CURRENT_TIMESTAMP
WHERE id = 9 AND project_id = 3;
```

---

### Variant C: Sprint 5 sa vôbec nevytvoril

```sql
-- 1. Uzavri Sprint 4
UPDATE sprints 
SET status = 'completed', 
    updated_at = CURRENT_TIMESTAMP
WHERE project_id = 3 AND name = 'Sprint 4';

-- 2. Potom choď do aplikácie a spusti smart sprint planning znova
--    (teraz už s opraveným kódom, takže bude fungovať správne)
```

---

## 🔄 Po oprave

### 1. Refreshni aplikáciu

```
Ctrl + F5  (hard refresh)
```

### 2. Prejdi na projekt "E-commerce Platform Redesign"

Mal by si vidieť:
- ✅ **Active Sprint:** Sprint 5
- ✅ Tasky priradené k Sprint 5 sú viditeľné
- ✅ Sprint 4 je v "Completed Sprints"

---

## 🛡️ Prevencia do budúcna

**Backend fix** (ktorý sme implementovali) zabráni tomuto problému:
- Ak existuje aktívny sprint a nezaškrtneš "Close active sprint", Apply tlačidlo bude **zablokované**
- Nemôžeš vytvoriť druhý aktívny sprint

---

## 📞 Ak niečo nefunguje

### Skontroluj backend logy:

```bash
# Spusti backend v debug móde
cd backend
python app.py
```

### Pozri sa na chybové hlášky:
- Ak vidíš error pri apply, pošli mi ho
- Skontroluj či backend beží na `http://localhost:5000`

---

## 🎯 Zhrnutie krokov

1. ✅ Otvor databázu
2. ✅ Nájdi ID projektu (query #1)
3. ✅ Zisti všetky sprinty (query #2)
4. ✅ Over koľko je aktívnych (query #3)
5. ✅ Uzavri Sprint 4 (UPDATE query podľa variantu)
6. ✅ Refreshni aplikáciu
7. ✅ Over že vidíš Sprint 5 ako aktívny

---

**Potrebuješ pomoc s vykonaním SQL dotazov? Daj vedieť a pomôžem ti krok za krokom!** 🚀


