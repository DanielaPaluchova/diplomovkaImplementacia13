-- SQL dotazy na diagnostiku problému s dvoma aktívnymi sprintmi

-- 1. Zobraz všetky sprinty v projekte (uprav project_id podľa tvojho projektu)
-- NAHRAĎ [tvoj_project_id] skutočným ID projektu
SELECT 
    id,
    name,
    status,
    start_date,
    end_date,
    planned_story_points,
    created_at
FROM sprints
WHERE project_id = [tvoj_project_id]
ORDER BY created_at DESC;

-- 2. Zisti, koľko aktívnych sprintov má každý projekt
SELECT 
    project_id,
    COUNT(*) as active_sprint_count,
    GROUP_CONCAT(name) as sprint_names
FROM sprints
WHERE status = 'active'
GROUP BY project_id
HAVING COUNT(*) > 1;  -- Zobrazí len projekty s viac ako 1 aktívnym sprintom

-- 3. Zobraz tasky priradené k aktívnym sprintom
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
  AND t.project_id = [tvoj_project_id]
ORDER BY t.sprint_id, t.id;

-- 4. Ak potrebuješ FIX - uzavri starší aktívny sprint (najprv over ID!)
-- Najprv nájdi ID starého sprintu pomocou query #1
-- Potom spusti:
-- UPDATE sprints 
-- SET status = 'completed'
-- WHERE id = [id_stareho_aktivneho_sprintu];


