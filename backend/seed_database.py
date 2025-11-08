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
    print("[OK] Users seeded")


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
            'skills': ['Vue.js', 'TypeScript', 'React', 'Node.js', 'GraphQL']
        },
        {
            'id': 2,
            'name': 'Sarah Johnson',
            'email': 'sarah.johnson@company.com',
            'role': 'Backend Developer',
            'avatar': 'https://cdn.quasar.dev/img/avatar3.jpg',
            'status': 'busy',
            'skills': ['Python', 'Django', 'PostgreSQL', 'Docker', 'AWS']
        },
        {
            'id': 3,
            'name': 'Mike Wilson',
            'email': 'mike.wilson@company.com',
            'role': 'DevOps Engineer',
            'avatar': 'https://cdn.quasar.dev/img/avatar4.jpg',
            'status': 'away',
            'skills': ['Kubernetes', 'Docker', 'Jenkins', 'AWS', 'Terraform']
        },
        {
            'id': 4,
            'name': 'Emma Davis',
            'email': 'emma.davis@company.com',
            'role': 'UI/UX Designer',
            'avatar': 'https://cdn.quasar.dev/img/avatar5.jpg',
            'status': 'online',
            'skills': ['Figma', 'Adobe XD', 'Sketch', 'Prototyping', 'User Research']
        },
        {
            'id': 5,
            'name': 'Alex Chen',
            'email': 'alex.chen@company.com',
            'role': 'Full Stack Developer',
            'avatar': 'https://cdn.quasar.dev/img/avatar.png',
            'status': 'online',
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
                skills=member_data['skills']
            )
            db.session.add(member)
    
    db.session.commit()
    print("[OK] Team members seeded")


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
            status='completed'
            # task_ids, total_tasks, completed_tasks computed automatically
        )
        sprint2 = Sprint(
            project_id=project1.id,
            name='Sprint 2',
            goal='Product catalog and shopping cart',
            start_date=datetime(2024, 1, 23),
            end_date=datetime(2024, 2, 6),
            status='active'
            # task_ids, total_tasks, completed_tasks computed automatically
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
        
        # Add sprint for project 2
        sprint3 = Sprint(
            project_id=project2.id,
            name='Sprint 1 - Mobile',
            goal='Core app functionality and navigation',
            start_date=datetime(2024, 2, 1),
            end_date=datetime(2024, 2, 15),
            status='active'
            # task_ids, total_tasks, completed_tasks computed automatically
        )
        db.session.add(sprint3)
        
        # Add tasks for project 2
        task4 = Task(
            project_id=project2.id,
            sprint_id=sprint3.id,
            name='User Registration Flow',
            title='User Registration Flow',
            description='Implement user registration with email verification',
            status='Done',
            priority='high',
            type='feature',
            story_points=8,
            due_date=datetime(2024, 2, 15),
            completed=True,
            labels=['mobile', 'frontend'],
            complexity=7,
            pert_optimistic=20,
            pert_most_likely=32,
            pert_pessimistic=48,
            raci_responsible=[1],
            raci_accountable=2,
            raci_consulted=[5],
            raci_informed=[]
        )
        task4.calculate_pert_expected()
        
        task5 = Task(
            project_id=project2.id,
            sprint_id=sprint3.id,
            name='Restaurant Listing Screen',
            title='Restaurant Listing Screen',
            description='Display nearby restaurants with filters',
            status='Done',
            priority='high',
            type='feature',
            story_points=5,
            due_date=datetime(2024, 2, 15),
            completed=True,
            labels=['mobile', 'ui'],
            complexity=6,
            pert_optimistic=16,
            pert_most_likely=24,
            pert_pessimistic=32,
            raci_responsible=[5],
            raci_accountable=2,
            raci_consulted=[1],
            raci_informed=[]
        )
        task5.calculate_pert_expected()
        
        task6 = Task(
            project_id=project2.id,
            sprint_id=sprint3.id,
            name='Order Management System',
            title='Order Management System',
            description='Backend API for order processing',
            status='In Progress',
            priority='medium',
            type='feature',
            story_points=8,
            due_date=datetime(2024, 2, 15),
            completed=False,
            labels=['backend', 'api'],
            complexity=8,
            pert_optimistic=24,
            pert_most_likely=40,
            pert_pessimistic=56,
            raci_responsible=[2],
            raci_accountable=2,
            raci_consulted=[5],
            raci_informed=[1]
        )
        task6.calculate_pert_expected()
        
        task7 = Task(
            project_id=project2.id,
            sprint_id=sprint3.id,
            name='Payment Integration',
            title='Payment Integration',
            description='Integrate Stripe payment gateway',
            status='To Do',
            priority='high',
            type='feature',
            story_points=13,
            due_date=datetime(2024, 2, 15),
            completed=False,
            labels=['backend', 'payment'],
            complexity=9,
            pert_optimistic=32,
            pert_most_likely=48,
            pert_pessimistic=72,
            raci_responsible=[2],
            raci_accountable=2,
            raci_consulted=[1, 5],
            raci_informed=[]
        )
        task7.calculate_pert_expected()
        
        db.session.add_all([task4, task5, task6, task7])
        
        # Project stats (total_tasks, tasks_completed) are updated automatically by Task model
        
        # Add more projects for variety
        project3 = Project(
            name='Data Migration Project',
            description='Legacy system to cloud migration with data transformation',
            template='Waterfall',
            icon='cloud_upload',
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
            tasks_completed=0,
            total_tasks=0,
            status='In Progress',
            due_date=datetime(2024, 6, 15),
            team_member_ids=[5, 6],
            total_story_points=95,
            estimated_duration=75
        )
        db.session.add(project6)
    
    # Create realistic project - Hotel Booking Platform
    if not Project.query.filter_by(name='Hotel Booking Platform').first():
        project7 = Project(
            name='Hotel Booking Platform',
            description='Comprehensive hotel reservation system with real-time availability, booking management, and payment processing',
            template='Agile Development',
            icon='hotel',
            tasks_completed=0,
            total_tasks=0,  # Will be updated after creating tasks
            status='In Progress',
            due_date=datetime(2024, 8, 30),
            team_member_ids=[1, 2, 3, 4, 5, 6],
            total_story_points=0,  # Will be calculated
            estimated_duration=180
        )
        db.session.add(project7)
        db.session.flush()
        
        # Add project roles for Hotel Booking Platform
        role_proj7_1 = ProjectRole(
            project_id=project7.id,
            member_id=6,
            role='owner',
            can_edit=True,
            can_delete=True,
            can_manage_team=True,
            can_manage_sprints=True
        )
        role_proj7_2 = ProjectRole(
            project_id=project7.id,
            member_id=1,
            role='developer',
            can_edit=True,
            can_delete=False,
            can_manage_team=False,
            can_manage_sprints=False
        )
        role_proj7_3 = ProjectRole(
            project_id=project7.id,
            member_id=2,
            role='developer',
            can_edit=True,
            can_delete=False,
            can_manage_team=False,
            can_manage_sprints=False
        )
        role_proj7_4 = ProjectRole(
            project_id=project7.id,
            member_id=4,
            role='developer',
            can_edit=True,
            can_delete=False,
            can_manage_team=False,
            can_manage_sprints=False
        )
        db.session.add_all([role_proj7_1, role_proj7_2, role_proj7_3, role_proj7_4])
        
        # Create Sprint 1 - Foundation & Analysis
        sprint_hotel_1 = Sprint(
            project_id=project7.id,
            name='Sprint 1 - Foundation & Analysis',
            goal='Complete requirements analysis, system design, and project setup',
            start_date=datetime(2024, 2, 5),
            end_date=datetime(2024, 2, 19),
            status='active'
            # task_ids, total_tasks, completed_tasks computed automatically
        )
        db.session.add(sprint_hotel_1)
        db.session.flush()
        
        # Create Sprint 2 - Planned
        sprint_hotel_2 = Sprint(
            project_id=project7.id,
            name='Sprint 2 - Core Backend',
            goal='Develop core backend services and database structure',
            start_date=datetime(2024, 2, 20),
            end_date=datetime(2024, 3, 5),
            status='planned'
            # task_ids, total_tasks, completed_tasks computed automatically
        )
        db.session.add(sprint_hotel_2)
        
        # ============================================
        # SPRINT 1 TASKS (Active Sprint)
        # ============================================
        
        # Task 1: Requirements Analysis (Lisa - PM)
        task_hotel_1 = Task(
            project_id=project7.id,
            sprint_id=sprint_hotel_1.id,
            name='Requirements Analysis & Stakeholder Interviews',
            title='Requirements Analysis & Stakeholder Interviews',
            description='Conduct stakeholder interviews, gather functional and non-functional requirements, create user stories',
            status='In Progress',
            priority='high',
            type='task',
            story_points=8,
            due_date=datetime(2024, 2, 10),
            completed=False,
            labels=['analysis', 'planning', 'requirements'],
            complexity=6,
            pert_optimistic=16,
            pert_most_likely=24,
            pert_pessimistic=40,
            raci_responsible=[6],
            raci_accountable=6,
            raci_consulted=[1, 2, 4],
            raci_informed=[3, 5],
            start_date=datetime(2024, 2, 5),
            end_date=datetime(2024, 2, 6),
            dependencies=[]
        )
        task_hotel_1.calculate_pert_expected()
        
        # Task 2: UI/UX Design & Wireframes (Emma - Designer)
        task_hotel_2 = Task(
            project_id=project7.id,
            sprint_id=sprint_hotel_1.id,
            name='UI/UX Design & Wireframes',
            title='UI/UX Design & Wireframes',
            description='Create wireframes, user flows, and high-fidelity mockups for all main screens',
            status='To Do',
            priority='high',
            type='feature',
            story_points=13,
            due_date=datetime(2024, 2, 15),
            completed=False,
            labels=['design', 'ui', 'wireframes'],
            complexity=7,
            pert_optimistic=24,
            pert_most_likely=40,
            pert_pessimistic=64,
            raci_responsible=[4],
            raci_accountable=6,
            raci_consulted=[1, 6],
            raci_informed=[2, 5],
            start_date=datetime(2024, 2, 6),
            end_date=datetime(2024, 2, 7),
            dependencies=[]
        )
        task_hotel_2.calculate_pert_expected()
        
        # Task 3: Database Schema Design (Sarah - Backend)
        task_hotel_3 = Task(
            project_id=project7.id,
            sprint_id=sprint_hotel_1.id,
            name='Database Schema Design',
            title='Database Schema Design',
            description='Design PostgreSQL database schema for hotels, rooms, bookings, users, and payments',
            status='To Do',
            priority='high',
            type='task',
            story_points=8,
            due_date=datetime(2024, 2, 12),
            completed=False,
            labels=['database', 'architecture', 'backend'],
            complexity=8,
            pert_optimistic=16,
            pert_most_likely=24,
            pert_pessimistic=40,
            raci_responsible=[2],
            raci_accountable=6,
            raci_consulted=[5],
            raci_informed=[1, 3],
            start_date=datetime(2024, 2, 6),
            end_date=datetime(2024, 2, 7),
            dependencies=[]
        )
        task_hotel_3.calculate_pert_expected()
        
        # Task 4: DevOps Infrastructure Setup (Mike - DevOps)
        task_hotel_4 = Task(
            project_id=project7.id,
            sprint_id=sprint_hotel_1.id,
            name='DevOps Infrastructure Setup',
            title='DevOps Infrastructure Setup',
            description='Setup CI/CD pipeline, Docker containers, AWS infrastructure, and monitoring',
            status='To Do',
            priority='high',
            type='task',
            story_points=13,
            due_date=datetime(2024, 2, 18),
            completed=False,
            labels=['devops', 'infrastructure', 'aws', 'docker'],
            complexity=9,
            pert_optimistic=32,
            pert_most_likely=48,
            pert_pessimistic=72,
            raci_responsible=[3],
            raci_accountable=6,
            raci_consulted=[2, 5],
            raci_informed=[1],
            start_date=datetime(2024, 2, 7),
            end_date=datetime(2024, 2, 9),
            dependencies=[]
        )
        task_hotel_4.calculate_pert_expected()
        
        # Task 5: API Architecture Design (Alex - Full Stack)
        task_hotel_5 = Task(
            project_id=project7.id,
            sprint_id=sprint_hotel_1.id,
            name='API Architecture & Documentation',
            title='API Architecture & Documentation',
            description='Design RESTful API architecture, define endpoints, create OpenAPI documentation',
            status='To Do',
            priority='high',
            type='task',
            story_points=8,
            due_date=datetime(2024, 2, 14),
            completed=False,
            labels=['api', 'architecture', 'documentation'],
            complexity=7,
            pert_optimistic=16,
            pert_most_likely=32,
            pert_pessimistic=48,
            raci_responsible=[5],
            raci_accountable=6,
            raci_consulted=[2],
            raci_informed=[1, 3],
            start_date=datetime(2024, 2, 7),
            end_date=datetime(2024, 2, 8),
            dependencies=[]
        )
        task_hotel_5.calculate_pert_expected()
        
        db.session.add_all([task_hotel_1, task_hotel_2, task_hotel_3, task_hotel_4, task_hotel_5])
        
        # ============================================
        # BACKLOG TASKS (Not in Sprint)
        # ============================================
        
        # BACKEND DEVELOPMENT TASKS
        
        task_hotel_6 = Task(
            project_id=project7.id,
            sprint_id=None,
            name='User Authentication & Authorization System',
            title='User Authentication & Authorization System',
            description='Implement JWT-based authentication with role-based access control (Customer, Hotel Manager, Admin)',
            status='To Do',
            priority='high',
            type='feature',
            story_points=13,
            due_date=datetime(2024, 3, 5),
            completed=False,
            labels=['backend', 'security', 'authentication'],
            complexity=8,
            pert_optimistic=32,
            pert_most_likely=48,
            pert_pessimistic=72,
            raci_responsible=[2],
            raci_accountable=6,
            raci_consulted=[5],
            raci_informed=[1]
        )
        task_hotel_6.calculate_pert_expected()
        
        task_hotel_7 = Task(
            project_id=project7.id,
            sprint_id=None,
            name='Hotel & Room Management API',
            title='Hotel & Room Management API',
            description='Create CRUD operations for hotels, rooms, amenities, and pricing management',
            status='To Do',
            priority='high',
            type='feature',
            story_points=13,
            due_date=datetime(2024, 3, 10),
            completed=False,
            labels=['backend', 'api', 'hotels'],
            complexity=8,
            pert_optimistic=32,
            pert_most_likely=48,
            pert_pessimistic=64,
            raci_responsible=[2],
            raci_accountable=6,
            raci_consulted=[5],
            raci_informed=[]
        )
        task_hotel_7.calculate_pert_expected()
        
        task_hotel_8 = Task(
            project_id=project7.id,
            sprint_id=None,
            name='Real-time Availability System',
            title='Real-time Availability System',
            description='Implement real-time room availability checking with Redis caching and conflict prevention',
            status='To Do',
            priority='high',
            type='feature',
            story_points=21,
            due_date=datetime(2024, 3, 20),
            completed=False,
            labels=['backend', 'realtime', 'redis', 'performance'],
            complexity=9,
            pert_optimistic=48,
            pert_most_likely=72,
            pert_pessimistic=104,
            raci_responsible=[5],
            raci_accountable=6,
            raci_consulted=[2, 3],
            raci_informed=[1]
        )
        task_hotel_8.calculate_pert_expected()
        
        task_hotel_9 = Task(
            project_id=project7.id,
            sprint_id=None,
            name='Booking Management System',
            title='Booking Management System',
            description='Create booking workflow: search, reserve, confirm, modify, cancel with proper state management',
            status='To Do',
            priority='high',
            type='feature',
            story_points=21,
            due_date=datetime(2024, 3, 25),
            completed=False,
            labels=['backend', 'bookings', 'workflow'],
            complexity=9,
            pert_optimistic=56,
            pert_most_likely=80,
            pert_pessimistic=120,
            raci_responsible=[2],
            raci_accountable=6,
            raci_consulted=[5],
            raci_informed=[1, 4]
        )
        task_hotel_9.calculate_pert_expected()
        
        task_hotel_10 = Task(
            project_id=project7.id,
            sprint_id=None,
            name='Payment Gateway Integration',
            title='Payment Gateway Integration',
            description='Integrate Stripe for payments, refunds, and secure payment processing with PCI compliance',
            status='To Do',
            priority='high',
            type='feature',
            story_points=21,
            due_date=datetime(2024, 4, 5),
            completed=False,
            labels=['backend', 'payment', 'stripe', 'security'],
            complexity=9,
            pert_optimistic=48,
            pert_most_likely=72,
            pert_pessimistic=96,
            raci_responsible=[2],
            raci_accountable=6,
            raci_consulted=[3, 5],
            raci_informed=[1]
        )
        task_hotel_10.calculate_pert_expected()
        
        task_hotel_11 = Task(
            project_id=project7.id,
            sprint_id=None,
            name='Email Notification Service',
            title='Email Notification Service',
            description='Implement email notifications for booking confirmations, reminders, and cancellations',
            status='To Do',
            priority='medium',
            type='feature',
            story_points=8,
            due_date=datetime(2024, 4, 10),
            completed=False,
            labels=['backend', 'notifications', 'email'],
            complexity=6,
            pert_optimistic=16,
            pert_most_likely=24,
            pert_pessimistic=40,
            raci_responsible=[5],
            raci_accountable=6,
            raci_consulted=[2],
            raci_informed=[]
        )
        task_hotel_11.calculate_pert_expected()
        
        task_hotel_12 = Task(
            project_id=project7.id,
            sprint_id=None,
            name='Search & Filter Engine',
            title='Search & Filter Engine',
            description='Implement advanced search with filters: location, price range, amenities, ratings, dates',
            status='To Do',
            priority='high',
            type='feature',
            story_points=13,
            due_date=datetime(2024, 4, 15),
            completed=False,
            labels=['backend', 'search', 'filters'],
            complexity=8,
            pert_optimistic=32,
            pert_most_likely=48,
            pert_pessimistic=72,
            raci_responsible=[5],
            raci_accountable=6,
            raci_consulted=[2],
            raci_informed=[1]
        )
        task_hotel_12.calculate_pert_expected()
        
        task_hotel_13 = Task(
            project_id=project7.id,
            sprint_id=None,
            name='Review & Rating System',
            title='Review & Rating System',
            description='Create review and rating system with moderation and verified stays validation',
            status='To Do',
            priority='medium',
            type='feature',
            story_points=13,
            due_date=datetime(2024, 4, 20),
            completed=False,
            labels=['backend', 'reviews', 'ratings'],
            complexity=7,
            pert_optimistic=24,
            pert_most_likely=40,
            pert_pessimistic=64,
            raci_responsible=[2],
            raci_accountable=6,
            raci_consulted=[5],
            raci_informed=[4]
        )
        task_hotel_13.calculate_pert_expected()
        
        # FRONTEND DEVELOPMENT TASKS
        
        task_hotel_14 = Task(
            project_id=project7.id,
            sprint_id=None,
            name='Frontend Project Setup & Architecture',
            title='Frontend Project Setup & Architecture',
            description='Setup Vue.js project with TypeScript, Quasar, state management, and routing',
            status='To Do',
            priority='high',
            type='task',
            story_points=8,
            due_date=datetime(2024, 3, 5),
            completed=False,
            labels=['frontend', 'setup', 'architecture'],
            complexity=6,
            pert_optimistic=16,
            pert_most_likely=24,
            pert_pessimistic=32,
            raci_responsible=[1],
            raci_accountable=6,
            raci_consulted=[5],
            raci_informed=[4]
        )
        task_hotel_14.calculate_pert_expected()
        
        task_hotel_15 = Task(
            project_id=project7.id,
            sprint_id=None,
            name='User Authentication UI',
            title='User Authentication UI',
            description='Create login, registration, password reset, and profile management screens',
            status='To Do',
            priority='high',
            type='feature',
            story_points=13,
            due_date=datetime(2024, 3, 15),
            completed=False,
            labels=['frontend', 'authentication', 'ui'],
            complexity=7,
            pert_optimistic=24,
            pert_most_likely=40,
            pert_pessimistic=56,
            raci_responsible=[1],
            raci_accountable=6,
            raci_consulted=[4],
            raci_informed=[2]
        )
        task_hotel_15.calculate_pert_expected()
        
        task_hotel_16 = Task(
            project_id=project7.id,
            sprint_id=None,
            name='Hotel Search & Listing UI',
            title='Hotel Search & Listing UI',
            description='Create hotel search page with filters, map view, and list view with infinite scroll',
            status='To Do',
            priority='high',
            type='feature',
            story_points=21,
            due_date=datetime(2024, 3, 30),
            completed=False,
            labels=['frontend', 'search', 'ui'],
            complexity=8,
            pert_optimistic=40,
            pert_most_likely=64,
            pert_pessimistic=96,
            raci_responsible=[1],
            raci_accountable=6,
            raci_consulted=[4, 5],
            raci_informed=[]
        )
        task_hotel_16.calculate_pert_expected()
        
        task_hotel_17 = Task(
            project_id=project7.id,
            sprint_id=None,
            name='Hotel Detail Page',
            title='Hotel Detail Page',
            description='Create hotel detail page with gallery, amenities, rooms, reviews, and booking widget',
            status='To Do',
            priority='high',
            type='feature',
            story_points=21,
            due_date=datetime(2024, 4, 10),
            completed=False,
            labels=['frontend', 'hotel-details', 'ui'],
            complexity=8,
            pert_optimistic=48,
            pert_most_likely=64,
            pert_pessimistic=88,
            raci_responsible=[1],
            raci_accountable=6,
            raci_consulted=[4],
            raci_informed=[2]
        )
        task_hotel_17.calculate_pert_expected()
        
        task_hotel_18 = Task(
            project_id=project7.id,
            sprint_id=None,
            name='Booking Flow UI',
            title='Booking Flow UI',
            description='Create multi-step booking flow: room selection, guest details, payment, confirmation',
            status='To Do',
            priority='high',
            type='feature',
            story_points=21,
            due_date=datetime(2024, 4, 25),
            completed=False,
            labels=['frontend', 'booking', 'checkout', 'ui'],
            complexity=9,
            pert_optimistic=48,
            pert_most_likely=72,
            pert_pessimistic=104,
            raci_responsible=[1],
            raci_accountable=6,
            raci_consulted=[4, 2],
            raci_informed=[5]
        )
        task_hotel_18.calculate_pert_expected()
        
        task_hotel_19 = Task(
            project_id=project7.id,
            sprint_id=None,
            name='User Dashboard & Booking Management',
            title='User Dashboard & Booking Management',
            description='Create user dashboard with booking history, upcoming stays, and cancellation management',
            status='To Do',
            priority='medium',
            type='feature',
            story_points=13,
            due_date=datetime(2024, 5, 5),
            completed=False,
            labels=['frontend', 'dashboard', 'ui'],
            complexity=7,
            pert_optimistic=32,
            pert_most_likely=48,
            pert_pessimistic=64,
            raci_responsible=[1],
            raci_accountable=6,
            raci_consulted=[4],
            raci_informed=[2]
        )
        task_hotel_19.calculate_pert_expected()
        
        task_hotel_20 = Task(
            project_id=project7.id,
            sprint_id=None,
            name='Hotel Manager Dashboard',
            title='Hotel Manager Dashboard',
            description='Create hotel manager interface for managing properties, rooms, bookings, and analytics',
            status='To Do',
            priority='medium',
            type='feature',
            story_points=21,
            due_date=datetime(2024, 5, 20),
            completed=False,
            labels=['frontend', 'admin', 'dashboard', 'ui'],
            complexity=8,
            pert_optimistic=48,
            pert_most_likely=72,
            pert_pessimistic=104,
            raci_responsible=[5],
            raci_accountable=6,
            raci_consulted=[1, 4],
            raci_informed=[2]
        )
        task_hotel_20.calculate_pert_expected()
        
        # TESTING TASKS
        
        task_hotel_21 = Task(
            project_id=project7.id,
            sprint_id=None,
            name='Backend Unit & Integration Tests',
            title='Backend Unit & Integration Tests',
            description='Write comprehensive unit and integration tests for all backend services with 80%+ coverage',
            status='To Do',
            priority='high',
            type='task',
            story_points=21,
            due_date=datetime(2024, 6, 5),
            completed=False,
            labels=['testing', 'backend', 'quality'],
            complexity=8,
            pert_optimistic=48,
            pert_most_likely=72,
            pert_pessimistic=96,
            raci_responsible=[2, 5],
            raci_accountable=6,
            raci_consulted=[],
            raci_informed=[1, 3]
        )
        task_hotel_21.calculate_pert_expected()
        
        task_hotel_22 = Task(
            project_id=project7.id,
            sprint_id=None,
            name='Frontend Unit & E2E Tests',
            title='Frontend Unit & E2E Tests',
            description='Write unit tests and end-to-end tests using Cypress for critical user flows',
            status='To Do',
            priority='high',
            type='task',
            story_points=21,
            due_date=datetime(2024, 6, 15),
            completed=False,
            labels=['testing', 'frontend', 'e2e', 'quality'],
            complexity=8,
            pert_optimistic=48,
            pert_most_likely=64,
            pert_pessimistic=88,
            raci_responsible=[1],
            raci_accountable=6,
            raci_consulted=[5],
            raci_informed=[2, 4]
        )
        task_hotel_22.calculate_pert_expected()
        
        task_hotel_23 = Task(
            project_id=project7.id,
            sprint_id=None,
            name='Performance Testing & Optimization',
            title='Performance Testing & Optimization',
            description='Conduct load testing, identify bottlenecks, optimize database queries and API response times',
            status='To Do',
            priority='medium',
            type='task',
            story_points=13,
            due_date=datetime(2024, 6, 25),
            completed=False,
            labels=['testing', 'performance', 'optimization'],
            complexity=8,
            pert_optimistic=32,
            pert_most_likely=48,
            pert_pessimistic=72,
            raci_responsible=[3, 5],
            raci_accountable=6,
            raci_consulted=[2],
            raci_informed=[1]
        )
        task_hotel_23.calculate_pert_expected()
        
        task_hotel_24 = Task(
            project_id=project7.id,
            sprint_id=None,
            name='Security Audit & Penetration Testing',
            title='Security Audit & Penetration Testing',
            description='Conduct security audit, penetration testing, fix vulnerabilities, ensure OWASP compliance',
            status='To Do',
            priority='high',
            type='task',
            story_points=13,
            due_date=datetime(2024, 7, 5),
            completed=False,
            labels=['security', 'testing', 'audit'],
            complexity=9,
            pert_optimistic=32,
            pert_most_likely=56,
            pert_pessimistic=88,
            raci_responsible=[3],
            raci_accountable=6,
            raci_consulted=[2, 5],
            raci_informed=[1]
        )
        task_hotel_24.calculate_pert_expected()
        
        # DEPLOYMENT & PRODUCTION TASKS
        
        task_hotel_25 = Task(
            project_id=project7.id,
            sprint_id=None,
            name='Staging Environment Setup',
            title='Staging Environment Setup',
            description='Setup staging environment identical to production for final testing and client demos',
            status='To Do',
            priority='high',
            type='task',
            story_points=8,
            due_date=datetime(2024, 7, 10),
            completed=False,
            labels=['devops', 'deployment', 'staging'],
            complexity=7,
            pert_optimistic=16,
            pert_most_likely=24,
            pert_pessimistic=40,
            raci_responsible=[3],
            raci_accountable=6,
            raci_consulted=[2, 5],
            raci_informed=[1]
        )
        task_hotel_25.calculate_pert_expected()
        
        task_hotel_26 = Task(
            project_id=project7.id,
            sprint_id=None,
            name='Database Migration Scripts',
            title='Database Migration Scripts',
            description='Create and test database migration scripts for production deployment',
            status='To Do',
            priority='high',
            type='task',
            story_points=8,
            due_date=datetime(2024, 7, 15),
            completed=False,
            labels=['database', 'deployment', 'migration'],
            complexity=7,
            pert_optimistic=16,
            pert_most_likely=24,
            pert_pessimistic=40,
            raci_responsible=[2],
            raci_accountable=6,
            raci_consulted=[3],
            raci_informed=[5]
        )
        task_hotel_26.calculate_pert_expected()
        
        task_hotel_27 = Task(
            project_id=project7.id,
            sprint_id=None,
            name='Production Deployment & Monitoring',
            title='Production Deployment & Monitoring',
            description='Deploy to production with zero downtime, setup monitoring, alerts, and logging',
            status='To Do',
            priority='high',
            type='task',
            story_points=13,
            due_date=datetime(2024, 7, 25),
            completed=False,
            labels=['devops', 'deployment', 'production', 'monitoring'],
            complexity=9,
            pert_optimistic=24,
            pert_most_likely=40,
            pert_pessimistic=64,
            raci_responsible=[3],
            raci_accountable=6,
            raci_consulted=[2, 5],
            raci_informed=[1, 4]
        )
        task_hotel_27.calculate_pert_expected()
        
        task_hotel_28 = Task(
            project_id=project7.id,
            sprint_id=None,
            name='User Documentation & Training',
            title='User Documentation & Training',
            description='Create user documentation, admin guides, video tutorials, and conduct training sessions',
            status='To Do',
            priority='medium',
            type='task',
            story_points=13,
            due_date=datetime(2024, 8, 5),
            completed=False,
            labels=['documentation', 'training'],
            complexity=6,
            pert_optimistic=24,
            pert_most_likely=40,
            pert_pessimistic=56,
            raci_responsible=[6, 4],
            raci_accountable=6,
            raci_consulted=[1, 2],
            raci_informed=[3, 5]
        )
        task_hotel_28.calculate_pert_expected()
        
        task_hotel_29 = Task(
            project_id=project7.id,
            sprint_id=None,
            name='Post-Launch Support & Bug Fixes',
            title='Post-Launch Support & Bug Fixes',
            description='Monitor production issues, fix bugs, provide user support for first 2 weeks after launch',
            status='To Do',
            priority='high',
            type='task',
            story_points=21,
            due_date=datetime(2024, 8, 30),
            completed=False,
            labels=['support', 'bugfix', 'production'],
            complexity=7,
            pert_optimistic=40,
            pert_most_likely=64,
            pert_pessimistic=96,
            raci_responsible=[1, 2, 3, 5],
            raci_accountable=6,
            raci_consulted=[],
            raci_informed=[4]
        )
        task_hotel_29.calculate_pert_expected()
        
        # Add all hotel booking tasks
        db.session.add_all([
            task_hotel_6, task_hotel_7, task_hotel_8, task_hotel_9, task_hotel_10,
            task_hotel_11, task_hotel_12, task_hotel_13, task_hotel_14, task_hotel_15,
            task_hotel_16, task_hotel_17, task_hotel_18, task_hotel_19, task_hotel_20,
            task_hotel_21, task_hotel_22, task_hotel_23, task_hotel_24, task_hotel_25,
            task_hotel_26, task_hotel_27, task_hotel_28, task_hotel_29
        ])
        
        # Update project stats
        project7.total_tasks = 29
        project7.tasks_completed = 0
        project7.total_story_points = 413  # Sum of all story points
    
    db.session.commit()
    print("[OK] Projects seeded")


def seed_all():
    """Seed all data"""
    print("\n[*] Starting database seeding...\n")
    
    seed_users()
    seed_team_members()
    seed_projects()
    
    print("\n[SUCCESS] Database seeding completed!\n")


if __name__ == '__main__':
    app = create_app()
    
    with app.app_context():
        # Create all tables
        print("Creating database tables...")
        db.create_all()
        print("[OK] Tables created\n")
        
        # Seed data
        seed_all()

