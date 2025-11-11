import sys
sys.path.insert(0, 'backend')

from app import create_app, db
from app.models.team_member import TeamMember
from app.models.task import Task
from app.models.project import Project
from app.models.sprint import Sprint

app = create_app()
with app.app_context():
    # Find Mark Thompson
    mark = TeamMember.query.filter_by(name='Mark Thompson').first()
    if not mark:
        print('Mark Thompson not found!')
        sys.exit(1)
    
    print(f'Mark Thompson (ID: {mark.id})')
    print(f'Max Story Points: {mark.max_story_points}')
    print('=' * 80)
    
    # Find active sprints
    active_sprints = Sprint.query.filter_by(status='active').all()
    print(f'\nActive Sprints: {[s.id for s in active_sprints]}')
    print('=' * 80)
    
    # Get all tasks where Mark is assigned in ANY RACI role
    all_tasks = Task.query.all()
    
    mark_tasks = []
    for task in all_tasks:
        roles = []
        if task.raci_responsible and mark.id in task.raci_responsible:
            roles.append('R')
        if task.raci_accountable and task.raci_accountable == mark.id:
            roles.append('A')
        if task.raci_consulted and mark.id in task.raci_consulted:
            roles.append('C')
        if task.raci_informed and mark.id in task.raci_informed:
            roles.append('I')
        
        if roles:
            mark_tasks.append((task, roles))
    
    print(f'\nAll tasks with Mark Thompson in RACI roles: {len(mark_tasks)}')
    print('=' * 80)
    
    # RACI Weights
    RACI_WEIGHTS = {
        'R': 1.0,
        'A': 0.1,
        'C': 0.05,
        'I': 0.01
    }
    
    total_weighted_sp = 0.0
    
    for task, roles in mark_tasks:
        sprint = Sprint.query.get(task.sprint_id) if task.sprint_id else None
        project = Project.query.get(task.project_id) if task.project_id else None
        
        sp = task.story_points or 0
        weighted_sp = sum(RACI_WEIGHTS[role] * sp for role in roles)
        total_weighted_sp += weighted_sp
        
        print(f'\nTask: {task.title or task.name}')
        print(f'  ID: {task.id}')
        print(f'  Status: {task.status}')
        print(f'  Story Points: {sp}')
        print(f'  RACI Roles: {", ".join(roles)}')
        print(f'  Weighted SP: {weighted_sp:.2f}')
        print(f'  Sprint ID: {task.sprint_id}')
        print(f'  Sprint Status: {sprint.status if sprint else "N/A"}')
        print(f'  Project: {project.name if project else "Unknown"}')
    
    print('=' * 80)
    print(f'\nTOTAL WEIGHTED SP: {total_weighted_sp:.2f}')
    print(f'MAX SP: {mark.max_story_points}')
    print(f'WORKLOAD %: {(total_weighted_sp / mark.max_story_points * 100):.1f}%')
    print('=' * 80)

