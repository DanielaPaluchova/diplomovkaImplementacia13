"""
Seed Epic data for strategic planning demonstration
This script adds epics with realistic dependencies to an existing project
"""
import sys
from app import create_app, db
from app.models.epic import Epic
from app.models.project import Project
from app.models.task import Task

app = create_app()


def seed_epics_for_project(project_id):
    """
    Seed epics for a specific project with realistic dependencies
    
    Example epic structure:
    - Epic 1: User Authentication (no dependencies)
    - Epic 2: User Profile Management (depends on Epic 1)
    - Epic 3: Dashboard & Analytics (depends on Epic 1)
    - Epic 4: Admin Panel (depends on Epic 1, 2)
    - Epic 5: Notifications System (depends on Epic 1)
    - Epic 6: Mobile App (depends on Epic 1, 2, 3)
    """
    with app.app_context():
        print(f"\n{'='*60}")
        print(f"SEEDING EPICS FOR PROJECT {project_id}")
        print(f"{'='*60}\n")
        
        # Check if project exists
        project = Project.query.get(project_id)
        if not project:
            print(f"❌ Error: Project with ID {project_id} not found")
            return
        
        print(f"✓ Found project: {project.name}")
        
        # Check if epics already exist for this project
        existing_epics = Epic.query.filter_by(project_id=project_id).all()
        if existing_epics:
            print(f"⚠ Warning: Project already has {len(existing_epics)} epics")
            response = input("Do you want to delete existing epics and create new ones? (yes/no): ")
            if response.lower() == 'yes':
                for epic in existing_epics:
                    # Set epic_id to null for all tasks in this epic
                    tasks = Task.query.filter_by(epic_id=epic.id).all()
                    for task in tasks:
                        task.epic_id = None
                    db.session.delete(epic)
                db.session.commit()
                print(f"✓ Deleted {len(existing_epics)} existing epics")
            else:
                print("Cancelled.")
                return
        
        # Define epics
        epics_data = [
            {
                'name': 'User Authentication & Security',
                'description': 'Implement complete user authentication system with login, registration, password reset, and OAuth integration. Include security features like 2FA and session management.',
                'status': 'in_progress',
                'business_value': 100,
                'target_release': 'v1.0',
                'pert': {
                    'optimistic': 10,
                    'most_likely': 15,
                    'pessimistic': 25
                },
                'dependencies': [],
                'position': (100, 100)
            },
            {
                'name': 'User Profile Management',
                'description': 'Build user profile system with avatar upload, personal information management, preferences, and privacy settings.',
                'status': 'to_do',
                'business_value': 80,
                'target_release': 'v1.0',
                'pert': {
                    'optimistic': 8,
                    'most_likely': 12,
                    'pessimistic': 18
                },
                'dependencies': [1],  # Depends on User Authentication
                'position': (350, 100)
            },
            {
                'name': 'Dashboard & Analytics',
                'description': 'Create comprehensive dashboard with real-time analytics, charts, KPI tracking, and customizable widgets.',
                'status': 'to_do',
                'business_value': 90,
                'target_release': 'v1.1',
                'pert': {
                    'optimistic': 15,
                    'most_likely': 20,
                    'pessimistic': 30
                },
                'dependencies': [1],  # Depends on User Authentication
                'position': (100, 250)
            },
            {
                'name': 'Admin Panel & User Management',
                'description': 'Develop admin panel for system administrators with user management, role assignment, permissions, and system configuration.',
                'status': 'to_do',
                'business_value': 70,
                'target_release': 'v1.1',
                'pert': {
                    'optimistic': 12,
                    'most_likely': 18,
                    'pessimistic': 25
                },
                'dependencies': [1, 2],  # Depends on User Authentication and Profile
                'position': (600, 100)
            },
            {
                'name': 'Notifications & Communication',
                'description': 'Implement multi-channel notification system (email, SMS, push notifications) with preferences and notification center.',
                'status': 'to_do',
                'business_value': 60,
                'target_release': 'v1.2',
                'pert': {
                    'optimistic': 8,
                    'most_likely': 14,
                    'pessimistic': 20
                },
                'dependencies': [1],  # Depends on User Authentication
                'position': (350, 250)
            },
            {
                'name': 'Mobile Application',
                'description': 'Develop native mobile apps (iOS and Android) with core features, offline mode, and push notifications.',
                'status': 'to_do',
                'business_value': 95,
                'target_release': 'v2.0',
                'pert': {
                    'optimistic': 25,
                    'most_likely': 40,
                    'pessimistic': 60
                },
                'dependencies': [1, 2, 3],  # Depends on Auth, Profile, and Dashboard
                'position': (350, 400)
            },
            {
                'name': 'Payment & Billing System',
                'description': 'Integrate payment gateway, subscription management, invoicing, and billing history.',
                'status': 'to_do',
                'business_value': 85,
                'target_release': 'v1.5',
                'pert': {
                    'optimistic': 10,
                    'most_likely': 16,
                    'pessimistic': 24
                },
                'dependencies': [1, 2],  # Depends on Auth and Profile
                'position': (600, 250)
            },
            {
                'name': 'API & Third-Party Integrations',
                'description': 'Build RESTful API, webhooks system, and integrate with popular third-party services (Slack, Google, Microsoft).',
                'status': 'to_do',
                'business_value': 75,
                'target_release': 'v1.3',
                'pert': {
                    'optimistic': 12,
                    'most_likely': 18,
                    'pessimistic': 28
                },
                'dependencies': [1, 3],  # Depends on Auth and Dashboard
                'position': (100, 400)
            }
        ]
        
        # Create epics
        created_epics = []
        for epic_data in epics_data:
            # Calculate PERT expected
            pert = epic_data['pert']
            pert_expected = (pert['optimistic'] + 4 * pert['most_likely'] + pert['pessimistic']) / 6
            
            epic = Epic(
                project_id=project_id,
                name=epic_data['name'],
                description=epic_data['description'],
                status=epic_data['status'],
                business_value=epic_data['business_value'],
                target_release=epic_data['target_release'],
                pert_optimistic=pert['optimistic'],
                pert_most_likely=pert['most_likely'],
                pert_pessimistic=pert['pessimistic'],
                pert_expected=pert_expected,
                dependencies=[],  # Will be set after all epics are created
                diagram_position_x=epic_data['position'][0],
                diagram_position_y=epic_data['position'][1]
            )
            
            db.session.add(epic)
            db.session.flush()  # Get ID
            created_epics.append((epic, epic_data['dependencies']))
            
            print(f"✓ Created epic: {epic.name} (ID: {epic.id})")
        
        # Set dependencies (now that we have all IDs)
        for epic, dep_indices in created_epics:
            if dep_indices:
                epic_dependencies = [created_epics[i-1][0].id for i in dep_indices]
                epic.dependencies = epic_dependencies
                print(f"  → Set dependencies for '{epic.name}': {epic_dependencies}")
        
        db.session.commit()
        
        print(f"\n✅ Successfully created {len(created_epics)} epics for project '{project.name}'")
        print(f"\nEpic Summary:")
        for epic, _ in created_epics:
            deps = epic.dependencies or []
            deps_str = f" (depends on: {deps})" if deps else " (no dependencies)"
            print(f"  • {epic.name} - BV: {epic.business_value}, Duration: {epic.pert_expected:.1f} days{deps_str}")
        
        # Optional: Assign some existing tasks to epics
        print(f"\n{'='*60}")
        print(f"OPTIONAL: ASSIGN TASKS TO EPICS")
        print(f"{'='*60}\n")
        
        tasks = Task.query.filter_by(project_id=project_id).limit(20).all()
        if tasks:
            print(f"Found {len(tasks)} tasks in project")
            response = input(f"Do you want to randomly assign some tasks to epics? (yes/no): ")
            if response.lower() == 'yes':
                import random
                assigned_count = 0
                for task in tasks:
                    if random.random() < 0.6:  # 60% chance to assign to an epic
                        epic = random.choice([e for e, _ in created_epics])
                        task.epic_id = epic.id
                        assigned_count += 1
                
                db.session.commit()
                print(f"✓ Assigned {assigned_count} tasks to epics")
        
        print(f"\n{'='*60}")
        print(f"EPIC SEEDING COMPLETED!")
        print(f"{'='*60}\n")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python seed_epics.py <project_id>")
        print("\nExample:")
        print("  python seed_epics.py 1")
        sys.exit(1)
    
    try:
        project_id = int(sys.argv[1])
        seed_epics_for_project(project_id)
    except ValueError:
        print("Error: project_id must be an integer")
        sys.exit(1)
