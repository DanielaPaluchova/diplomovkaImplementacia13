# Debug Idle Resource Issue

## Kontrolný zoznam:

### 1. Scope
- [ ] Analyzujem **Current Sprint** (nie Backlog/All Sprints)

### 2. Sprint status
- [ ] Sprint má `status = 'active'`
- [ ] Task je v tomto sprinte (`task.sprint_id = sprint.id`)

### 3. Task assignment
- [ ] Task nemá `raci_responsible` (prázdne alebo null)
- [ ] Task nemá `raci_accountable` (prázdne alebo null)
- [ ] Task má `status != 'Done'`

### 4. Member workload
- [ ] doggy1 má workload <= 40% (má 0%, takže OK)
- [ ] doggy1 je v team_members projektu

### 5. Backend log
Pozri console output pri Analyze, mali by tam byť debug printy ako:
```
Found X unassigned tasks
Member doggy1: workload 0%
```

## Ako testovať:

1. **Vytvor test task:**
   - Name: "Test Idle"
   - Sprint: Current active sprint
   - Status: To Do
   - **RACI: PRÁZDNE** (žiadne Responsible, žiadne Accountable)
   
2. **Spusti Analyze:**
   - Scope: **Current Sprint**
   - Pozri či sa objaví Idle Resource

3. **Ak stále nie:**
   - Skontroluj backend terminal log
   - Pošli mi screenshot

