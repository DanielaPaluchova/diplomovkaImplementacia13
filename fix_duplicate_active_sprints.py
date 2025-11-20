#!/usr/bin/env python3
"""
Skript na opravu problému s duplicitnými aktívnymi sprintmi
Použitie: python fix_duplicate_active_sprints.py
"""

import sqlite3
from datetime import datetime

# Cesta k databáze
DB_PATH = 'backend/project_management.db'

def fix_duplicate_active_sprints():
    """Nájde a opraví projekty s viacerými aktívnymi sprintmi"""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("=" * 60)
    print("🔍 Hľadám projekty s duplicitnými aktívnymi sprintmi...")
    print("=" * 60)
    
    # Nájdi projekty s viacerými aktívnymi sprintmi
    cursor.execute("""
        SELECT 
            p.id as project_id,
            p.name as project_name,
            COUNT(s.id) as active_sprint_count
        FROM projects p
        JOIN sprints s ON s.project_id = p.id
        WHERE s.status = 'active'
        GROUP BY p.id, p.name
        HAVING COUNT(s.id) > 1
    """)
    
    projects_with_issues = cursor.fetchall()
    
    if not projects_with_issues:
        print("✅ Výborne! Žiadne projekty s duplicitnými aktívnymi sprintmi.")
        conn.close()
        return
    
    print(f"\n⚠️  Nájdené {len(projects_with_issues)} projekty s problémom:\n")
    
    for project_id, project_name, sprint_count in projects_with_issues:
        print(f"📁 Projekt: {project_name} (ID: {project_id})")
        print(f"   Počet aktívnych sprintov: {sprint_count}")
        
        # Zobraz všetky aktívne sprinty v tomto projekte
        cursor.execute("""
            SELECT id, name, start_date, created_at
            FROM sprints
            WHERE project_id = ? AND status = 'active'
            ORDER BY created_at ASC
        """, (project_id,))
        
        active_sprints = cursor.fetchall()
        
        print(f"\n   Aktívne sprinty:")
        for sprint_id, sprint_name, start_date, created_at in active_sprints:
            print(f"   - {sprint_name} (ID: {sprint_id}, vytvorený: {created_at})")
        
        # Starší sprint (prvý vytvorený) by mal byť uzavretý
        old_sprint_id = active_sprints[0][0]
        old_sprint_name = active_sprints[0][1]
        
        print(f"\n   💡 Odporúčanie: Uzavrieť starší sprint '{old_sprint_name}' (ID: {old_sprint_id})")
        
        response = input(f"\n   Chceš uzavrieť sprint '{old_sprint_name}'? (y/n): ").strip().lower()
        
        if response == 'y':
            # Uzavri starší sprint
            cursor.execute("""
                UPDATE sprints
                SET status = 'completed', 
                    updated_at = ?
                WHERE id = ? AND project_id = ?
            """, (datetime.utcnow().isoformat(), old_sprint_id, project_id))
            
            conn.commit()
            
            print(f"   ✅ Sprint '{old_sprint_name}' bol úspešne uzavretý!")
            
            # Over výsledok
            cursor.execute("""
                SELECT name, status
                FROM sprints
                WHERE project_id = ? AND status = 'active'
            """, (project_id,))
            
            remaining_active = cursor.fetchall()
            print(f"\n   📊 Zostávajúci aktívny sprint:")
            for name, status in remaining_active:
                print(f"   - {name} (status: {status})")
        else:
            print(f"   ⏭️  Preskočené - žiadna zmena")
        
        print("\n" + "-" * 60 + "\n")
    
    conn.close()
    print("=" * 60)
    print("✨ Hotovo!")
    print("=" * 60)
    print("\n💡 Odporúčanie: Refreshni aplikáciu (Ctrl+F5) aby sa zmeny prejavili.\n")

def show_project_sprints(project_name_pattern):
    """Zobraz všetky sprinty pre daný projekt"""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Nájdi projekt
    cursor.execute("""
        SELECT id, name, status
        FROM projects
        WHERE name LIKE ?
    """, (f'%{project_name_pattern}%',))
    
    projects = cursor.fetchall()
    
    if not projects:
        print(f"❌ Projekt obsahujúci '{project_name_pattern}' nebol nájdený.")
        conn.close()
        return
    
    for project_id, project_name, project_status in projects:
        print(f"\n📁 Projekt: {project_name} (ID: {project_id}, Status: {project_status})")
        print("=" * 60)
        
        # Zobraz všetky sprinty
        cursor.execute("""
            SELECT id, name, status, start_date, end_date, created_at
            FROM sprints
            WHERE project_id = ?
            ORDER BY created_at DESC
        """, (project_id,))
        
        sprints = cursor.fetchall()
        
        if not sprints:
            print("   Žiadne sprinty")
        else:
            for sprint_id, name, status, start, end, created in sprints:
                status_icon = "🟢" if status == "active" else "✅" if status == "completed" else "📋"
                print(f"   {status_icon} {name} (ID: {sprint_id})")
                print(f"      Status: {status}")
                print(f"      Vytvorený: {created}")
                print(f"      Trvanie: {start} - {end}")
                print()
    
    conn.close()

if __name__ == "__main__":
    import sys
    
    print("\n" + "=" * 60)
    print("🛠️  Sprint Duplicate Fixer")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        # Ak je zadaný argument, zobraz sprinty pre daný projekt
        project_pattern = sys.argv[1]
        print(f"\n📊 Zobrazujem sprinty pre projekt: {project_pattern}\n")
        show_project_sprints(project_pattern)
    else:
        # Inak spusti automatickú opravu
        print()
        fix_duplicate_active_sprints()
    
    print()



