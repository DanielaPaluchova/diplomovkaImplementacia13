# Fix: Automatická cleanup RACI priradení pri odstránení členov

## 🎯 Problém

Keď sa člen tímu **odstránil z projektu** alebo **vymazal z databázy**, jeho ID zostávalo v RACI priradeniach taskov. To spôsobovalo:

```
Member 5 (ID: 5)
Aktívne projekty: ...
```

Namiesto skutočného mena člena sa zobrazovalo `"Member 5"` pretože člen s ID 5 už neexistoval alebo nebol priradený k projektu.

### Príčina:

Backend **nemal cleanup logiku** pri:
1. Vymazaní člena z databázy (`DELETE /api/teams/{id}`)
2. Odstránení člena z projektu (`PUT /api/projects/{id}` s novým `teamMemberIds`)

## ✅ Riešenie

### 1. Nová pomocná funkcia `cleanup_member_from_tasks()`

**Súbor:** `backend/app/routes/tasks.py` (riadky ~44-91)

```python
def cleanup_member_from_tasks(member_id, project_id=None):
    """
    Remove a team member from all RACI roles in tasks.
    Called when a member is deleted or removed from a project.
    
    Args:
        member_id: ID of the member to remove
        project_id: Optional project ID to limit cleanup to specific project
        
    Returns:
        int: Number of tasks updated
    """
```

**Funkcia:**
- Odstráni `member_id` zo všetkých RACI rolí (R, A, C, I)
- Môže pracovať na všetkých taskoch alebo len v konkrétnom projekte
- Vracia počet upravených taskov

### 2. Upravený `delete_team_member` endpoint

**Súbor:** `backend/app/routes/teams.py` (riadky ~171-205)

**PRED:**
```python
def delete_team_member(member_id):
    member = TeamMember.query.get(member_id)
    db.session.delete(member)
    db.session.commit()
```

**PO:**
```python
def delete_team_member(member_id):
    # Remove member from all RACI roles in all tasks
    updated_tasks = cleanup_member_from_tasks(member_id)
    
    # Remove member from all projects
    projects = Project.query.all()
    for project in projects:
        if project.team_member_ids and member_id in project.team_member_ids:
            project.team_member_ids.remove(member_id)
    
    # Delete member
    db.session.delete(member)
    db.session.commit()
```

**Zmeny:**
1. ✅ Automaticky odstráni člena zo všetkých RACI priradení
2. ✅ Odstráni člena zo všetkých projektov
3. ✅ Vracia počet upravených taskov v odpovedi

### 3. Upravený `update_project` endpoint

**Súbor:** `backend/app/routes/projects.py` (riadky ~113-126)

**PRED:**
```python
if 'teamMemberIds' in data:
    project.team_member_ids = data['teamMemberIds']
```

**PO:**
```python
if 'teamMemberIds' in data:
    old_member_ids = set(project.team_member_ids or [])
    new_member_ids = set(data['teamMemberIds'])
    
    # Find removed members
    removed_members = old_member_ids - new_member_ids
    
    # Cleanup RACI for removed members
    if removed_members:
        from app.routes.tasks import cleanup_member_from_tasks
        for member_id in removed_members:
            cleanup_member_from_tasks(member_id, project_id=project_id)
    
    project.team_member_ids = data['teamMemberIds']
```

**Zmeny:**
1. ✅ Detekuje ktorí členovia boli odstránení z projektu
2. ✅ Pre každého odstráneného člena vyčistí RACI v taskoch tohto projektu
3. ✅ Automatické - nevyžaduje žiadnu akciu od frontendov

### 4. Jednorázový cleanup skript

**Súbor:** `backend/cleanup_orphaned_members.py`

Pre vyčistenie **existujúcich starých dát** v databáze.

**Použitie:**
```bash
cd backend
python cleanup_orphaned_members.py
```

**Čo robí:**
1. Nájde všetkých platných členov v databáze
2. Skontroluje všetky tasky a projekty
3. Odstráni neexistujúce member IDs z RACI priradení
4. Zobrazí report o nájdených problémoch
5. Pýta sa na potvrdenie pred commitom zmien

**Príklad výstupu:**
```
Found 5 valid team members: [1, 2, 3, 4, 6]
Checking 156 tasks...

============================================================
CLEANUP REPORT
============================================================

Orphaned member IDs found: [5]
Number of tasks updated: 12
Number of projects updated: 2

Tasks with orphaned members:
  - Task #45: Implement user authentication
    Project ID: 3
    Removed member IDs: [5]
  - Task #67: Design homepage
    Project ID: 3
    Removed member IDs: [5]

Projects with orphaned members:
  - Project #3: Mobile Banking App
    Removed member IDs: [5]

Do you want to commit these changes? (yes/no):
```

## 📊 Kedy sa cleanup spúšťa

### Automaticky:

1. **Vymazanie člena z databázy**
   - Endpoint: `DELETE /api/teams/{member_id}`
   - Cleanup: Vo všetkých taskoch všetkých projektov

2. **Odstránenie člena z projektu**
   - Endpoint: `PUT /api/projects/{project_id}`
   - Cleanup: V taskoch tohto konkrétneho projektu

### Manuálne:

3. **Jednorázový cleanup existujúcich dát**
   - Skript: `python backend/cleanup_orphaned_members.py`
   - Cleanup: Vyčistí všetky staré orphaned member IDs

## 🎓 Výhody pre užívateľa

1. **Žiadne "Member 5"** - Už sa nezobrazujú neexistujúci členovia
2. **Automatické** - Nevyžaduje žiadnu manuálnu akciu
3. **Konzistentné dáta** - RACI priradenia sú vždy aktuálne
4. **Transparentné** - DELETE endpoint vracia počet upravených taskov

## 🔍 Technické detaily

### Cleanup logika:

**Responsible (R):**
```python
if task.raci_responsible and member_id in task.raci_responsible:
    task.raci_responsible = [m for m in task.raci_responsible if m != member_id]
```

**Accountable (A):**
```python
if task.raci_accountable == member_id:
    task.raci_accountable = None
```

**Consulted (C) & Informed (I):**
```python
# Rovnaká logika ako Responsible
```

### Transakcie:

- Všetky zmeny sú v jednej transakcii
- Pri chybe sa všetko rollbackne
- Žiadne čiastočné zmeny v databáze

### Performance:

- Cleanup je efektívny - len jeden query na task
- Pre veľké databázy môže trvať niekoľko sekúnd
- Jednorázový cleanup skript má progress report

## 📅 Migrácia existujúcich dát

**Kroky:**

1. **Spustite cleanup skript:**
```bash
cd backend
python cleanup_orphaned_members.py
```

2. **Skontrolujte report**
   - Pozrite si zoznam orphaned member IDs
   - Skontrolujte ktoré tasky a projekty budú upravené

3. **Potvrďte zmeny**
   - Napíšte `yes` pre commit
   - Alebo `no` pre rollback

4. **Reštartujte backend**
   - Nové zmeny v kóde sa aplikujú automaticky

## 🐛 Testovanie

**Test scenáre:**

1. ✅ Vymazať člena z databázy → RACI sa vyčistí vo všetkých taskoch
2. ✅ Odstrániť člena z projektu → RACI sa vyčistí v taskoch tohto projektu
3. ✅ Spustiť cleanup skript → Staré orphaned IDs sa vyčistia

## 📅 Dátum

2025-11-13

## ✍️ Autor

AI Assistant (based on user requirements)


