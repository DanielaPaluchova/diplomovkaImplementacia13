# Analýza RACI Weighted Workload pre Sarah Johnson

## Ako sa počíta priemer

### RACI Workload Weights (váhy):
```typescript
responsible: 1.0   // 100% váha
accountable: 0.1   // 10% váha  
consulted: 0.05    // 5% váha
informed: 0.01     // 1% váha
```

### Výpočet pre jeden sprint:

Pre každý task v sprinte, kde má Sarah nejakú RACI rolu:

**Ak má Sarah rolu Responsible:**
```
Workload = 1.0 × story_points
```

**Ak má Sarah rolu Accountable:**
```
Workload = 0.1 × story_points
```

**Ak má Sarah rolu Consulted:**
```
Workload = 0.05 × story_points
```

**Ak má Sarah rolu Informed:**
```
Workload = 0.01 × story_points
```

**Sprint Workload** = suma všetkých taskových workloadov v sprinte

### Výpočet priemeru:

```
Priemerný RACI Weighted Workload = 
    (Suma workloadov zo všetkých completed šprintov) 
    ÷ 
    (Počet completed šprintov, kde má Sarah workload > 0)
```

## SQL Query na zistenie všetkých údajov

### 1. Najprv zisti Sarah ID:

```sql
SELECT id, name, max_story_points 
FROM team_members 
WHERE name LIKE '%Sarah%';
```

### 2. Zobraz všetky completed šprinty s taskami kde Sarah má RACI rolu:

```sql
-- Nahraď [SARAH_ID] skutočným ID z predchádzajúceho query
-- Napríklad ak má Sarah ID = 2, nahraď všetky [SARAH_ID] za 2

SELECT 
    p.name as project_name,
    s.id as sprint_id,
    s.name as sprint_name,
    t.id as task_id,
    t.name as task_name,
    t.story_points,
    CASE 
        WHEN [SARAH_ID] = ANY(t.raci_responsible) THEN 'RESPONSIBLE (1.0x)'
        ELSE ''
    END as is_responsible,
    CASE 
        WHEN t.raci_accountable = [SARAH_ID] THEN 'ACCOUNTABLE (0.1x)'
        ELSE ''
    END as is_accountable,
    CASE 
        WHEN [SARAH_ID] = ANY(t.raci_consulted) THEN 'CONSULTED (0.05x)'
        ELSE ''
    END as is_consulted,
    CASE 
        WHEN [SARAH_ID] = ANY(t.raci_informed) THEN 'INFORMED (0.01x)'
        ELSE ''
    END as is_informed
FROM tasks t
JOIN sprints s ON t.sprint_id = s.id
JOIN projects p ON s.project_id = p.id
WHERE s.status = 'completed'
  AND (
    [SARAH_ID] = ANY(t.raci_responsible) OR
    t.raci_accountable = [SARAH_ID] OR
    [SARAH_ID] = ANY(t.raci_consulted) OR
    [SARAH_ID] = ANY(t.raci_informed)
  )
ORDER BY p.name, s.id, t.id;
```

### 3. Python skript na výpočet (spusti v backend priečinku):

Vytvoril som ti súbor `backend/analyze_sarah_workload.py`, ktorý môžeš spustiť:

```bash
cd backend
python analyze_sarah_workload.py
```

Alebo priamo z root priečinka:

```bash
python backend/analyze_sarah_workload.py
```

## Manuálny výpočet z SQL výsledkov:

Pre každý sprint:

1. **Spočítaj všetky tasky v sprinte:**
   - Pre každý task, kde Sarah má RESPONSIBLE: `workload += 1.0 × story_points`
   - Pre každý task, kde Sarah má ACCOUNTABLE: `workload += 0.1 × story_points`
   - Pre každý task, kde Sarah má CONSULTED: `workload += 0.05 × story_points`
   - Pre každý task, kde Sarah má INFORMED: `workload += 0.01 × story_points`

2. **Suma = Sprint Workload**

3. **Na konci:**
   ```
   Priemer = (Suma všetkých sprint workloadov) ÷ (Počet šprintov)
   ```

## Príklad výpočtu:

Predpokladajme, že Sarah má v týchto completed šprintoch:

### Sprint 1 (E-commerce):
- Task A: 10 SP, role: **Responsible** → 1.0 × 10 = **10.0**
- Task B: 5 SP, role: **Responsible** → 1.0 × 5 = **5.0**
- **Sprint 1 Workload: 15.0**

### Sprint 2 (E-commerce):
- Task C: 15 SP, role: **Responsible** → 1.0 × 15 = **15.0**
- **Sprint 2 Workload: 15.0**

### Sprint 3 (E-commerce):
- Task D: 20 SP, role: **Responsible** → 1.0 × 20 = **20.0**
- Task E: 8 SP, role: **Responsible** → 1.0 × 8 = **8.0**
- Task F: 10 SP, role: **Accountable** → 0.1 × 10 = **1.0**
- Task G: 100 SP, role: **Consulted** → 0.05 × 100 = **5.0**
- Task H: 500 SP, role: **Informed** → 0.01 × 500 = **5.0**
- **Sprint 3 Workload: 39.0**

### Sprint 4 (Hotel Management):
- Task I: 3 SP, role: **Accountable** → 0.1 × 3 = **0.3**
- **Sprint 4 Workload: 0.3**

### Sprint 5 (Hotel Management):  
- Task J: 5 SP, role: **Consulted** → 0.05 × 5 = **0.25**
- **Sprint 5 Workload: 0.25**

### Výpočet priemeru:
```
Suma: 15.0 + 15.0 + 39.0 + 0.3 + 0.25 = 69.55
Počet šprintov: 5
Priemer: 69.55 ÷ 5 = 13.91 ≈ **14**
```

**Takto by sme dostali priemer okolo 13-14!**

## Prečo nie je priemer 23 (z 15, 15, 39)?

Pretože výpočet zahŕňa **VŠETKY completed šprinty naprieč VŠETKÝMI projektami**, nie len E-commerce!

Ak máš v analýze priemer **13**, znamená to, že Sarah má workload v **viacerých šprintoch**, kde má menšiu rolu (Accountable, Consulted, Informed) alebo pracuje na malých taskoch.

## Ako overiť presné údaje:

1. Spusti SQL query vyššie (nezabudni nahradiť [SARAH_ID])
2. Alebo spusti Python skript: `python backend/analyze_sarah_workload.py`
3. Skript ti ukáže VŠETKY completed šprinty so všetkými taskami a presný výpočet

---

## Kde sa táto metrika používa:

Táto metrika sa zobrazuje na stránke **PERT + RACI Optimization** v sekcii:

**"Priemerné RACI Weighted Workload (Minulé Šprinty naprieč projektami)"**

A používa sa na:
- Porovnanie historického workloadu členov tímu
- Plánovanie kapacity pre budúce šprinty
- Identifikáciu preťažených/podvyťažených členov tímu



