"""
One-time cleanup script to remove orphaned member IDs from RACI assignments in tasks.
This script finds and fixes tasks that reference non-existent team members.

Usage:
    python cleanup_orphaned_members.py
"""

from app import create_app, db
from app.models.task import Task
from app.models.team_member import TeamMember
from app.models.project import Project

def cleanup_orphaned_members():
    """Remove non-existent member IDs from all RACI assignments"""
    app = create_app()
    
    with app.app_context():
        # Get all valid member IDs
        valid_member_ids = {m.id for m in TeamMember.query.all()}
        print(f"Found {len(valid_member_ids)} valid team members: {sorted(valid_member_ids)}")
        
        # Get all tasks
        tasks = Task.query.all()
        print(f"\nChecking {len(tasks)} tasks...")
        
        updated_tasks = []
        orphaned_members_found = set()
        
        for task in tasks:
            task_updated = False
            task_orphans = []
            
            # Check responsible (array)
            if task.raci_responsible:
                original = task.raci_responsible.copy()
                task.raci_responsible = [m for m in task.raci_responsible if m in valid_member_ids]
                if original != task.raci_responsible:
                    removed = set(original) - set(task.raci_responsible)
                    orphaned_members_found.update(removed)
                    task_orphans.extend(removed)
                    task_updated = True
            
            # Check accountable (single value)
            if task.raci_accountable and task.raci_accountable not in valid_member_ids:
                orphaned_members_found.add(task.raci_accountable)
                task_orphans.append(task.raci_accountable)
                task.raci_accountable = None
                task_updated = True
            
            # Check consulted (array)
            if task.raci_consulted:
                original = task.raci_consulted.copy()
                task.raci_consulted = [m for m in task.raci_consulted if m in valid_member_ids]
                if original != task.raci_consulted:
                    removed = set(original) - set(task.raci_consulted)
                    orphaned_members_found.update(removed)
                    task_orphans.extend(removed)
                    task_updated = True
            
            # Check informed (array)
            if task.raci_informed:
                original = task.raci_informed.copy()
                task.raci_informed = [m for m in task.raci_informed if m in valid_member_ids]
                if original != task.raci_informed:
                    removed = set(original) - set(task.raci_informed)
                    orphaned_members_found.update(removed)
                    task_orphans.extend(removed)
                    task_updated = True
            
            if task_updated:
                db.session.add(task)
                updated_tasks.append({
                    'id': task.id,
                    'name': task.name,
                    'project_id': task.project_id,
                    'orphaned_members': list(set(task_orphans))
                })
        
        # Also cleanup project.team_member_ids
        projects = Project.query.all()
        updated_projects = []
        
        for project in projects:
            if project.team_member_ids:
                original = project.team_member_ids.copy()
                project.team_member_ids = [m for m in project.team_member_ids if m in valid_member_ids]
                if original != project.team_member_ids:
                    removed = set(original) - set(project.team_member_ids)
                    orphaned_members_found.update(removed)
                    db.session.add(project)
                    updated_projects.append({
                        'id': project.id,
                        'name': project.name,
                        'removed_members': list(removed)
                    })
        
        # Print report
        print(f"\n{'='*60}")
        print("CLEANUP REPORT")
        print(f"{'='*60}")
        print(f"\nOrphaned member IDs found: {sorted(orphaned_members_found)}")
        print(f"Number of tasks updated: {len(updated_tasks)}")
        print(f"Number of projects updated: {len(updated_projects)}")
        
        if updated_tasks:
            print(f"\nTasks with orphaned members:")
            for task in updated_tasks:
                print(f"  - Task #{task['id']}: {task['name']}")
                print(f"    Project ID: {task['project_id']}")
                print(f"    Removed member IDs: {task['orphaned_members']}")
        
        if updated_projects:
            print(f"\nProjects with orphaned members:")
            for project in updated_projects:
                print(f"  - Project #{project['id']}: {project['name']}")
                print(f"    Removed member IDs: {project['removed_members']}")
        
        # Ask for confirmation
        if updated_tasks or updated_projects:
            print(f"\n{'='*60}")
            response = input("\nDo you want to commit these changes? (yes/no): ")
            if response.lower() in ['yes', 'y']:
                db.session.commit()
                print("✅ Changes committed successfully!")
            else:
                db.session.rollback()
                print("❌ Changes rolled back. No data was modified.")
        else:
            print("\n✅ No orphaned members found. Database is clean!")

if __name__ == '__main__':
    cleanup_orphaned_members()

