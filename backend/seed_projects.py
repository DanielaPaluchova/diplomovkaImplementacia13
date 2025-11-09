"""
8 COMPLETE PROJECTS FOR SEED DATABASE
Each project has unique scenarios and intentional issues
Global workload tracked: max 20 SP per person across ALL active sprints
"""
from app import db
from app.models.project import Project
from app.models.sprint import Sprint
from app.models.task import Task
from app.models.project_role import ProjectRole
from app.models.task_history import TaskHistory
from datetime import datetime, timedelta
import random


def create_task_history(task, member_id, sprint_end_date):
    """Create task history for completed task"""
    actual_hours = int(task.estimated_hours * random.uniform(0.8, 1.3))
    performance_score = random.uniform(0.85, 1.0) if actual_hours <= task.estimated_hours else random.uniform(0.7, 0.85)
    
    return TaskHistory(
        task_id=task.id, member_id=member_id, action='completed',
        story_points=task.story_points, actual_hours=actual_hours,
        completed_date=sprint_end_date, performance_score=performance_score,
        notes='Completed successfully'
    )


def create_task_with_dates(project_id, sprint, **kwargs):
    """Helper to create task with start/end dates based on sprint"""
    # Calculate dates if sprint is provided
    if sprint and 'start_date' not in kwargs:
        sprint_duration = (sprint.end_date - sprint.start_date).days
        # Random start within sprint
        days_offset = random.randint(0, max(1, sprint_duration - 3))
        task_start = sprint.start_date + timedelta(days=days_offset)
        # Task duration based on story points (rough estimate: 1 SP = 0.5-1 day)
        sp = kwargs.get('story_points', 5)
        task_duration = max(1, int(sp * random.uniform(0.5, 1.0)))
        task_end = task_start + timedelta(days=task_duration)
        # Ensure doesn't exceed sprint
        if task_end > sprint.end_date:
            task_end = sprint.end_date
        kwargs['start_date'] = task_start
        kwargs['end_date'] = task_end
    
    # Ensure raci_consulted and raci_informed exist (even if empty)
    # NOTE: These should be filled with real people, not the responsible person
    kwargs.setdefault('raci_consulted', [])
    kwargs.setdefault('raci_informed', [])
    
    return Task(project_id=project_id, sprint_id=sprint.id if sprint else None, **kwargs)


def update_project_stats(project):
    """Update project statistics after adding all tasks"""
    from app.models.task import Task
    
    # Count tasks
    all_tasks = Task.query.filter_by(project_id=project.id).all()
    
    # Update total story points (other stats like total_tasks, tasks_completed, and progress are now computed dynamically)
    project.total_story_points = sum(t.story_points for t in all_tasks)
    
    db.session.add(project)


# ====================================================================================
# PROJECT 1: E-COMMERCE PLATFORM - MAIN TESTING PROJECT
# Issues: Giant task, Skill mismatch, Overload, Underutilization, Merge opportunity
# Team: John (8 SP), Sarah (3 SP), Mike (8 SP), Sophie (5 SP), Lisa (1 SP)
# ====================================================================================

def seed_ecommerce(m):
    """Project 1: E-commerce Platform with multiple intentional issues"""
    
    project = Project(
        name='E-commerce Platform Redesign',
        description='Complete UI/UX overhaul with payment integration and real-time inventory',
        template='Agile Development',
        icon='shopping_cart',
        status='In Progress',
        due_date=datetime(2026, 1, 15),
        team_member_ids=[m['john'], m['sarah'], m['mike'], m['sophie'], m['lisa']],
        estimated_duration=120,
        max_story_points_per_person=20
    )
    db.session.add(project)
    db.session.flush()
    
    # Sprint 1 - Completed (June 2024)
    sprint1 = Sprint(
        project_id=project.id, name='Sprint 1 - Foundation', goal='Setup infrastructure and base components',
        start_date=datetime(2024, 6, 1), end_date=datetime(2024, 6, 14),
        status='completed', capacity=100, planned_story_points=34, velocity=34
    )
    db.session.add(sprint1)
    db.session.flush()
    
    # Completed tasks with history
    for name, member, sp, skills in [
        ('Docker Setup & CI/CD Pipeline', m['mike'], 8, ['Docker', 'CI/CD', 'Jenkins']),
        ('PostgreSQL Schema Design', m['sarah'], 13, ['PostgreSQL', 'Database', 'SQL']),
        ('UI/UX Wireframes & Prototypes', m['sophie'], 13, ['Figma', 'Adobe XD', 'Prototyping'])
    ]:
        task = Task(
            project_id=project.id, sprint_id=sprint1.id,
            name=name, title=name, description=f'{name} - completed in Sprint 1',
            status='Done', priority='high', type='task',
            story_points=sp, completed=True,
            labels=['foundation', 'completed'], complexity=6,
            pert_optimistic=sp*3, pert_most_likely=sp*5, pert_pessimistic=sp*7, pert_expected=sp*5,
            raci_responsible=[member], raci_accountable=m['lisa'], raci_consulted=[m['sarah']], raci_informed=[m['sophie'], m['lisa']],
            required_skills=skills, estimated_hours=sp*5, actual_hours=sp*5, risk_level='medium',
        start_date=datetime(2024, 11, 2), end_date=datetime(2024, 11, 12)
    )
        db.session.add(task)
        db.session.flush()
        db.session.add(create_task_history(task, member, sprint1.end_date))
    
    # Sprint 2 - Completed (August 2024)
    sprint2 = Sprint(
        project_id=project.id, name='Sprint 2 - User Management', goal='Authentication and user profiles',
        start_date=datetime(2024, 8, 1), end_date=datetime(2024, 8, 14),
        status='completed', capacity=100, planned_story_points=42, velocity=42
    )
    db.session.add(sprint2)
    db.session.flush()
    
    for name, member, sp, skills in [
        ('JWT Authentication System', m['sarah'], 13, ['Python', 'FastAPI', 'JWT']),
        ('User Registration Flow', m['john'], 8, ['Vue.js', 'JavaScript', 'Forms']),
        ('AWS S3 Avatar Upload', m['mike'], 8, ['AWS', 'S3', 'Storage']),
        ('Profile Page Design', m['sophie'], 13, ['Figma', 'UI Design'])
    ]:
        task = Task(
            project_id=project.id, sprint_id=sprint2.id,
            name=name, title=name, description=f'{name} - completed in Sprint 2',
            status='Done', priority='high', type='feature',
            story_points=sp, completed=True,
            labels=['auth', 'completed'], complexity=7,
            pert_optimistic=sp*3, pert_most_likely=sp*5, pert_pessimistic=sp*7, pert_expected=sp*5,
            raci_responsible=[member], raci_accountable=m['lisa'], raci_consulted=[m['sarah']], raci_informed=[m['sophie'], m['lisa']],
            required_skills=skills, estimated_hours=sp*5, actual_hours=sp*5, risk_level='medium',
        start_date=datetime(2024, 11, 2), end_date=datetime(2024, 11, 12)
    )
        db.session.add(task)
        db.session.flush()
        db.session.add(create_task_history(task, member, sprint2.end_date))
    
    # Sprint 3 - ACTIVE (November 2024) - WITH INTENTIONAL ISSUES!
    sprint3 = Sprint(
        project_id=project.id, name='Sprint 3 - Payment & Analytics', goal='Stripe integration and dashboard',
        start_date=datetime(2024, 11, 1), end_date=datetime(2024, 11, 15),
        status='active', capacity=100, planned_story_points=72, velocity=0
    )
    db.session.add(sprint3)
    db.session.flush()
    
    # ❌ ISSUE #1: Giant Task (34 SP - should be split)
    db.session.add(Task(
        project_id=project.id, sprint_id=sprint3.id,
        name='Complete Stripe Payment Gateway Integration',
        title='Complete Stripe Payment Gateway Integration',
        description='Full Stripe integration with subscriptions, one-time payments, webhooks, and refunds',
        status='To Do', priority='high', type='feature',
        story_points=34, completed=False,
        labels=['payment', 'critical', 'giant-task'], complexity=9,
        pert_optimistic=80, pert_most_likely=120, pert_pessimistic=160, pert_expected=120,
        raci_responsible=[m['sarah']], raci_accountable=m['lisa'], 
        raci_consulted=[m['john'], m['mike']], raci_informed=[m['sophie']],
        required_skills=['Python', 'FastAPI', 'Stripe', 'Webhooks'], 
        estimated_hours=120, actual_hours=0, risk_level='critical',
        start_date=datetime(2024, 11, 2), end_date=datetime(2024, 11, 14)
    ))
    
    # ❌ ISSUE #2: Skill Mismatch (PostgreSQL task assigned to Frontend dev)
    db.session.add(Task(
        project_id=project.id, sprint_id=sprint3.id,
        name='Optimize PostgreSQL Query Performance',
        title='Optimize PostgreSQL Query Performance',
        description='Add indexes, optimize slow queries, implement query caching',
        status='To Do', priority='high', type='task',
        story_points=8, completed=False,
        labels=['database', 'performance', 'skill-mismatch'], complexity=7,
        pert_optimistic=16, pert_most_likely=24, pert_pessimistic=40, pert_expected=26,
        raci_responsible=[m['john']], raci_accountable=m['lisa'], 
        raci_consulted=[m['sarah']], raci_informed=[m['mike']],  # Sarah should consult since she has PostgreSQL skills
        required_skills=['PostgreSQL', 'Database', 'SQL', 'Performance'], 
        estimated_hours=26, actual_hours=0, risk_level='medium',
        start_date=datetime(2024, 11, 3), end_date=datetime(2024, 11, 8)
    ))
    
    # John's legit task (13 SP + 8 SP above = 21 SP - over limit)
    db.session.add(Task(
        project_id=project.id, sprint_id=sprint3.id,
        name='Analytics Dashboard with Charts',
        title='Analytics Dashboard with Charts',
        description='Real-time analytics dashboard with Chart.js visualizations',
        status='In Progress', priority='medium', type='feature',
        story_points=13, completed=False,
        labels=['frontend', 'analytics'], complexity=7,
        pert_optimistic=32, pert_most_likely=48, pert_pessimistic=64, pert_expected=48,
        raci_responsible=[m['john']], raci_accountable=m['lisa'], raci_consulted=[m['sarah']], raci_informed=[m['sophie'], m['lisa']],
        required_skills=['Vue.js', 'Chart.js', 'JavaScript'], 
        estimated_hours=48, actual_hours=0, risk_level='low',
        dependencies=[],  # Should depend on PostgreSQL optimization
        start_date=datetime(2024, 11, 2), end_date=datetime(2024, 11, 12)
    ))
    
    # ❌ ISSUE #3: Sarah Underutilized (only 3 SP)
    db.session.add(Task(
        project_id=project.id, sprint_id=sprint3.id,
        name='API Rate Limiting Implementation',
        title='API Rate Limiting Implementation',
        description='Implement Redis-based rate limiting for API endpoints',
        status='To Do', priority='medium', type='task',
        story_points=3, completed=False,
        labels=['backend', 'security'], complexity=5,
        pert_optimistic=6, pert_most_likely=12, pert_pessimistic=18, pert_expected=12,
        raci_responsible=[m['sarah']], raci_accountable=m['lisa'], raci_consulted=[], raci_informed=[m['sophie'], m['lisa']],
        required_skills=['Python', 'Redis', 'Rate Limiting'], 
        estimated_hours=12, actual_hours=0, risk_level='low',
        start_date=datetime(2024, 11, 2), end_date=datetime(2024, 11, 12)
    ))
    
    # Mike's task
    db.session.add(Task(
        project_id=project.id, sprint_id=sprint3.id,
        name='Prometheus Monitoring Setup',
        title='Prometheus Monitoring Setup',
        description='Setup Prometheus metrics collection and Grafana dashboards',
        status='In Progress', priority='high', type='task',
        story_points=8, completed=False,
        labels=['devops', 'monitoring'], complexity=6,
        pert_optimistic=16, pert_most_likely=32, pert_pessimistic=48, pert_expected=32,
        raci_responsible=[m['mike']], raci_accountable=m['lisa'], raci_consulted=[m['sarah']], raci_informed=[m['sophie'], m['lisa']],
        required_skills=['Prometheus', 'Grafana', 'Monitoring'], 
        estimated_hours=32, actual_hours=0, risk_level='medium',
        start_date=datetime(2024, 11, 2), end_date=datetime(2024, 11, 12)
    ))
    
    # Sophie's task
    db.session.add(Task(
        project_id=project.id, sprint_id=sprint3.id,
        name='Product Page Redesign',
        title='Product Page Redesign',
        description='New product page design with improved UX',
        status='Done', priority='medium', type='feature',
        story_points=5, completed=True,
        labels=['design', 'ui'], complexity=5,
        pert_optimistic=10, pert_most_likely=20, pert_pessimistic=30, pert_expected=20,
        raci_responsible=[m['sophie']], raci_accountable=m['lisa'], raci_consulted=[m['sarah']], raci_informed=[m['sophie'], m['lisa']],
        required_skills=['Figma', 'UI Design'], 
        estimated_hours=20, actual_hours=18, risk_level='low',
        start_date=datetime(2024, 11, 2), end_date=datetime(2024, 11, 12)
    ))
    
    # ❌ ISSUE #4: Merge Opportunity (4 tiny tasks - should be merged)
    for i, name in enumerate(['Fix button typo', 'Update primary color', 'Add hover tooltip', 'Change heading font'], 1):
        db.session.add(Task(
            project_id=project.id, sprint_id=sprint3.id,
            name=name, title=name,
            description=f'Small UI fix #{i}',
            status='To Do', priority='low', type='task',
            story_points=1, completed=False,
            labels=['ui', 'quick-fix', 'merge-candidate'], complexity=1,
            pert_optimistic=1, pert_most_likely=2, pert_pessimistic=3, pert_expected=2,
            raci_responsible=[m['john']], raci_accountable=m['lisa'], raci_consulted=[m['sarah']], raci_informed=[m['sophie'], m['lisa']],
            required_skills=['Vue.js', 'CSS'], 
            estimated_hours=2, actual_hours=0, risk_level='low',
        start_date=datetime(2024, 11, 2), end_date=datetime(2024, 11, 12)
    ))
    
    # Lisa's minimal task
    db.session.add(Task(
        project_id=project.id, sprint_id=sprint3.id,
        name='Sprint Retrospective Preparation',
        title='Sprint Retrospective Preparation',
        description='Prepare retrospective agenda and metrics',
        status='To Do', priority='low', type='task',
        story_points=1, completed=False,
        labels=['management'], complexity=2,
        pert_optimistic=1, pert_most_likely=2, pert_pessimistic=3, pert_expected=2,
        raci_responsible=[m['lisa']], raci_accountable=m['lisa'], raci_consulted=[m['sarah']], raci_informed=[m['sophie'], m['lisa']],
        required_skills=['Scrum', 'Agile'], 
        estimated_hours=2, actual_hours=0, risk_level='low',
        start_date=datetime(2024, 11, 2), end_date=datetime(2024, 11, 12)
    ))
    
    # BACKLOG TASKS (sprint_id=None)
    for name, sp, member, skills, labels in [
        ('Product Review & Rating System', 13, m['alex'], ['Python', 'Vue.js', 'PostgreSQL'], ['backlog', 'feature']),
        ('Advanced Search with Filters', 8, m['sarah'], ['PostgreSQL', 'ElasticSearch'], ['backlog', 'search']),
        ('Order Tracking System', 13, m['david'], ['Node.js', 'MongoDB', 'WebSocket'], ['backlog', 'orders']),
        ('Customer Support Live Chat', 21, m['alex'], ['WebSocket', 'Real-time', 'Vue.js'], ['backlog', 'support']),
        ('Admin Analytics Dashboard', 13, m['john'], ['Vue.js', 'Charts', 'Analytics'], ['backlog', 'admin']),
        ('Email Marketing Integration', 8, m['sarah'], ['Python', 'SendGrid', 'Email'], ['backlog', 'marketing']),
        ('Mobile App REST API', 21, m['david'], ['REST API', 'Mobile', 'Documentation'], ['backlog', 'mobile']),
        ('Performance Optimization', 13, m['mike'], ['Performance', 'Caching', 'Redis'], ['backlog', 'optimization']),
        ('Multi-currency Support', 13, m['sarah'], ['Python', 'Currency', 'Localization'], ['backlog', 'i18n']),
        ('Inventory Management', 21, m['alex'], ['Python', 'PostgreSQL', 'Business Logic'], ['backlog', 'inventory'])
    ]:
        db.session.add(Task(
            project_id=project.id, sprint_id=None,  # BACKLOG!
            name=name, title=name,
            description=f'{name} - planned for future sprint',
            status='To Do', priority='medium', type='feature',
            story_points=sp, completed=False,
            labels=labels, complexity=7,
            pert_optimistic=sp*3, pert_most_likely=sp*5, pert_pessimistic=sp*7, pert_expected=sp*5,
            raci_responsible=[member], raci_accountable=m['lisa'], raci_consulted=[m['sarah']], raci_informed=[m['sophie'], m['lisa']],
            required_skills=skills, 
            estimated_hours=sp*5, actual_hours=0, risk_level='medium',
        start_date=datetime(2024, 11, 2), end_date=datetime(2024, 11, 12)
    ))
    
    # Project roles
    for member_key in ['lisa', 'john', 'sarah', 'mike', 'sophie']:
        role_type = 'owner' if member_key == 'lisa' else 'developer'
        db.session.add(ProjectRole(
            project_id=project.id, member_id=m[member_key], role=role_type,
            can_edit=True, can_delete=(role_type=='owner'),
            can_manage_team=(role_type=='owner'), can_manage_sprints=(role_type=='owner')
        ))
    
    # Update project statistics (total_tasks, completed_tasks, etc.)
    db.session.flush()
    update_project_stats(project)
    
    # Update project statistics
    db.session.flush()
    update_project_stats(project)
    db.session.commit()
    print("[OK] E-commerce Platform created (3 sprints, 10 backlog tasks, 7+ issues)")


# ====================================================================================
# PROJECT 2-8: Additional 7 projects with full implementations
# ====================================================================================

def seed_banking(m):
    """Project 2: Mobile Banking App - Dependency Chain Issues"""
    project = Project(
        name='Mobile Banking App',
        description='Secure mobile banking application with biometric authentication',
        template='Agile Development',
        icon='account_balance',
        status='In Progress',
        due_date=datetime(2026, 3, 1),
        team_member_ids=[m['emma'], m['alex'], m['chris'], m['rachel'], m['mark']],
        estimated_duration=90,
        max_story_points_per_person=20
    )
    db.session.add(project)
    db.session.flush()
    
    # Completed sprint
    sprint1 = Sprint(
        project_id=project.id, name='Sprint 1 - Auth Foundation',
        goal='Core authentication', start_date=datetime(2024, 7, 1), end_date=datetime(2024, 7, 14),
        status='completed', capacity=100, planned_story_points=38, velocity=38
    )
    db.session.add(sprint1)
    db.session.flush()
    
    for name, member, sp in [('Biometric Auth API', m['alex'], 13), ('Login UI', m['emma'], 13), ('AWS Setup', m['chris'], 12)]:
        task = Task(
            project_id=project.id, sprint_id=sprint1.id, name=name, title=name, description=name,
            status='Done', priority='high', type='feature', story_points=sp, completed=True,
            labels=['auth'], complexity=7, pert_optimistic=sp*3, pert_most_likely=sp*5, 
            pert_pessimistic=sp*7, pert_expected=sp*5,
            raci_responsible=[member], raci_accountable=m['mark'], raci_consulted=[m['sarah']], raci_informed=[m['sophie'], m['lisa']],
            required_skills=['Security'], estimated_hours=sp*5, actual_hours=sp*5, risk_level='high',
        start_date=datetime(2024, 11, 2), end_date=datetime(2024, 11, 12)
    )
        db.session.add(task)
        db.session.flush()
        db.session.add(create_task_history(task, member, sprint1.end_date))
    
    # Active sprint with dependency issues
    sprint2 = Sprint(
        project_id=project.id, name='Sprint 2 - Transactions',
        goal='Transaction system', start_date=datetime(2024, 11, 1), end_date=datetime(2024, 11, 14),
        status='active', capacity=100, planned_story_points=23, velocity=0
    )
    db.session.add(sprint2)
    db.session.flush()
    
    # ❌ Dependency bottleneck - 1 task blocks 3 others
    root_task = Task(
        project_id=project.id, sprint_id=sprint2.id,
        name='Transaction Core API', title='Transaction Core API',
        description='Core transaction processing logic - blocks other features',
        status='In Progress', priority='critical', type='feature',
        story_points=8, completed=False, labels=['backend', 'blocker'], complexity=9,
        pert_optimistic=16, pert_most_likely=32, pert_pessimistic=48, pert_expected=32,
        raci_responsible=[m['alex']], raci_accountable=m['mark'], raci_consulted=[m['sarah']], raci_informed=[m['sophie'], m['lisa']],
        required_skills=['Python', 'FastAPI', 'Banking'], estimated_hours=32, actual_hours=0, risk_level='critical',
        start_date=datetime(2024, 11, 2), end_date=datetime(2024, 11, 12)
    )
    db.session.add(root_task)
    db.session.flush()
    root_id = root_task.id
    
    # Blocked tasks
    for name, member, sp in [
        ('Transaction History UI', m['emma'], 5),
        ('Transaction Notifications', m['alex'], 3),
        ('Transaction Reports', m['alex'], 7)
    ]:
        db.session.add(Task(
            project_id=project.id, sprint_id=sprint2.id,
            name=name, title=name, description=f'{name} - blocked by Transaction Core API',
            status='Blocked', priority='high', type='feature',
            story_points=sp, completed=False, labels=['blocked'], complexity=6,
            pert_optimistic=sp*3, pert_most_likely=sp*5, pert_pessimistic=sp*7, pert_expected=sp*5,
            raci_responsible=[member], raci_accountable=m['mark'], raci_consulted=[m['sarah']], raci_informed=[m['sophie'], m['lisa']],
            required_skills=['Vue.js' if 'UI' in name else 'Python'],
            estimated_hours=sp*5, actual_hours=0, risk_level='high',
            dependencies=[root_id]  # Blocked by root task
        ))
    
    # Other tasks
    for name, member, sp in [('Security Audit', m['chris'], 7), ('Push Notifications Design', m['rachel'], 3)]:
        db.session.add(Task(
            project_id=project.id, sprint_id=sprint2.id,
            name=name, title=name, description=name, status='To Do', priority='medium', type='task',
            story_points=sp, completed=False, labels=['feature'], complexity=5,
            pert_optimistic=sp*3, pert_most_likely=sp*5, pert_pessimistic=sp*7, pert_expected=sp*5,
            raci_responsible=[member], raci_accountable=m['mark'], raci_consulted=[m['sarah']], raci_informed=[m['sophie'], m['lisa']],
            required_skills=['Security' if 'Security' in name else 'Figma'],
            estimated_hours=sp*5, actual_hours=0, risk_level='medium',
        start_date=datetime(2024, 11, 2), end_date=datetime(2024, 11, 12)
    ))
    
    # Backlog
    for name, sp, member in [
        ('Bill Payment Feature', 21, m['alex']),
        ('Account Statements', 13, m['emma']),
        ('Budgeting Tools', 13, m['alex']),
        ('ATM Locator', 8, m['emma']),
        ('Currency Exchange', 13, m['alex']),
        ('Investment Portfolio', 21, m['alex'])
    ]:
        db.session.add(Task(
            project_id=project.id, sprint_id=None, name=name, title=name, description=name,
            status='To Do', priority='medium', type='feature', story_points=sp, completed=False,
            labels=['backlog'], complexity=7, pert_optimistic=sp*3, pert_most_likely=sp*5,
            pert_pessimistic=sp*7, pert_expected=sp*5,
            raci_responsible=[member], raci_accountable=m['mark'], raci_consulted=[m['sarah']], raci_informed=[m['sophie'], m['lisa']],
            required_skills=['Python', 'Vue.js'], estimated_hours=sp*5, actual_hours=0, risk_level='medium',
        start_date=datetime(2024, 11, 2), end_date=datetime(2024, 11, 12)
    ))
    
    for member_key in ['mark', 'emma', 'alex', 'chris', 'rachel']:
        db.session.add(ProjectRole(
            project_id=project.id, member_id=m[member_key], role='owner' if member_key=='mark' else 'developer',
            can_edit=True, can_delete=(member_key=='mark'),
            can_manage_team=(member_key=='mark'), can_manage_sprints=(member_key=='mark')
        ))
    
    # Update project statistics
    db.session.flush()
    update_project_stats(project)
    db.session.commit()
    print("[OK] Mobile Banking App created (dependency chain issues)")


def seed_healthcare(m):
    """Project 3: Healthcare Portal - Giant Task in Backlog"""
    project = Project(
        name='Healthcare Patient Portal',
        description='Telemedicine platform with appointment scheduling',
        template='Agile Development',
        icon='local_hospital',
        status='In Progress',
        due_date=datetime(2026, 2, 15),
        team_member_ids=[m['tom'], m['david'], m['mike'], m['sophie'], m['lisa']],
        estimated_duration=100,
        max_story_points_per_person=20
    )
    db.session.add(project)
    db.session.flush()
    
    # Completed sprint
    sprint1 = Sprint(
        project_id=project.id, name='Sprint 1 - Patient Records',
        goal='Patient data management', start_date=datetime(2024, 8, 1), end_date=datetime(2024, 8, 14),
        status='completed', capacity=100, planned_story_points=40, velocity=40
    )
    db.session.add(sprint1)
    db.session.flush()
    
    for name, member, sp in [('Patient Database', m['david'], 13), ('HIPAA Compliance', m['mike'], 13), ('Patient UI', m['tom'], 14)]:
        task = Task(
            project_id=project.id, sprint_id=sprint1.id, name=name, title=name, description=name,
            status='Done', priority='critical', type='feature', story_points=sp, completed=True,
            labels=['foundation'], complexity=8, pert_optimistic=sp*3, pert_most_likely=sp*5,
            pert_pessimistic=sp*7, pert_expected=sp*5,
            raci_responsible=[member], raci_accountable=m['lisa'], raci_consulted=[m['sarah']], raci_informed=[m['sophie'], m['lisa']],
            required_skills=['Security', 'Healthcare'], estimated_hours=sp*5, actual_hours=sp*5, risk_level='critical',
        start_date=datetime(2024, 11, 2), end_date=datetime(2024, 11, 12)
    )
        db.session.add(task)
        db.session.flush()
        db.session.add(create_task_history(task, member, sprint1.end_date))
    
    # Active sprint
    sprint2 = Sprint(
        project_id=project.id, name='Sprint 2 - Appointments',
        goal='Scheduling system', start_date=datetime(2024, 11, 1), end_date=datetime(2024, 11, 14),
        status='active', capacity=100, planned_story_points=27, velocity=0
    )
    db.session.add(sprint2)
    db.session.flush()
    
    # Store appointment API task ID for dependencies
    appointment_api = Task(
        project_id=project.id, sprint_id=sprint2.id,
        name='Appointment Booking API', title='Appointment Booking API',
        description='Appointment Booking API', status='In Progress', priority='high', type='feature',
        story_points=8, completed=False, labels=['appointments'], complexity=6,
        pert_optimistic=24, pert_most_likely=40, pert_pessimistic=56, pert_expected=40,
        raci_responsible=[m['david']], raci_accountable=m['lisa'], raci_consulted=[m['sarah']], raci_informed=[m['sophie'], m['lisa']],
        required_skills=['Node.js'], estimated_hours=40, actual_hours=0, risk_level='medium',
        start_date=datetime(2024, 11, 2), end_date=datetime(2024, 11, 12)
    )
    db.session.add(appointment_api)
    db.session.flush()
    api_id = appointment_api.id
    
    # Other tasks - Email Reminders depends on API
    for name, member, sp, status, deps in [
        ('Calendar Integration', m['tom'], 7, 'To Do', None),
        ('Doctor Dashboard', m['tom'], 7, 'To Do', None),
        ('Email Reminders', m['david'], 5, 'To Do', [api_id]),  # ✅ Depends on Appointment API
        ('Appointment History UI', m['sophie'], 5, 'Done', None)
    ]:
        task = Task(
            project_id=project.id, sprint_id=sprint2.id,
            name=name, title=name, description=name, status=status, priority='high', type='feature',
            story_points=sp, completed=(status=='Done'), labels=['appointments'], complexity=6,
            pert_optimistic=sp*3, pert_most_likely=sp*5, pert_pessimistic=sp*7, pert_expected=sp*5,
            raci_responsible=[member], raci_accountable=m['lisa'], raci_consulted=[m['sarah']], raci_informed=[m['sophie'], m['lisa']],
            required_skills=['Node.js' if member==m['david'] else 'Vue.js'],
            estimated_hours=sp*5, actual_hours=0 if status!='Done' else sp*5, risk_level='medium',
            start_date=datetime(2024, 11, 2), end_date=datetime(2024, 11, 12),
            dependencies=deps
        )
        db.session.add(task)
    
    # Mike and Lisa tasks
    for name, member, sp in [('Kubernetes Scale-up', m['mike'], 5), ('Stakeholder Meeting Prep', m['lisa'], 2)]:
        db.session.add(Task(
            project_id=project.id, sprint_id=sprint2.id,
            name=name, title=name, description=name, status='To Do', priority='medium', type='task',
            story_points=sp, completed=False, labels=['infrastructure' if 'Kubernetes' in name else 'management'], complexity=4,
            pert_optimistic=sp*3, pert_most_likely=sp*5, pert_pessimistic=sp*7, pert_expected=sp*5,
            raci_responsible=[member], raci_accountable=m['lisa'], raci_consulted=[m['sarah']], raci_informed=[m['sophie'], m['lisa']],
            required_skills=['Kubernetes' if 'Kubernetes' in name else 'Scrum'],
            estimated_hours=sp*5, actual_hours=0, risk_level='low',
        start_date=datetime(2024, 11, 2), end_date=datetime(2024, 11, 12)
    ))
    
    # ❌ GIANT TASK IN BACKLOG (55 SP!)
    db.session.add(Task(
        project_id=project.id, sprint_id=None,
        name='Complete Telemedicine Video Consultation Platform',
        title='Complete Telemedicine Video Consultation Platform',
        description='Full video consultation with WebRTC, recording, chat, screen sharing, prescriptions',
        status='To Do', priority='high', type='feature',
        story_points=55, completed=False, labels=['backlog', 'giant-task', 'telemedicine'], complexity=10,
        pert_optimistic=120, pert_most_likely=200, pert_pessimistic=280, pert_expected=200,
        raci_responsible=[m['david']], raci_accountable=m['lisa'], raci_consulted=[m['sarah']], raci_informed=[m['sophie'], m['lisa']],
        required_skills=['WebRTC', 'Video', 'Real-time', 'Healthcare'],
        estimated_hours=200, actual_hours=0, risk_level='critical',
        start_date=datetime(2024, 11, 2), end_date=datetime(2024, 11, 12)
    ))
    
    # Other backlog
    for name, sp, member in [
        ('Lab Results Integration', 13, m['david']),
        ('Prescription Management', 13, m['tom']),
        ('Medical History Timeline', 8, m['tom']),
        ('Insurance Verification', 13, m['david']),
        ('Billing System', 21, m['david'])
    ]:
        db.session.add(Task(
            project_id=project.id, sprint_id=None, name=name, title=name, description=name,
            status='To Do', priority='medium', type='feature', story_points=sp, completed=False,
            labels=['backlog'], complexity=7, pert_optimistic=sp*3, pert_most_likely=sp*5,
            pert_pessimistic=sp*7, pert_expected=sp*5,
            raci_responsible=[member], raci_accountable=m['lisa'], raci_consulted=[m['sarah']], raci_informed=[m['sophie'], m['lisa']],
            required_skills=['Healthcare', 'HIPAA'], estimated_hours=sp*5, actual_hours=0, risk_level='medium',
        start_date=datetime(2024, 11, 2), end_date=datetime(2024, 11, 12)
    ))
    
    for member_key in ['lisa', 'tom', 'david', 'mike', 'sophie']:
        db.session.add(ProjectRole(
            project_id=project.id, member_id=m[member_key], role='owner' if member_key=='lisa' else 'developer',
            can_edit=True, can_delete=(member_key=='lisa'),
            can_manage_team=(member_key=='lisa'), can_manage_sprints=(member_key=='lisa')
        ))
    
    # Update project statistics
    db.session.flush()
    update_project_stats(project)
    db.session.commit()
    print("[OK] Healthcare Portal created (giant 55 SP task in backlog)")


def seed_logistics(m):
    """Project 4: Logistics Dashboard - Bad PERT Estimates"""
    project = Project(
        name='Logistics Tracking Dashboard',
        description='Real-time shipment tracking and route optimization',
        template='Agile Development',
        icon='local_shipping',
        status='In Progress',
        due_date=datetime(2025, 12, 31),
        team_member_ids=[m['john'], m['sarah'], m['chris'], m['rachel'], m['mark']],
        estimated_duration=80,
        max_story_points_per_person=20
    )
    db.session.add(project)
    db.session.flush()
    
    sprint1 = Sprint(
        project_id=project.id, name='Sprint 1 - Tracking Core',
        goal='GPS tracking', start_date=datetime(2024, 9, 1), end_date=datetime(2024, 9, 14),
        status='completed', capacity=100, planned_story_points=35, velocity=35
    )
    db.session.add(sprint1)
    db.session.flush()
    
    for name, member, sp in [('GPS Integration', m['sarah'], 13), ('Map Display', m['john'], 13), ('AWS IoT', m['chris'], 9)]:
        task = Task(
            project_id=project.id, sprint_id=sprint1.id, name=name, title=name, description=name,
            status='Done', priority='high', type='feature', story_points=sp, completed=True,
            labels=['tracking'], complexity=7, pert_optimistic=sp*3, pert_most_likely=sp*5,
            pert_pessimistic=sp*7, pert_expected=sp*5,
            raci_responsible=[member], raci_accountable=m['mark'], raci_consulted=[m['sarah']], raci_informed=[m['sophie'], m['lisa']],
            required_skills=['GPS', 'Maps'], estimated_hours=sp*5, actual_hours=sp*5, risk_level='medium',
        start_date=datetime(2024, 11, 2), end_date=datetime(2024, 11, 12)
    )
        db.session.add(task)
        db.session.flush()
        db.session.add(create_task_history(task, member, sprint1.end_date))
    
    # Active sprint with BAD PERT estimates
    sprint2 = Sprint(
        project_id=project.id, name='Sprint 2 - Route Optimization',
        goal='AI route planning', start_date=datetime(2024, 11, 1), end_date=datetime(2024, 11, 14),
        status='active', capacity=100, planned_story_points=28, velocity=0
    )
    db.session.add(sprint2)
    db.session.flush()
    
    # ❌ BAD PERT ESTIMATES (optimistic way too high!)
    for name, member, sp, opt, ml, pes in [
        ('Route Optimization Algorithm', m['sarah'], 13, 50, 65, 80),  # optimistic too high!
        ('Driver Mobile App', m['john'], 8, 30, 40, 50),  # should be 24, 40, 56
        ('Warehouse Management', m['sarah'], 5, 20, 25, 30),  # optimistic should be 15
        ('Real-time Alerts', m['chris'], 8, 32, 40, 48),  # This one is correct
        ('Dashboard Analytics', m['john'], 7, 28, 35, 42),  # Optimistic too high
        ('Delivery Proof Upload', m['rachel'], 5, 15, 25, 35),  # Correct
        ('Sprint Planning', m['mark'], 3, 9, 15, 21)  # Correct
    ]:
        db.session.add(Task(
            project_id=project.id, sprint_id=sprint2.id,
            name=name, title=name, description=name, status='To Do', priority='high', type='feature',
            story_points=sp, completed=False, labels=['optimization'], complexity=7,
            pert_optimistic=opt, pert_most_likely=ml, pert_pessimistic=pes, pert_expected=ml,
            raci_responsible=[member], raci_accountable=m['mark'], raci_consulted=[m['sarah']], raci_informed=[m['sophie'], m['lisa']],
            required_skills=['AI' if 'Algorithm' in name else 'Software'],
            estimated_hours=ml, actual_hours=0, risk_level='high' if sp > 10 else 'medium'
        ))
    
    # Backlog
    for name, sp in [
        ('Customer Portal', 13),
        ('Invoice Generation', 8),
        ('Fleet Management', 21),
        ('Fuel Optimization', 13),
        ('Driver Performance', 8)
    ]:
        db.session.add(Task(
            project_id=project.id, sprint_id=None, name=name, title=name, description=name,
            status='To Do', priority='medium', type='feature', story_points=sp, completed=False,
            labels=['backlog'], complexity=6, pert_optimistic=sp*3, pert_most_likely=sp*5,
            pert_pessimistic=sp*7, pert_expected=sp*5,
            raci_responsible=[m['sarah']], raci_accountable=m['mark'], raci_consulted=[], raci_informed=[m['sophie'], m['lisa']],
            required_skills=['Logistics'], estimated_hours=sp*5, actual_hours=0, risk_level='medium',
        start_date=datetime(2024, 11, 2), end_date=datetime(2024, 11, 12)
    ))
    
    for member_key in ['mark', 'john', 'sarah', 'chris', 'rachel']:
        db.session.add(ProjectRole(
            project_id=project.id, member_id=m[member_key], role='owner' if member_key=='mark' else 'developer',
            can_edit=True, can_delete=(member_key=='mark'),
            can_manage_team=(member_key=='mark'), can_manage_sprints=(member_key=='mark')
        ))
    
    # Update project statistics
    db.session.flush()
    update_project_stats(project)
    db.session.commit()
    print("[OK] Logistics Dashboard created (bad PERT estimates)")


def seed_social_media(m):
    """Project 5: Social Media - Under-capacity Sprint"""
    project = Project(
        name='Social Media Platform',
        description='Next-gen social networking with AR filters',
        template='Agile Development',
        icon='people',
        status='In Progress',
        due_date=datetime(2026, 6, 1),
        team_member_ids=[m['emma'], m['alex'], m['mike'], m['sophie'], m['lisa']],
        estimated_duration=150,
        max_story_points_per_person=20
    )
    db.session.add(project)
    db.session.flush()
    
    sprint1 = Sprint(
        project_id=project.id, name='Sprint 1 - Social Core',
        goal='Posts and feeds', start_date=datetime(2024, 9, 15), end_date=datetime(2024, 9, 29),
        status='completed', capacity=100, planned_story_points=45, velocity=45
    )
    db.session.add(sprint1)
    db.session.flush()
    
    for name, member, sp in [('News Feed Algorithm', m['alex'], 13), ('Post Creation UI', m['emma'], 13), ('Image CDN', m['mike'], 13), ('Feed Design', m['sophie'], 6)]:
        task = Task(
            project_id=project.id, sprint_id=sprint1.id, name=name, title=name, description=name,
            status='Done', priority='high', type='feature', story_points=sp, completed=True,
            labels=['social'], complexity=7, pert_optimistic=sp*3, pert_most_likely=sp*5,
            pert_pessimistic=sp*7, pert_expected=sp*5,
            raci_responsible=[member], raci_accountable=m['lisa'], raci_consulted=[m['sarah']], raci_informed=[m['sophie'], m['lisa']],
            required_skills=['Social Media'], estimated_hours=sp*5, actual_hours=sp*5, risk_level='medium',
        start_date=datetime(2024, 11, 2), end_date=datetime(2024, 11, 12)
    )
        db.session.add(task)
        db.session.flush()
        db.session.add(create_task_history(task, member, sprint1.end_date))
    
    # ❌ UNDER-CAPACITY SPRINT (only 13 SP planned out of 100!)
    sprint2 = Sprint(
        project_id=project.id, name='Sprint 2 - Messaging',
        goal='Direct messaging', start_date=datetime(2024, 11, 1), end_date=datetime(2024, 11, 14),
        status='active', capacity=100, planned_story_points=13, velocity=0  # Very low!
    )
    db.session.add(sprint2)
    db.session.flush()
    
    # Only a few small tasks
    for name, member, sp in [
        ('Basic Chat UI', m['emma'], 5),
        ('Message API Endpoint', m['alex'], 3),
        ('Chat Icon Design', m['sophie'], 2),
        ('Sprint Review Prep', m['lisa'], 3)
    ]:
        db.session.add(Task(
            project_id=project.id, sprint_id=sprint2.id,
            name=name, title=name, description=name, status='To Do', priority='medium', type='task',
            story_points=sp, completed=False, labels=['messaging', 'under-capacity'], complexity=4,
            pert_optimistic=sp*3, pert_most_likely=sp*5, pert_pessimistic=sp*7, pert_expected=sp*5,
            raci_responsible=[member], raci_accountable=m['lisa'], raci_consulted=[m['sarah']], raci_informed=[m['sophie'], m['lisa']],
            required_skills=['Chat' if 'Chat' in name else 'Messaging'],
            estimated_hours=sp*5, actual_hours=0, risk_level='low',
        start_date=datetime(2024, 11, 2), end_date=datetime(2024, 11, 12)
    ))
    
    # Large backlog (could pull tasks from here!)
    for name, sp, member in [
        ('AR Filters Integration', 21, m['emma']),
        ('Video Stories', 21, m['alex']),
        ('Group Chats', 13, m['alex']),
        ('Live Streaming', 34, m['alex']),
        ('Hashtag System', 8, m['alex']),
        ('Trending Topics', 13, m['alex']),
        ('Profile Customization', 8, m['emma']),
        ('Privacy Settings', 13, m['alex']),
        ('Content Moderation AI', 21, m['alex']),
        ('Analytics Dashboard', 13, m['emma'])
    ]:
        db.session.add(Task(
            project_id=project.id, sprint_id=None, name=name, title=name, description=name,
            status='To Do', priority='high' if sp > 15 else 'medium', type='feature',
            story_points=sp, completed=False, labels=['backlog', 'high-value'], complexity=8,
            pert_optimistic=sp*3, pert_most_likely=sp*5, pert_pessimistic=sp*7, pert_expected=sp*5,
            raci_responsible=[member], raci_accountable=m['lisa'], raci_consulted=[m['sarah']], raci_informed=[m['sophie'], m['lisa']],
            required_skills=['Social Media', 'AR' if 'AR' in name else 'Video' if 'Video' in name else 'Python'],
            estimated_hours=sp*5, actual_hours=0, risk_level='high' if sp > 20 else 'medium'
        ))
    
    for member_key in ['lisa', 'emma', 'alex', 'mike', 'sophie']:
        db.session.add(ProjectRole(
            project_id=project.id, member_id=m[member_key], role='owner' if member_key=='lisa' else 'developer',
            can_edit=True, can_delete=(member_key=='lisa'),
            can_manage_team=(member_key=='lisa'), can_manage_sprints=(member_key=='lisa')
        ))
    
    # Update project statistics
    db.session.flush()
    update_project_stats(project)
    db.session.commit()
    print("[OK] Social Media Platform created (under-capacity sprint: 13/100 SP)")


def seed_ai_generator(m):
    """Project 6: AI Content Generator - Skill Mismatches"""
    project = Project(
        name='AI Content Generator',
        description='GPT-powered content creation platform',
        template='Agile Development',
        icon='auto_awesome',
        status='In Progress',
        due_date=datetime(2026, 4, 15),
        team_member_ids=[m['tom'], m['david'], m['chris'], m['rachel'], m['mark']],
        estimated_duration=110,
        max_story_points_per_person=20
    )
    db.session.add(project)
    db.session.flush()
    
    sprint1 = Sprint(
        project_id=project.id, name='Sprint 1 - AI Integration',
        goal='OpenAI setup', start_date=datetime(2024, 10, 1), end_date=datetime(2024, 10, 14),
        status='completed', capacity=100, planned_story_points=38, velocity=38
    )
    db.session.add(sprint1)
    db.session.flush()
    
    for name, member, sp in [('OpenAI API Integration', m['david'], 13), ('Content Editor UI', m['tom'], 13), ('AWS Lambda Deploy', m['chris'], 12)]:
        task = Task(
            project_id=project.id, sprint_id=sprint1.id, name=name, title=name, description=name,
            status='Done', priority='high', type='feature', story_points=sp, completed=True,
            labels=['ai'], complexity=8, pert_optimistic=sp*3, pert_most_likely=sp*5,
            pert_pessimistic=sp*7, pert_expected=sp*5,
            raci_responsible=[member], raci_accountable=m['mark'], raci_consulted=[m['sarah']], raci_informed=[m['sophie'], m['lisa']],
            required_skills=['AI', 'GPT'], estimated_hours=sp*5, actual_hours=sp*5, risk_level='high',
        start_date=datetime(2024, 11, 2), end_date=datetime(2024, 11, 12)
    )
        db.session.add(task)
        db.session.flush()
        db.session.add(create_task_history(task, member, sprint1.end_date))
    
    # Active sprint with SKILL MISMATCHES
    sprint2 = Sprint(
        project_id=project.id, name='Sprint 2 - Content Types',
        goal='Multiple content formats', start_date=datetime(2024, 11, 1), end_date=datetime(2024, 11, 14),
        status='active', capacity=100, planned_story_points=31, velocity=0
    )
    db.session.add(sprint2)
    db.session.flush()
    
    # ❌ SKILL MISMATCHES
    for name, member, sp, required_skills, labels in [
        # Kubernetes task assigned to Frontend dev!
        ('Kubernetes Auto-scaling Setup', m['tom'], 8, ['Kubernetes', 'DevOps', 'Infrastructure'], ['skill-mismatch', 'devops']),
        # ML model task assigned to Designer!
        ('Fine-tune GPT Model', m['rachel'], 13, ['Machine Learning', 'Python', 'AI'], ['skill-mismatch', 'ai']),
        # Legit tasks
        ('Blog Post Generator', m['david'], 8, ['Node.js', 'GPT'], ['feature']),
        ('Social Media Post Generator', m['tom'], 5, ['Vue.js', 'JavaScript'], ['feature']),
        ('Content Templates', m['rachel'], 8, ['Figma', 'UI Design'], ['design']),
        # More skill mismatches
        ('MongoDB Sharding', m['rachel'], 5, ['MongoDB', 'Database'], ['skill-mismatch', 'database']),
        ('Load Testing', m['chris'], 5, ['Performance', 'Testing'], ['testing'])
    ]:
        db.session.add(Task(
            project_id=project.id, sprint_id=sprint2.id,
            name=name, title=name, description=name, status='To Do', priority='high', type='feature',
            story_points=sp, completed=False, labels=labels, complexity=7,
            pert_optimistic=sp*3, pert_most_likely=sp*5, pert_pessimistic=sp*7, pert_expected=sp*5,
            raci_responsible=[member], raci_accountable=m['mark'], raci_consulted=[m['sarah']], raci_informed=[m['sophie'], m['lisa']],
            required_skills=required_skills, estimated_hours=sp*5, actual_hours=0,
            risk_level='high' if 'skill-mismatch' in labels else 'medium'
        ))
    
    # Backlog
    for name, sp in [
        ('Video Script Generator', 21),
        ('SEO Optimization', 13),
        ('Multi-language Support', 13),
        ('Content Calendar', 8),
        ('Plagiarism Checker', 13),
        ('Image Generation', 21)
    ]:
        db.session.add(Task(
            project_id=project.id, sprint_id=None, name=name, title=name, description=name,
            status='To Do', priority='medium', type='feature', story_points=sp, completed=False,
            labels=['backlog'], complexity=7, pert_optimistic=sp*3, pert_most_likely=sp*5,
            pert_pessimistic=sp*7, pert_expected=sp*5,
            raci_responsible=[m['david']], raci_accountable=m['mark'], raci_consulted=[m['sarah']], raci_informed=[m['sophie'], m['lisa']],
            required_skills=['AI', 'GPT'], estimated_hours=sp*5, actual_hours=0, risk_level='medium',
        start_date=datetime(2024, 11, 2), end_date=datetime(2024, 11, 12)
    ))
    
    for member_key in ['mark', 'tom', 'david', 'chris', 'rachel']:
        db.session.add(ProjectRole(
            project_id=project.id, member_id=m[member_key], role='owner' if member_key=='mark' else 'developer',
            can_edit=True, can_delete=(member_key=='mark'),
            can_manage_team=(member_key=='mark'), can_manage_sprints=(member_key=='mark')
        ))
    
    # Update project statistics
    db.session.flush()
    update_project_stats(project)
    db.session.commit()
    print("[OK] AI Content Generator created (3+ skill mismatches)")


def seed_iot(m):
    """Project 7: IoT Device Manager - Deadline Panic"""
    project = Project(
        name='IoT Device Manager',
        description='Smart home device management platform',
        template='Agile Development',
        icon='devices',
        status='In Progress',
        due_date=datetime(2025, 11, 30),
        team_member_ids=[m['john'], m['emma'], m['david'], m['sophie'], m['mark']],
        estimated_duration=85,
        max_story_points_per_person=20
    )
    db.session.add(project)
    db.session.flush()
    
    sprint1 = Sprint(
        project_id=project.id, name='Sprint 1 - Device Registration',
        goal='Device onboarding', start_date=datetime(2024, 10, 1), end_date=datetime(2024, 10, 14),
        status='completed', capacity=100, planned_story_points=42, velocity=42
    )
    db.session.add(sprint1)
    db.session.flush()
    
    for name, member, sp in [('Device API', m['david'], 13), ('Registration UI', m['john'], 13), ('Device Icons', m['sophie'], 8), ('Pairing Flow UI', m['emma'], 8)]:
        task = Task(
            project_id=project.id, sprint_id=sprint1.id, name=name, title=name, description=name,
            status='Done', priority='high', type='feature', story_points=sp, completed=True,
            labels=['devices'], complexity=7, pert_optimistic=sp*3, pert_most_likely=sp*5,
            pert_pessimistic=sp*7, pert_expected=sp*5,
            raci_responsible=[member], raci_accountable=m['mark'], raci_consulted=[m['sarah']], raci_informed=[m['sophie'], m['lisa']],
            required_skills=['IoT'], estimated_hours=sp*5, actual_hours=sp*5, risk_level='medium',
        start_date=datetime(2024, 11, 2), end_date=datetime(2024, 11, 12)
    )
        db.session.add(task)
        db.session.flush()
        db.session.add(create_task_history(task, member, sprint1.end_date))
    
    # Active sprint with DEADLINE PANIC
    sprint2 = Sprint(
        project_id=project.id, name='Sprint 2 - Automation',
        goal='Smart automation rules', start_date=datetime(2024, 11, 1), end_date=datetime(2024, 11, 14),
        status='active', capacity=100, planned_story_points=27, velocity=0
    )
    db.session.add(sprint2)
    db.session.flush()
    
    # ❌ DEADLINE PANIC - Critical task due in 2 days!
    db.session.add(Task(
        project_id=project.id, sprint_id=sprint2.id,
        name='Critical Security Patch for Device Auth',
        title='Critical Security Patch for Device Auth',
        description='Emergency security fix required by Nov 10 due to vulnerability disclosure',
        status='To Do', priority='critical', type='bug',
        story_points=13, completed=False, labels=['security', 'critical', 'deadline-panic'], complexity=9,
        pert_optimistic=24, pert_most_likely=40, pert_pessimistic=56, pert_expected=40,
        raci_responsible=[m['david']], raci_accountable=m['mark'], raci_consulted=[m['sarah']], raci_informed=[m['sophie'], m['lisa']],
        required_skills=['Security', 'IoT', 'Cryptography'],
        estimated_hours=40, actual_hours=0, risk_level='critical',
        due_date=datetime(2024, 11, 10)  # 2 days away!
    ))
    
    # Other tasks
    for name, member, sp in [
        ('Automation Rules Engine', m['david'], 8),
        ('Rule Builder UI', m['john'], 5),
        ('Device Groups', m['emma'], 8),
        ('Dashboard Widgets', m['sophie'], 3),
        ('Project Documentation', m['mark'], 3)
    ]:
        db.session.add(Task(
            project_id=project.id, sprint_id=sprint2.id,
            name=name, title=name, description=name, status='To Do', priority='medium', type='feature',
            story_points=sp, completed=False, labels=['automation'], complexity=6,
            pert_optimistic=sp*3, pert_most_likely=sp*5, pert_pessimistic=sp*7, pert_expected=sp*5,
            raci_responsible=[member], raci_accountable=m['mark'], raci_consulted=[m['sarah']], raci_informed=[m['sophie'], m['lisa']],
            required_skills=['IoT'], estimated_hours=sp*5, actual_hours=0, risk_level='medium',
        start_date=datetime(2024, 11, 2), end_date=datetime(2024, 11, 12)
    ))
    
    # Backlog
    for name, sp in [
        ('Voice Control Integration', 21),
        ('Energy Monitoring', 13),
        ('Scene Management', 13),
        ('Mobile App', 34),
        ('Device Firmware Updates', 13),
        ('Usage Analytics', 13)
    ]:
        db.session.add(Task(
            project_id=project.id, sprint_id=None, name=name, title=name, description=name,
            status='To Do', priority='medium', type='feature', story_points=sp, completed=False,
            labels=['backlog'], complexity=7, pert_optimistic=sp*3, pert_most_likely=sp*5,
            pert_pessimistic=sp*7, pert_expected=sp*5,
            raci_responsible=[m['david']], raci_accountable=m['mark'], raci_consulted=[m['sarah']], raci_informed=[m['sophie'], m['lisa']],
            required_skills=['IoT', 'Smart Home'], estimated_hours=sp*5, actual_hours=0, risk_level='medium',
        start_date=datetime(2024, 11, 2), end_date=datetime(2024, 11, 12)
    ))
    
    for member_key in ['mark', 'john', 'emma', 'david', 'sophie']:
        db.session.add(ProjectRole(
            project_id=project.id, member_id=m[member_key], role='owner' if member_key=='mark' else 'developer',
            can_edit=True, can_delete=(member_key=='mark'),
            can_manage_team=(member_key=='mark'), can_manage_sprints=(member_key=='mark')
        ))
    
    # Update project statistics
    db.session.flush()
    update_project_stats(project)
    db.session.commit()
    print("[OK] IoT Device Manager created (deadline panic: critical task due in 2 days)")


def seed_education(m):
    """Project 8: Education LMS - Priority Conflicts & Rachel Overload"""
    project = Project(
        name='Education Learning Management System',
        description='Online learning platform with live classes',
        template='Agile Development',
        icon='school',
        status='In Progress',
        due_date=datetime(2026, 5, 1),
        team_member_ids=[m['tom'], m['sarah'], m['alex'], m['mike'], m['rachel']],
        estimated_duration=130,
        max_story_points_per_person=20
    )
    db.session.add(project)
    db.session.flush()
    
    sprint1 = Sprint(
        project_id=project.id, name='Sprint 1 - Course Management',
        goal='Course CRUD', start_date=datetime(2024, 10, 15), end_date=datetime(2024, 10, 29),
        status='completed', capacity=100, planned_story_points=48, velocity=48
    )
    db.session.add(sprint1)
    db.session.flush()
    
    for name, member, sp in [('Course API', m['sarah'], 13), ('Course Builder UI', m['tom'], 13), ('Video Upload', m['mike'], 13), ('Course Cards Design', m['rachel'], 9)]:
        task = Task(
            project_id=project.id, sprint_id=sprint1.id, name=name, title=name, description=name,
            status='Done', priority='high', type='feature', story_points=sp, completed=True,
            labels=['courses'], complexity=7, pert_optimistic=sp*3, pert_most_likely=sp*5,
            pert_pessimistic=sp*7, pert_expected=sp*5,
            raci_responsible=[member], raci_accountable=m['lisa'], raci_consulted=[m['sarah']], raci_informed=[m['sophie'], m['lisa']],
            required_skills=['Education'], estimated_hours=sp*5, actual_hours=sp*5, risk_level='medium',
        start_date=datetime(2024, 11, 2), end_date=datetime(2024, 11, 12)
    )
        db.session.add(task)
        db.session.flush()
        db.session.add(create_task_history(task, member, sprint1.end_date))
    
    # Active sprint with PRIORITY CONFLICTS and RACHEL OVERLOAD
    sprint2 = Sprint(
        project_id=project.id, name='Sprint 2 - Student Features',
        goal='Student dashboard', start_date=datetime(2024, 11, 1), end_date=datetime(2024, 11, 14),
        status='active', capacity=100, planned_story_points=25, velocity=0
    )
    db.session.add(sprint2)
    db.session.flush()
    
    # ❌ PRIORITY CONFLICTS - 3 high-priority tasks in progress simultaneously
    for name, member, sp, status in [
        ('Student Dashboard API', m['sarah'], 8, 'In Progress'),  # High priority, in progress
        ('Live Class Integration', m['alex'], 5, 'In Progress'),  # High priority, in progress
        ('Assignment Grading System', m['sarah'], 8, 'In Progress')  # High priority, in progress
    ]:
        db.session.add(Task(
            project_id=project.id, sprint_id=sprint2.id,
            name=name, title=name, description=name, status=status, priority='high', type='feature',
            story_points=sp, completed=False, labels=['student', 'priority-conflict'], complexity=7,
            pert_optimistic=sp*3, pert_most_likely=sp*5, pert_pessimistic=sp*7, pert_expected=sp*5,
            raci_responsible=[member], raci_accountable=m['lisa'], raci_consulted=[m['sarah']], raci_informed=[m['sophie'], m['lisa']],
            required_skills=['Python' if member==m['sarah'] or member==m['alex'] else 'Education'],
            estimated_hours=sp*5, actual_hours=0, risk_level='high',
        start_date=datetime(2024, 11, 2), end_date=datetime(2024, 11, 12)
    ))
    
    # ❌ Rachel gets overloaded (5 SP here + 3 Banking + 5 Logistics + 8 AI = 21 SP total!)
    db.session.add(Task(
        project_id=project.id, sprint_id=sprint2.id,
        name='Complete UI/UX Design System',
        title='Complete UI/UX Design System',
        description='Design system for entire LMS platform',
        status='To Do', priority='high', type='feature',
        story_points=5, completed=False, labels=['design', 'overload'], complexity=7,
        pert_optimistic=15, pert_most_likely=25, pert_pessimistic=35, pert_expected=25,
        raci_responsible=[m['rachel']], raci_accountable=m['lisa'], raci_consulted=[m['sarah']], raci_informed=[m['sophie'], m['lisa']],
        required_skills=['Figma', 'Design Systems', 'UI/UX'],
        estimated_hours=25, actual_hours=0, risk_level='medium',
        start_date=datetime(2024, 11, 2), end_date=datetime(2024, 11, 12)
    ))
    
    # Other tasks
    for name, member, sp in [
        ('Progress Tracking', m['tom'], 3),
        ('Certificate Generation', m['mike'], 4),
        ('Email Notifications', m['alex'], 3)
    ]:
        db.session.add(Task(
            project_id=project.id, sprint_id=sprint2.id,
            name=name, title=name, description=name, status='To Do', priority='medium', type='feature',
            story_points=sp, completed=False, labels=['student'], complexity=5,
            pert_optimistic=sp*3, pert_most_likely=sp*5, pert_pessimistic=sp*7, pert_expected=sp*5,
            raci_responsible=[member], raci_accountable=m['lisa'], raci_consulted=[m['sarah']], raci_informed=[m['sophie'], m['lisa']],
            required_skills=['Education'], estimated_hours=sp*5, actual_hours=0, risk_level='low',
        start_date=datetime(2024, 11, 2), end_date=datetime(2024, 11, 12)
    ))
    
    # Backlog
    for name, sp in [
        ('Discussion Forums', 13),
        ('Quiz Builder', 21),
        ('Peer Review System', 13),
        ('Gamification Features', 21),
        ('Mobile Learning App', 34),
        ('Parent Portal', 13),
        ('Analytics Dashboard', 13),
        ('Integration with Zoom', 8)
    ]:
        db.session.add(Task(
            project_id=project.id, sprint_id=None, name=name, title=name, description=name,
            status='To Do', priority='medium', type='feature', story_points=sp, completed=False,
            labels=['backlog'], complexity=7, pert_optimistic=sp*3, pert_most_likely=sp*5,
            pert_pessimistic=sp*7, pert_expected=sp*5,
            raci_responsible=[m['alex']], raci_accountable=m['lisa'], raci_consulted=[m['sarah']], raci_informed=[m['sophie'], m['lisa']],
            required_skills=['Education', 'E-learning'], estimated_hours=sp*5, actual_hours=0, risk_level='medium',
        start_date=datetime(2024, 11, 2), end_date=datetime(2024, 11, 12)
    ))
    
    for member_key in ['lisa', 'tom', 'sarah', 'alex', 'mike', 'rachel']:
        db.session.add(ProjectRole(
            project_id=project.id, member_id=m[member_key], role='owner' if member_key=='lisa' else 'developer',
            can_edit=True, can_delete=(member_key=='lisa'),
            can_manage_team=(member_key=='lisa'), can_manage_sprints=(member_key=='lisa')
        ))
    
    # Update project statistics
    db.session.flush()
    update_project_stats(project)
    db.session.commit()
    print("[OK] Education LMS created (priority conflicts, Rachel overloaded with 21 SP total)")

