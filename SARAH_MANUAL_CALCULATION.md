# Sarah Johnson (ID=4) - Manuálna Analýza Workloadu

## RACI Workload Weights:
- **Responsible (R)**: 1.0 × SP
- **Accountable (A)**: 0.1 × SP  
- **Consulted (C)**: 0.05 × SP
- **Informed (I)**: 0.01 × SP

---

## COMPLETED SPRINTS - Podrobný Rozklad:

### 1. E-commerce Platform - Sprint 1 "Foundation" (completed)

**Tasks kde má Sarah RACI rolu:**

1. **PostgreSQL Schema Design** (13 SP)
   - Sarah: **RESPONSIBLE** → 1.0 × 13 = **13.0**

2. **Docker Setup & CI/CD Pipeline** (8 SP)
   - Sarah: **CONSULTED** → 0.05 × 8 = **0.4**

3. **UI/UX Wireframes & Prototypes** (13 SP)
   - Sarah: **CONSULTED** → 0.05 × 13 = **0.65**

**Sprint 1 Total Workload: 13.0 + 0.4 + 0.65 = 14.05**

---

### 2. E-commerce Platform - Sprint 2 "User Management" (completed)

**Tasks kde má Sarah RACI rolu:**

1. **JWT Authentication System** (13 SP)
   - Sarah: **RESPONSIBLE** → 1.0 × 13 = **13.0**

2. **User Registration Flow** (8 SP)
   - Sarah: **CONSULTED** → 0.05 × 8 = **0.4**

3. **AWS S3 Avatar Upload** (8 SP)
   - Sarah: **CONSULTED** → 0.05 × 8 = **0.4**

4. **Profile Page Design** (13 SP)
   - Sarah: **CONSULTED** → 0.05 × 13 = **0.65**

**Sprint 2 Total Workload: 13.0 + 0.4 + 0.4 + 0.65 = 14.45**

---

### 3. Mobile Banking App - Sprint 1 "Auth Foundation" (completed)

**Tasks kde má Sarah RACI rolu:**

1. **Biometric Auth API** (13 SP)
   - Sarah: **CONSULTED** → 0.05 × 13 = **0.65**

2. **Login UI** (13 SP)
   - Sarah: **CONSULTED** → 0.05 × 13 = **0.65**

3. **AWS Setup** (12 SP)
   - Sarah: **CONSULTED** → 0.05 × 12 = **0.6**

**Sprint 3 Total Workload: 0.65 + 0.65 + 0.6 = 1.9**

---

### 4. Healthcare Portal - Sprint 1 "Patient Records" (completed)

**Tasks kde má Sarah RACI rolu:**

1. **Patient Database** (13 SP)
   - Sarah: **CONSULTED** → 0.05 × 13 = **0.65**

2. **HIPAA Compliance** (13 SP)
   - Sarah: **CONSULTED** → 0.05 × 13 = **0.65**

3. **Patient UI** (14 SP)
   - Sarah: **CONSULTED** → 0.05 × 14 = **0.7**

**Sprint 4 Total Workload: 0.65 + 0.65 + 0.7 = 2.0**

---

## VÝPOČET PRIEMERU:

### Suma všetkých sprint workloadov:
```
14.05 + 14.45 + 1.9 + 2.0 = 32.4
```

### Počet completed šprintov kde má Sarah workload:
```
4 šprinty
```

### Priemerný RACI Weighted Workload:
```
32.4 ÷ 4 = 8.1
```

### Zaokrúhlený priemer:
```
8.1 ≈ 8
```

---

## ⚠️ UPOZORNENIE:

**Ak frontend zobrazuje priemer 13**, znamená to že:

1. **Sú tam ďalšie completed šprinty**, ktoré nie sú v seed_projects.py alebo som ich nenašiel
2. **Alebo databáza obsahuje iné údaje** ako sú v seed súboroch
3. **Alebo existujú ďalšie projekty/šprinty**, ktoré boli pridané dodatočne

---

## AKO TO OVERIŤ:

### Spusti tento SQL query v databáze:

```sql
-- Zisti všetky completed šprinty kde Sarah (ID=4) má workload
WITH sarah_tasks AS (
    SELECT 
        p.name as project_name,
        s.id as sprint_id,
        s.name as sprint_name,
        t.name as task_name,
        t.story_points,
        (CASE WHEN 4 = ANY(t.raci_responsible) THEN 1.0 * COALESCE(t.story_points, 0) ELSE 0 END +
         CASE WHEN t.raci_accountable = 4 THEN 0.1 * COALESCE(t.story_points, 0) ELSE 0 END +
         CASE WHEN 4 = ANY(t.raci_consulted) THEN 0.05 * COALESCE(t.story_points, 0) ELSE 0 END +
         CASE WHEN 4 = ANY(t.raci_informed) THEN 0.01 * COALESCE(t.story_points, 0) ELSE 0 END) as task_workload
    FROM tasks t
    JOIN sprints s ON t.sprint_id = s.id
    JOIN projects p ON s.project_id = p.id
    WHERE s.status = 'completed'
      AND (
        4 = ANY(t.raci_responsible) OR
        t.raci_accountable = 4 OR
        4 = ANY(t.raci_consulted) OR
        4 = ANY(t.raci_informed)
      )
),
sprint_totals AS (
    SELECT 
        project_name,
        sprint_id,
        sprint_name,
        SUM(task_workload) as sprint_workload
    FROM sarah_tasks
    GROUP BY project_name, sprint_id, sprint_name
    HAVING SUM(task_workload) > 0
)
SELECT 
    project_name,
    sprint_name,
    ROUND(sprint_workload::numeric, 2) as workload
FROM sprint_totals
ORDER BY sprint_id;

-- A potom summary:
WITH sarah_tasks AS (
    SELECT 
        s.id as sprint_id,
        (CASE WHEN 4 = ANY(t.raci_responsible) THEN 1.0 * COALESCE(t.story_points, 0) ELSE 0 END +
         CASE WHEN t.raci_accountable = 4 THEN 0.1 * COALESCE(t.story_points, 0) ELSE 0 END +
         CASE WHEN 4 = ANY(t.raci_consulted) THEN 0.05 * COALESCE(t.story_points, 0) ELSE 0 END +
         CASE WHEN 4 = ANY(t.raci_informed) THEN 0.01 * COALESCE(t.story_points, 0) ELSE 0 END) as task_workload
    FROM tasks t
    JOIN sprints s ON t.sprint_id = s.id
    WHERE s.status = 'completed'
      AND (4 = ANY(t.raci_responsible) OR t.raci_accountable = 4 OR 4 = ANY(t.raci_consulted) OR 4 = ANY(t.raci_informed))
),
sprint_totals AS (
    SELECT sprint_id, SUM(task_workload) as sprint_workload
    FROM sarah_tasks
    GROUP BY sprint_id
    HAVING SUM(task_workload) > 0
)
SELECT 
    COUNT(*) as total_sprints,
    ROUND(SUM(sprint_workload)::numeric, 2) as total_workload,
    ROUND(AVG(sprint_workload)::numeric, 2) as average_workload
FROM sprint_totals;
```

---

## ZÁVER:

Podľa seed dát by Sarah mala mať **priemer 8**, nie 13.

Ak vidíš **priemer 13**, znamená to že:
- Databáza obsahuje **viac completed šprintov** ako sú v seed súboroch
- Alebo boli do databázy pridané **dodatočné projekty/šprinty**
- Alebo Sarah má v **iných completed šprintoch väčšiu rolu** (napr. viac Responsible taskov)

**Odporúčam spustiť SQL query vyššie a pozrieť sa na skutočné údaje v databáze!**


