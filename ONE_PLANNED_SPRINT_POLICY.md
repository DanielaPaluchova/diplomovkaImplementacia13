# One Planned Sprint per Project Policy

## 📋 Pravidlo

**Projekt môže mať maximálne 1 planned sprint naraz.**

```
✅ Povolené:
- 1 active sprint + 0 planned sprint
- 0 active sprint + 1 planned sprint
- 1 active sprint + 1 planned sprint

❌ Nepovolené:
- 0 active sprint + 2+ planned sprints
- 1 active sprint + 2+ planned sprints
```

---

## 🎯 Prečo?

### 1. Workload clarity
```
Bez limitu:
Sprint 5 (planned) - 40 SP pre Alice
Sprint 6 (planned) - 35 SP pre Alice
Sprint 7 (planned) - 30 SP pre Alice
→ ❌ Workload chaos! Ktoré započítať?

S limitom:
Sprint 5 (planned) - 40 SP pre Alice
→ ✅ Jasný workload context
```

### 2. Jasný workflow
```
Jira-style workflow:
1. Create planned sprint
2. Review & adjust
3. Start sprint → active
4. Create NEXT planned sprint
→ Sequential, predictable
```

### 3. Prevent over-planning
```
Bez limitu:
Týždeň 1: AI vytvorí Sprint 5, 6, 7, 8
Týždeň 2: Všetko sa zmenilo, 5-8 sú neaktuálne
→ ❌ Waste of planning effort

S limitom:
Týždeň 1: AI vytvorí Sprint 5
Týždeň 1: Sprint 5 starts
Týždeň 2: AI vytvorí Sprint 6 (based on current reality)
→ ✅ Just-in-time planning
```

---

## 🔧 Implementácia

### Backend validácia

#### 1. AI Sprint Planner (`smart_sprint.py`)
```python
# Pred vytvorením šprintu
existing_planned = Sprint.query.filter_by(
    project_id=project_id,
    status='planned'
).first()

if existing_planned:
    return error(400, {
        'message': f'Project already has a planned sprint: "{existing_planned.name}"',
        'existingPlannedSprint': existing_planned.to_dict()
    })
```

#### 2. Manual Sprint Creation (`projects.py`)
```python
# Pri POST /projects/{id}/sprints
if requested_status == 'planned':
    existing_planned = Sprint.query.filter_by(
        project_id=project_id,
        status='planned'
    ).first()
    
    if existing_planned:
        return error(400, {
            'message': f'Project already has a planned sprint: "{existing_planned.name}"'
        })
```

---

## 💬 User Messages

### AI Sprint Planner Error
```
⚠️ Cannot Create Planned Sprint

Project already has a planned sprint: "Sprint 5"

You have two options:
1. Start "Sprint 5" (click Start Sprint button)
2. Delete "Sprint 5" if no longer needed

After that, you can create a new planned sprint.

[Go to Sprint Management]  [Cancel]
```

### Manual Sprint Creation Error
```
⚠️ Cannot Create Sprint

Project already has a planned sprint: "Sprint 5"

Please start or delete the existing planned sprint before creating a new one.

[View Planned Sprint]  [OK]
```

---

## 🎭 User Workflow

### Scenario: AI Planning with existing planned sprint

```
Používateľ:
1. Klikne "Smart Sprint Planning"
2. AI detekuje: Sprint 5 (planned) už existuje
3. Zobrazí error + options:
   → "Start Sprint 5"
   → "Delete Sprint 5"
   → "Cancel"

4a. User klikne "Start Sprint 5":
    → Sprint 5 status → 'active'
    → AI Planning pokračuje
    → Vytvorí Sprint 6 (planned)
    ✅ Success

4b. User klikne "Delete Sprint 5":
    → Sprint 5 deleted
    → AI Planning pokračuje
    → Vytvorí Sprint 6 (planned)
    ✅ Success

4c. User klikne "Cancel":
    → Vráti sa späť
    → Môže manuálne upraviť Sprint 5
```

### Scenario: Manual sprint creation

```
Používateľ:
1. Klikne "Create Sprint" button
2. Vyplní form (name, dates, goal)
3. Status = 'planned' (default)
4. Submit

Backend check:
- Ak existuje planned sprint → error
- User vidí message
- Môže ísť do Sprint Management a vyriešiť

✅ Forced to clean up before creating new
```

---

## 📊 State Transitions

```
┌─────────────┐
│   BACKLOG   │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────┐
│  CREATE PLANNED SPRINT          │
│  (only if no other planned)     │
└──────┬──────────────────────────┘
       │
       ▼
┌─────────────┐
│  PLANNED    │ ◄───┐
│  (1 max)    │     │ Can edit, adjust
└──────┬──────┘     │
       │            │
       ▼            │
 ┌─────────┐       │
 │ START?  ├───NO──┘
 └────┬────┘
      │
     YES
      │
      ▼
┌─────────────┐
│   ACTIVE    │
└──────┬──────┘
       │
       ▼
 ┌──────────┐
 │ COMPLETE │
 └────┬─────┘
      │
      ▼
┌─────────────┐
│  COMPLETED  │
└─────────────┘
```

---

## 🔍 Edge Cases

### Edge Case 1: User creates planned sprint manually, then runs AI
```
Action:
1. User creates Sprint 5 (planned) manually
2. User runs AI Sprint Planner

Result:
❌ AI shows error: "Sprint 5 already exists"

Solution:
→ User must start or delete Sprint 5 first
```

### Edge Case 2: AI creates planned sprint, user edits it heavily
```
Action:
1. AI creates Sprint 5 (planned)
2. User edits extensively (different tasks, assignments)
3. User runs AI again with different parameters

Result:
❌ AI shows error: "Sprint 5 already exists"

Solution:
→ User can:
  a) Delete Sprint 5, let AI create new one
  b) Start Sprint 5 as-is, then let AI create Sprint 6
```

### Edge Case 3: Concurrent users
```
Scenario:
User A runs AI → creates Sprint 5 (planned)
User B runs AI at same time → tries to create Sprint 6 (planned)

Result:
✅ Backend validation catches it
❌ User B gets error: "Sprint 5 already exists"

Solution:
→ User B refreshes and sees Sprint 5
```

---

## 📈 Benefits

### 1. Clear mental model
```
Users think:
"One sprint being planned at a time"
→ Simple, predictable
```

### 2. No workload confusion
```
Workload calculation:
- Active sprints (all projects) ✅
- 1 planned sprint (current project) ✅
→ Clear, unambiguous
```

### 3. Forces discipline
```
Can't create Sprint 7 until Sprint 6 is decided
→ Just-in-time planning
→ Less wasted effort
```

### 4. Prevents clutter
```
Sprint list stays clean:
✅ Sprint 4 (active)
✅ Sprint 5 (planned)

Not:
❌ Sprint 4 (active)
❌ Sprint 5 (planned)
❌ Sprint 6 (planned)
❌ Sprint 7 (planned)
❌ Sprint 8 (planned) ← forgotten experiments
```

---

## 🎨 Frontend Hints

### Smart Sprint Planning Page
```vue
<q-banner v-if="existingPlannedSprint" class="bg-orange-2 q-mb-md">
  <template #avatar>
    <q-icon name="schedule" color="orange" />
  </template>
  
  <div class="text-weight-bold">Existing Planned Sprint Detected</div>
  <div class="q-mt-xs">
    Project has a planned sprint: "{{ existingPlannedSprint.name }}"
  </div>
  <div class="q-mt-sm">
    <q-btn 
      size="sm" 
      color="primary" 
      label="Start Sprint" 
      @click="startSprint(existingPlannedSprint)"
    />
    <q-btn 
      size="sm" 
      flat 
      label="Delete Sprint" 
      @click="confirmDeleteSprint(existingPlannedSprint)"
    />
    <q-btn 
      size="sm" 
      flat 
      label="View Sprint" 
      @click="viewSprint(existingPlannedSprint)"
    />
  </div>
</q-banner>
```

### Sprint Management Page
```vue
<!-- Show clearly which sprint is planned -->
<q-card 
  v-for="sprint in plannedSprints" 
  :key="sprint.id"
  class="bg-blue-1"
>
  <q-card-section>
    <q-badge color="blue" label="PLANNED" />
    <div class="text-h6">{{ sprint.name }}</div>
    <div class="text-caption text-grey-7">
      Only one planned sprint allowed. 
      Start this sprint to create another.
    </div>
  </q-card-section>
</q-card>
```

---

## 🧪 Testing

### Test 1: AI Planner with no planned sprint
```
Given: Project has no planned sprints
When: User runs AI Sprint Planner
Then: ✅ Sprint created with status='planned'
```

### Test 2: AI Planner with existing planned sprint
```
Given: Project has Sprint 5 (planned)
When: User runs AI Sprint Planner
Then: ❌ Error: "Sprint 5 already exists"
And: User sees options to start/delete Sprint 5
```

### Test 3: Manual creation with existing planned
```
Given: Project has Sprint 5 (planned)
When: User creates Sprint 6 with status='planned'
Then: ❌ Error: "Sprint 5 already exists"
```

### Test 4: Start planned sprint, then create new
```
Given: Project has Sprint 5 (planned)
When: User starts Sprint 5 (status → 'active')
And: User runs AI Sprint Planner
Then: ✅ Sprint 6 created with status='planned'
```

### Test 5: Delete planned sprint, then create new
```
Given: Project has Sprint 5 (planned)
When: User deletes Sprint 5
And: User runs AI Sprint Planner
Then: ✅ Sprint 6 created with status='planned'
```

---

## 📝 Documentation for Users

### Help Text
```
💡 One Planned Sprint Policy

Your project can have only ONE planned sprint at a time.

Why?
• Keeps planning focused and clear
• Prevents workload calculation confusion
• Encourages just-in-time planning

Workflow:
1. Create planned sprint (AI or manual)
2. Review and adjust
3. Start sprint when ready
4. Now you can create the next planned sprint

Need to change your plan?
• Edit the existing planned sprint, OR
• Delete it and create a new one
```

---

## 🎯 Summary

**Policy:** Maximum 1 planned sprint per project

**Enforcement:** Backend validation in both AI Planner and manual creation

**Benefits:**
- ✅ Clear workload context
- ✅ Simple mental model
- ✅ Prevents over-planning
- ✅ Forces discipline

**User Impact:**
- ⚠️ Small workflow change
- ✅ Clearer planning process
- ✅ Less confusion overall

**Implementation:** ✅ Done (backend validation added)
