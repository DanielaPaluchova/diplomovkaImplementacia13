"""
Seed database with initial data from frontend mock data
"""
from app import create_app, db
from app.models.user import User
from app.models.team_member import TeamMember
from app.models.project import Project
from app.models.sprint import Sprint
from app.models.task import Task
from app.models.project_role import ProjectRole
from app.models.experiment import Experiment
from datetime import datetime, timedelta

def seed_users():
    """Seed demo users"""
    print("Seeding users...")
    
    users_data = [
        {
            'email': 'admin@example.com',
            'password': 'admin123',
            'name': 'Admin User',
            'role': 'admin',
            'avatar': 'https://cdn.quasar.dev/img/avatar.png'
        },
        {
            'email': 'manager@example.com',
            'password': 'manager123',
            'name': 'Project Manager',
            'role': 'manager',
            'avatar': 'https://cdn.quasar.dev/img/avatar2.jpg'
        },
        {
            'email': 'developer@example.com',
            'password': 'dev123',
            'name': 'Developer',
            'role': 'developer',
            'avatar': 'https://cdn.quasar.dev/img/avatar3.jpg'
        }
    ]
    
    for user_data in users_data:
        if not User.query.filter_by(email=user_data['email']).first():
            user = User(
                email=user_data['email'],
                name=user_data['name'],
                role=user_data['role'],
                avatar=user_data['avatar']
            )
            user.set_password(user_data['password'])
            db.session.add(user)
    
    db.session.commit()
    print("✓ Users seeded")


def seed_team_members():
    """Seed team members"""
    print("Seeding team members...")
    
    members_data = [
        {
            'id': 1,
            'name': 'John Smith',
            'email': 'john.smith@company.com',
            'role': 'Senior Frontend Developer',
            'avatar': 'https://cdn.quasar.dev/img/avatar2.jpg',
            'status': 'online',
            'workload': 85,
            'skills': ['Vue.js', 'TypeScript', 'React', 'Node.js', 'GraphQL']
        },
        {
            'id': 2,
            'name': 'Sarah Johnson',
            'email': 'sarah.johnson@company.com',
            'role': 'Backend Developer',
            'avatar': 'https://cdn.quasar.dev/img/avatar3.jpg',
            'status': 'busy',
            'workload': 75,
            'skills': ['Python', 'Django', 'PostgreSQL', 'Docker', 'AWS']
        },
        {
            'id': 3,
            'name': 'Mike Wilson',
            'email': 'mike.wilson@company.com',
            'role': 'DevOps Engineer',
            'avatar': 'https://cdn.quasar.dev/img/avatar4.jpg',
            'status': 'away',
            'workload': 90,
            'skills': ['Kubernetes', 'Docker', 'Jenkins', 'AWS', 'Terraform']
        },
        {
            'id': 4,
            'name': 'Emma Davis',
            'email': 'emma.davis@company.com',
            'role': 'UI/UX Designer',
            'avatar': 'https://cdn.quasar.dev/img/avatar5.jpg',
            'status': 'online',
            'workload': 60,
            'skills': ['Figma', 'Adobe XD', 'Sketch', 'Prototyping', 'User Research']
        },
        {
            'id': 5,
            'name': 'Alex Chen',
            'email': 'alex.chen@company.com',
            'role': 'Full Stack Developer',
            'avatar': 'https://cdn.quasar.dev/img/avatar.png',
            'status': 'online',
            'workload': 70,
            'skills': ['Vue.js', 'Python', 'FastAPI', 'MongoDB', 'Redis']
        },
        {
            'id': 6,
            'name': 'Lisa Rodriguez',
            'email': 'lisa.rodriguez@company.com',
            'role': 'Project Manager',
            'system_role': 'manager',
            'avatar': 'https://cdn.quasar.dev/img/avatar6.jpg',
            'status': 'busy',
            'workload': 95,
            'skills': ['Scrum', 'Kanban', 'PERT', 'Risk Management', 'Stakeholder Management']
        }
    ]
    
    for member_data in members_data:
        if not TeamMember.query.filter_by(email=member_data['email']).first():
            member = TeamMember(
                name=member_data['name'],
                email=member_data['email'],
                role=member_data['role'],
                system_role=member_data.get('system_role'),
                avatar=member_data['avatar'],
                status=member_data['status'],
                workload=member_data['workload'],
                skills=member_data['skills']
            )
            db.session.add(member)
    
    db.session.commit()
    print("✓ Team members seeded")


def seed_experiments():
    """Seed experiments"""
    print("Seeding experiments...")
    
    experiments_data = [
        {
            'name': 'PERT+RACI vs Traditional Planning',
            'description': 'Comparing integrated PERT+RACI approach with traditional planning methods across 10 projects',
            'hypothesis': 'PERT+RACI integration will improve delivery accuracy by 25% and reduce team conflicts by 30%',
            'status': 'completed',
            'methodology': 'PERT+RACI vs Traditional',
            'start_date': datetime(2023, 10, 1),
            'end_date': datetime(2023, 12, 15),
            'participants': 50,
            'results': {'success': True, 'improvement': 28, 'confidence': 93}
        },
        {
            'name': 'Automatic Workload Rebalancing',
            'description': 'Testing automatic RACI reassignment when team members are overloaded (>80% workload)',
            'hypothesis': 'Automatic rebalancing will maintain team utilization under 80% while preserving project deadlines',
            'status': 'running',
            'methodology': 'Load Balancing Comparison',
            'start_date': datetime(2023, 11, 15),
            'end_date': datetime(2024, 1, 30),
            'participants': 35
        },
        {
            'name': 'Requirement Change Adaptation',
            'description': 'Simulating 50 client requirement changes and measuring system adaptation speed and accuracy',
            'hypothesis': 'System will adapt to requirement changes in <5 seconds while maintaining optimal PERT+RACI balance',
            'status': 'running',
            'methodology': 'Controlled Experiment',
            'start_date': datetime(2024, 1, 5),
            'end_date': datetime(2024, 2, 5),
            'participants': 25
        },
        {
            'name': 'Risk-Based PERT Optimization',
            'description': 'Comparing traditional PERT with risk-adjusted PERT (factoring in team overload)',
            'hypothesis': 'Risk-aware PERT will reduce project delays by 40% compared to standard PERT',
            'status': 'completed',
            'methodology': 'Risk-based Adaptation',
            'start_date': datetime(2023, 9, 1),
            'end_date': datetime(2023, 11, 30),
            'participants': 45,
            'results': {'success': True, 'improvement': 43, 'confidence': 89}
        },
        {
            'name': 'Multi-Project RACI Conflicts',
            'description': 'Identifying and resolving RACI role conflicts when team members work across multiple projects',
            'hypothesis': 'Automated conflict detection will reduce role confusion by 60%',
            'status': 'planning',
            'methodology': 'Before/After Study',
            'start_date': datetime(2024, 2, 1),
            'end_date': datetime(2024, 4, 1),
            'participants': 40
        }
    ]
    
    for exp_data in experiments_data:
        if not Experiment.query.filter_by(name=exp_data['name']).first():
            experiment = Experiment(**exp_data)
            db.session.add(experiment)
    
    db.session.commit()
    print("✓ Experiments seeded")


def seed_projects():
    """Seed projects with sprints and tasks"""
    print("Seeding projects...")
    
    # Create first project
    if not Project.query.filter_by(name='E-commerce Platform Redesign').first():
        project1 = Project(
            name='E-commerce Platform Redesign',
            description='Complete UI/UX overhaul of the main platform',
            template='Agile Development',
            icon='shopping_cart',
            progress=75,
            tasks_completed=3,
            total_tasks=9,
            status='On Track',
            due_date=datetime(2024, 3, 15),
            team_member_ids=[1, 3, 4],
            total_story_points=63,
            estimated_duration=45
        )
        db.session.add(project1)
        db.session.flush()
        
        # Add sprints for project 1
        sprint1 = Sprint(
            project_id=project1.id,
            name='Sprint 1',
            goal='Setup authentication and user management',
            start_date=datetime(2024, 1, 8),
            end_date=datetime(2024, 1, 22),
            status='completed',
            total_tasks=3,
            completed_tasks=3,
            task_ids=[1, 2, 3]
        )
        sprint2 = Sprint(
            project_id=project1.id,
            name='Sprint 2',
            goal='Product catalog and shopping cart',
            start_date=datetime(2024, 1, 23),
            end_date=datetime(2024, 2, 6),
            status='active',
            total_tasks=3,
            completed_tasks=0,
            task_ids=[4, 5, 6]
        )
        db.session.add_all([sprint1, sprint2])
        
        # Add tasks for project 1
        task1 = Task(
            project_id=project1.id,
            sprint_id=sprint1.id,
            name='User Authentication System',
            title='User Authentication System',
            description='Implement JWT-based authentication with refresh tokens',
            status='Done',
            priority='high',
            type='feature',
            story_points=8,
            assignee_id=1,
            assignee='John Smith',
            due_date=datetime(2024, 1, 22),
            completed=True,
            labels=['backend', 'security'],
            complexity=8,
            pert_optimistic=24,
            pert_most_likely=40,
            pert_pessimistic=64,
            raci_responsible=[1],
            raci_accountable=1,
            raci_consulted=[3],
            raci_informed=[4]
        )
        task1.calculate_pert_expected()
        
        task2 = Task(
            project_id=project1.id,
            sprint_id=sprint1.id,
            name='Product Catalog API',
            title='Product Catalog API',
            description='Create REST API endpoints for product catalog',
            status='Done',
            priority='high',
            type='feature',
            story_points=5,
            assignee_id=3,
            assignee='Mike Wilson',
            due_date=datetime(2024, 1, 22),
            completed=True,
            labels=['backend', 'api'],
            complexity=6,
            pert_optimistic=16,
            pert_most_likely=24,
            pert_pessimistic=40,
            raci_responsible=[3],
            raci_accountable=1,
            raci_consulted=[],
            raci_informed=[4]
        )
        task2.calculate_pert_expected()
        
        task3 = Task(
            project_id=project1.id,
            sprint_id=sprint1.id,
            name='Shopping Cart Component',
            title='Shopping Cart Component',
            description='Build shopping cart UI with add/remove functionality',
            status='Done',
            priority='high',
            type='feature',
            story_points=8,
            assignee_id=4,
            assignee='Emma Davis',
            due_date=datetime(2024, 1, 22),
            completed=True,
            labels=['frontend', 'ui'],
            complexity=7,
            pert_optimistic=20,
            pert_most_likely=32,
            pert_pessimistic=52,
            raci_responsible=[4],
            raci_accountable=1,
            raci_consulted=[3],
            raci_informed=[]
        )
        task3.calculate_pert_expected()
        
        db.session.add_all([task1, task2, task3])
        
        # Add project roles
        role1 = ProjectRole(
            project_id=project1.id,
            member_id=4,
            role='owner',
            can_edit=True,
            can_delete=True,
            can_manage_team=True,
            can_manage_sprints=True
        )
        role2 = ProjectRole(
            project_id=project1.id,
            member_id=1,
            role='developer',
            can_edit=True,
            can_delete=False,
            can_manage_team=False,
            can_manage_sprints=False
        )
        db.session.add_all([role1, role2])
    
    # Create second project - Mobile App
    if not Project.query.filter_by(name='Mobile App Development').first():
        project2 = Project(
            name='Mobile App Development',
            description='Native iOS and Android application for food delivery',
            template='Agile Development',
            icon='phone_android',
            progress=45,
            tasks_completed=2,
            total_tasks=7,
            status='In Progress',
            due_date=datetime(2024, 4, 20),
            team_member_ids=[1, 2, 5],
            total_story_points=85,
            estimated_duration=60
        )
        db.session.add(project2)
        db.session.flush()
        
        # Add more projects for variety
        project3 = Project(
            name='Data Migration Project',
            description='Legacy system to cloud migration with data transformation',
            template='Waterfall',
            icon='cloud_upload',
            progress=30,
            tasks_completed=0,
            total_tasks=0,
            status='At Risk',
            due_date=datetime(2024, 5, 30),
            team_member_ids=[2, 3, 6],
            total_story_points=120,
            estimated_duration=90
        )
        db.session.add(project3)
        db.session.flush()
        
        project4 = Project(
            name='AI Chatbot Integration',
            description='Integration of AI-powered chatbot for customer support',
            template='Agile Development',
            icon='smart_toy',
            progress=60,
            tasks_completed=0,
            total_tasks=0,
            status='On Track',
            due_date=datetime(2024, 3, 10),
            team_member_ids=[1, 5],
            total_story_points=50,
            estimated_duration=30
        )
        db.session.add(project4)
        db.session.flush()
        
        project5 = Project(
            name='Security Audit & Compliance',
            description='Complete security audit and GDPR compliance implementation',
            template='Waterfall',
            icon='security',
            progress=90,
            tasks_completed=0,
            total_tasks=0,
            status='On Track',
            due_date=datetime(2024, 2, 5),
            team_member_ids=[2, 3],
            total_story_points=40,
            estimated_duration=20
        )
        db.session.add(project5)
        db.session.flush()
        
        project6 = Project(
            name='API Modernization',
            description='Modernizing REST APIs to GraphQL with performance optimization',
            template='Hybrid',
            icon='api',
            progress=25,
            tasks_completed=0,
            total_tasks=0,
            status='In Progress',
            due_date=datetime(2024, 6, 15),
            team_member_ids=[5, 6],
            total_story_points=95,
            estimated_duration=75
        )
        db.session.add(project6)
    
    db.session.commit()
    print("✓ Projects seeded")


def seed_all():
    """Seed all data"""
    print("\n🌱 Starting database seeding...\n")
    
    seed_users()
    seed_team_members()
    seed_experiments()
    seed_projects()
    
    print("\n✅ Database seeding completed!\n")


if __name__ == '__main__':
    app = create_app()
    
    with app.app_context():
        # Create all tables
        print("Creating database tables...")
        db.create_all()
        print("✓ Tables created\n")
        
        # Seed data
        seed_all()

