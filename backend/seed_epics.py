"""
Seed Epic data for strategic planning demonstration.
This script adds epics with realistic dependencies to an existing project.
"""
import random
import sys

from app import create_app, db
from app.models.epic import Epic
from app.models.project import Project
from app.models.task import Task


def _default_epics_data():
    return [
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


def _seed_epics_core(
    project_id: int,
    replace_existing: bool,
    assign_tasks: bool,
    interactive: bool,
    verbose: bool,
) -> dict:
    if verbose:
        print(f"\n{'='*60}")
        print(f"SEEDING EPICS FOR PROJECT {project_id}")
        print(f"{'='*60}\n")

    project = db.session.get(Project, project_id)
    if not project:
        msg = f"Error: Project with ID {project_id} not found"
        if verbose:
            print(msg)
        return {'ok': False, 'error': msg, 'project_id': project_id}

    if verbose:
        print(f"[OK] Found project: {project.name}")

    existing_epics = Epic.query.filter_by(project_id=project_id).all()
    if existing_epics:
        if not replace_existing and not interactive:
            msg = f"Skipped: project already has {len(existing_epics)} epics"
            if verbose:
                print(f"[SKIP] {msg}")
            return {
                'ok': True,
                'skipped': True,
                'project_id': project_id,
                'project_name': project.name,
                'existing_epics': len(existing_epics),
                'created_epics': 0,
                'message': msg,
            }

        if interactive and not replace_existing:
            print(f"[WARN] Project already has {len(existing_epics)} epics")
            response = input("Do you want to delete existing epics and create new ones? (yes/no): ")
            replace_existing = response.strip().lower() == 'yes'
            if not replace_existing:
                return {
                    'ok': True,
                    'skipped': True,
                    'project_id': project_id,
                    'project_name': project.name,
                    'existing_epics': len(existing_epics),
                    'created_epics': 0,
                    'message': 'Cancelled by user.',
                }

        if replace_existing:
            for epic in existing_epics:
                tasks = Task.query.filter_by(epic_id=epic.id).all()
                for task in tasks:
                    task.epic_id = None
                db.session.delete(epic)
            db.session.commit()
            if verbose:
                print(f"[OK] Deleted {len(existing_epics)} existing epics")

    epics_data = _default_epics_data()
    created_epics = []
    for epic_data in epics_data:
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
            dependencies=[],
            diagram_position_x=epic_data['position'][0],
            diagram_position_y=epic_data['position'][1],
        )

        db.session.add(epic)
        db.session.flush()
        created_epics.append((epic, epic_data['dependencies']))
        if verbose:
            print(f"[OK] Created epic: {epic.name} (ID: {epic.id})")

    for epic, dep_indices in created_epics:
        if dep_indices:
            epic.dependencies = [created_epics[i - 1][0].id for i in dep_indices]
            if verbose:
                print(f"  -> Set dependencies for '{epic.name}': {epic.dependencies}")

    db.session.commit()

    assigned_count = 0
    if interactive:
        tasks = Task.query.filter_by(project_id=project_id).limit(20).all()
        if tasks:
            print(f"Found {len(tasks)} tasks in project")
            response = input("Do you want to randomly assign some tasks to epics? (yes/no): ")
            assign_tasks = response.strip().lower() == 'yes'

    if assign_tasks:
        tasks = Task.query.filter_by(project_id=project_id).limit(20).all()
        for task in tasks:
            if random.random() < 0.6:
                epic = random.choice([e for e, _ in created_epics])
                task.epic_id = epic.id
                assigned_count += 1
        db.session.commit()
        if verbose:
            print(f"[OK] Assigned {assigned_count} tasks to epics")

    if verbose:
        print(f"\n[OK] Successfully created {len(created_epics)} epics for project '{project.name}'")
        print(f"\n{'='*60}")
        print("EPIC SEEDING COMPLETED")
        print(f"{'='*60}\n")

    return {
        'ok': True,
        'skipped': False,
        'project_id': project_id,
        'project_name': project.name,
        'existing_epics': len(existing_epics),
        'created_epics': len(created_epics),
        'assigned_tasks': assigned_count,
    }


def seed_epics_for_project(
    project_id: int,
    replace_existing: bool = False,
    assign_tasks: bool = False,
    interactive: bool = True,
    use_app_context: bool = True,
    verbose: bool = True,
) -> dict:
    """
    Seed epics for one project.

    - CLI default: interactive flow with optional replacement/task assignment.
    - Programmatic use: set interactive=False for non-blocking automatic seed.
    """
    if use_app_context:
        app = create_app()
        with app.app_context():
            return _seed_epics_core(project_id, replace_existing, assign_tasks, interactive, verbose)
    return _seed_epics_core(project_id, replace_existing, assign_tasks, interactive, verbose)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python seed_epics.py <project_id>")
        print("\nExample:")
        print("  python seed_epics.py 1")
        sys.exit(1)
    
    try:
        project_id = int(sys.argv[1])
        seed_epics_for_project(project_id, interactive=True, use_app_context=True, verbose=True)
    except ValueError:
        print("Error: project_id must be an integer")
        sys.exit(1)
