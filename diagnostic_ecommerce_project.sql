-- Diagnostika projektu "E-commerce Platform Redesign"
-- Tieto dotazy ti pomôžu zistiť, čo sa stalo

-- 1. NAJPRV: Nájdi ID projektu "E-commerce Platform Redesign"
SELECT id, name, status
FROM projects
WHERE name LIKE '%E-commerce%' OR name LIKE '%Redesign%';

-- 2. POTOM: Skontroluj všetky sprinty v tomto projekte
--    (NAHRAĎ [PROJECT_ID] ID-čkom z predchádzajúceho query)
SELECT 
    id,
    name,
    status,
    start_date,
    end_date,
    planned_story_points,
    created_at,
    updated_at
FROM sprints
WHERE project_id = [PROJECT_ID]
ORDER BY created_at DESC;

-- 3. Zisti, koľko aktívnych sprintov máš v tomto projekte
SELECT 
    COUNT(*) as active_sprint_count,
    GROUP_CONCAT(id) as sprint_ids,
    GROUP_CONCAT(name) as sprint_names
FROM sprints
WHERE project_id = [PROJECT_ID] AND status = 'active';

-- 4. Zobraz tasky priradené k aktívnym sprintom
SELECT 
    t.id,
    t.name,
    t.sprint_id,
    s.name as sprint_name,
    s.status as sprint_status,
    t.status as task_status
FROM tasks t
JOIN sprints s ON t.sprint_id = s.id
WHERE s.status = 'active' 
  AND t.project_id = [PROJECT_ID]
ORDER BY t.sprint_id, t.id;

-- ============================================================
-- RIEŠENIE - Po zistení problému
-- ============================================================

-- SCENÁR A: Máš Sprint 4 a Sprint 5 oba ako 'active'
-- RIEŠENIE: Uzavri Sprint 4 (starší)

-- Najprv over ID sprintu 4:
-- SELECT id FROM sprints WHERE project_id = [PROJECT_ID] AND name = 'Sprint 4';

-- Potom ho uzavri:
-- UPDATE sprints 
-- SET status = 'completed', updated_at = CURRENT_TIMESTAMP
-- WHERE id = [SPRINT_4_ID] AND project_id = [PROJECT_ID];

-- ============================================================

-- SCENÁR B: Sprint 5 sa vytvoril ako 'planned' namiesto 'active'
-- RIEŠENIE: Aktivuj Sprint 5 a uzavri Sprint 4

-- Uzavri Sprint 4:
-- UPDATE sprints 
-- SET status = 'completed', updated_at = CURRENT_TIMESTAMP
-- WHERE id = [SPRINT_4_ID] AND project_id = [PROJECT_ID];

-- Aktivuj Sprint 5:
-- UPDATE sprints 
-- SET status = 'active', updated_at = CURRENT_TIMESTAMP
-- WHERE id = [SPRINT_5_ID] AND project_id = [PROJECT_ID];

-- ============================================================

-- SCENÁR C: Sprint 5 sa nevytvoril vôbec
-- RIEŠENIE: Manuálne uzavri Sprint 4, potom spusti smart sprint planning znova

-- UPDATE sprints 
-- SET status = 'completed', updated_at = CURRENT_TIMESTAMP
-- WHERE id = [SPRINT_4_ID] AND project_id = [PROJECT_ID];

-- Po tomto choď do aplikácie a spusti smart sprint planning znova

-- ============================================================
-- OVERENIE PO OPRAVE
-- ============================================================

-- Skontroluj že máš len 1 aktívny sprint:
-- SELECT id, name, status 
-- FROM sprints 
-- WHERE project_id = [PROJECT_ID] AND status = 'active';

-- Výsledok by mal byť len 1 riadok!


