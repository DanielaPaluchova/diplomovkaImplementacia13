"""
Tasks API endpoints with PERT and RACI
"""
from flask import Blueprint, request, jsonify
from app import db
from app.models.task import Task
from app.models.project import Project
from app.utils.auth import token_required
from datetime import datetime

tasks_bp = Blueprint('tasks', __name__)


def validate_team_members(project, raci_data=None):
    """
    Validate that team members are assigned to the project.
    
    Args:
        project: Project object
        raci_data: Optional dictionary with RACI role assignments
        
    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    project_member_ids = project.team_member_ids or []
    
    # Check RACI roles
    if raci_data:
        # Check accountable (single value)
        if 'accountable' in raci_data and raci_data['accountable'] is not None:
            if raci_data['accountable'] not in project_member_ids:
                return False, f'Team member with ID {raci_data["accountable"]} is not assigned to this project'
        
        # Check responsible, consulted, informed (arrays)
        for role in ['responsible', 'consulted', 'informed']:
            if role in raci_data and raci_data[role]:
                for member_id in raci_data[role]:
                    if member_id not in project_member_ids:
                        return False, f'Team member with ID {member_id} is not assigned to this project'
    
    return True, None


def has_circular_dependency(task_id, dependencies, project_id):
    """
    Check if adding dependencies would create a circular dependency.
    Uses DFS to detect cycles in the dependency graph.
    
    Args:
        task_id: ID of the task being updated/created
        dependencies: List of task IDs that this task depends on
        project_id: ID of the project
        
    Returns:
        tuple: (has_cycle: bool, error_message: str or None)
    """
    if not dependencies:
        return False, None
    
    # Build dependency graph for all tasks in the project
    all_tasks = Task.query.filter_by(project_id=project_id).all()
    dependency_graph = {}
    
    for task in all_tasks:
        if task.id == task_id:
            # Use the new dependencies for the current task
            dependency_graph[task.id] = dependencies or []
        else:
            dependency_graph[task.id] = task.dependencies or []
    
    # DFS to detect cycles
    visited = set()
    rec_stack = set()
    
    def has_cycle_dfs(node):
        visited.add(node)
        rec_stack.add(node)
        
        # Visit all dependencies
        for dependency in dependency_graph.get(node, []):
            if dependency not in visited:
                if has_cycle_dfs(dependency):
                    return True
            elif dependency in rec_stack:
                return True
        
        rec_stack.remove(node)
        return False
    
    # Check for cycles starting from the current task
    if has_cycle_dfs(task_id):
        return True, 'Circular dependency detected. A task cannot depend on itself directly or indirectly.'
    
    return False, None


@tasks_bp.route('/', methods=['GET'])
@token_required
def get_tasks():
    """Get all tasks (optionally filter by project)"""
    try:
        project_id = request.args.get('project_id', type=int)
        
        if project_id:
            tasks = Task.query.filter_by(project_id=project_id).all()
        else:
            tasks = Task.query.all()
        
        return jsonify([task.to_dict() for task in tasks]), 200
    except Exception as e:
        return jsonify({'error': 'Failed to get tasks', 'message': str(e)}), 500


@tasks_bp.route('/<int:task_id>', methods=['GET'])
@token_required
def get_task(task_id):
    """Get single task"""
    try:
        task = Task.query.get(task_id)
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        return jsonify(task.to_dict()), 200
    except Exception as e:
        return jsonify({'error': 'Failed to get task', 'message': str(e)}), 500


@tasks_bp.route('/', methods=['POST'])
@token_required
def create_task():
    """Create new task with PERT and RACI data"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('name') or not data.get('projectId'):
            return jsonify({'error': 'Task name and projectId are required'}), 400
        
        # Check if project exists
        project = Project.query.get(data['projectId'])
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        # Validate team member assignments
        raci_data = data.get('raci', {})
        
        is_valid, error_message = validate_team_members(project, raci_data)
        if not is_valid:
            return jsonify({'error': error_message}), 400
        
        # Create task first to get an ID (we'll validate dependencies after)
        task = Task(
            project_id=data['projectId'],
            sprint_id=data.get('sprintId'),
            name=data['name'],
            title=data.get('title', data['name']),
            description=data.get('description', ''),
            status=data.get('status', 'To Do'),
            priority=data.get('priority', 'medium'),
            type=data.get('type', 'task'),
            story_points=data.get('storyPoints', 0),
            due_date=datetime.fromisoformat(data['dueDate']) if data.get('dueDate') else None,
            labels=data.get('labels', []),
            complexity=data.get('complexity', 0)
        )
        
        # PERT data
        pert = data.get('pert', {})
        if pert:
            task.pert_optimistic = pert.get('optimistic')
            task.pert_most_likely = pert.get('mostLikely')
            task.pert_pessimistic = pert.get('pessimistic')
            task.calculate_pert_expected()
        
        # RACI data
        raci = data.get('raci', {})
        if raci:
            task.raci_responsible = raci.get('responsible', [])
            task.raci_accountable = raci.get('accountable')
            task.raci_consulted = raci.get('consulted', [])
            task.raci_informed = raci.get('informed', [])
        
        db.session.add(task)
        db.session.flush()  # Get task ID before validating dependencies
        
        # Dependencies (validate after task has ID)
        if 'dependencies' in data and data.get('dependencies'):
            dependencies = data['dependencies']
            has_cycle, cycle_error = has_circular_dependency(task.id, dependencies, project.id)
            if has_cycle:
                db.session.rollback()
                return jsonify({'error': cycle_error}), 400
            task.dependencies = dependencies
        
        # Update project stats
        project.total_tasks += 1
        if task.status == 'Done':
            project.tasks_completed += 1
        if task.story_points:
            project.total_story_points += task.story_points
        
        db.session.commit()
        
        return jsonify(task.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create task', 'message': str(e)}), 500


@tasks_bp.route('/<int:task_id>', methods=['PUT'])
@token_required
def update_task(task_id):
    """Update task"""
    try:
        task = Task.query.get(task_id)
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        data = request.get_json()
        old_status = task.status
        old_story_points = task.story_points
        
        # Validate team member assignments if they're being updated
        project = task.project
        raci_data = data.get('raci') if 'raci' in data else None
        
        if raci_data is not None:
            is_valid, error_message = validate_team_members(project, raci_data)
            if not is_valid:
                return jsonify({'error': error_message}), 400
        
        # Update basic fields
        if 'name' in data:
            task.name = data['name']
        if 'title' in data:
            task.title = data['title']
        if 'description' in data:
            task.description = data['description']
        if 'status' in data:
            task.status = data['status']
        if 'priority' in data:
            task.priority = data['priority']
        if 'type' in data:
            task.type = data['type']
        if 'storyPoints' in data:
            task.story_points = data['storyPoints']
        if 'sprintId' in data:
            task.sprint_id = data['sprintId']
        if 'dueDate' in data:
            task.due_date = datetime.fromisoformat(data['dueDate']) if data['dueDate'] else None
        if 'labels' in data:
            task.labels = data['labels']
        if 'complexity' in data:
            task.complexity = data['complexity']
        if 'completed' in data:
            task.completed = data['completed']
        
        # Update diagram position
        if 'diagramPositionX' in data:
            task.diagram_position_x = data['diagramPositionX']
        if 'diagramPositionY' in data:
            task.diagram_position_y = data['diagramPositionY']
        
        # Update PERT data
        if 'pert' in data:
            pert = data['pert']
            if 'optimistic' in pert:
                task.pert_optimistic = pert['optimistic']
            if 'mostLikely' in pert:
                task.pert_most_likely = pert['mostLikely']
            if 'pessimistic' in pert:
                task.pert_pessimistic = pert['pessimistic']
            task.calculate_pert_expected()
        
        # Update dependencies (with circular dependency validation)
        if 'dependencies' in data:
            dependencies = data['dependencies']
            if dependencies:
                has_cycle, cycle_error = has_circular_dependency(task.id, dependencies, task.project_id)
                if has_cycle:
                    return jsonify({'error': cycle_error}), 400
            task.dependencies = dependencies
        
        # Update RACI data
        if 'raci' in data:
            raci = data['raci']
            if 'responsible' in raci:
                task.raci_responsible = raci['responsible']
            if 'accountable' in raci:
                task.raci_accountable = raci['accountable']
            if 'consulted' in raci:
                task.raci_consulted = raci['consulted']
            if 'informed' in raci:
                task.raci_informed = raci['informed']
        
        # Update project stats if status or story points changed
        project = task.project
        if old_status != task.status:
            if old_status == 'Done':
                project.tasks_completed -= 1
            if task.status == 'Done':
                project.tasks_completed += 1
        
        if old_story_points != task.story_points:
            project.total_story_points = project.total_story_points - old_story_points + task.story_points
        
        # progress is computed automatically in to_dict() method
        
        task.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify(task.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update task', 'message': str(e)}), 500


@tasks_bp.route('/<int:task_id>', methods=['DELETE'])
@token_required
def delete_task(task_id):
    """Delete task"""
    try:
        task = Task.query.get(task_id)
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        # Update project stats
        project = task.project
        project.total_tasks -= 1
        if task.status == 'Done':
            project.tasks_completed -= 1
        if task.story_points:
            project.total_story_points -= task.story_points
        
        # progress is computed automatically in to_dict() method
        
        db.session.delete(task)
        db.session.commit()
        
        return jsonify({'message': 'Task deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete task', 'message': str(e)}), 500


@tasks_bp.route('/bulk-update', methods=['POST'])
@token_required
def bulk_update_tasks():
    """Bulk update multiple tasks (for PERT/RACI optimization)"""
    try:
        data = request.get_json()
        tasks_data = data.get('tasks', [])
        
        updated_tasks = []
        
        for task_data in tasks_data:
            task_id = task_data.get('id')
            if not task_id:
                continue
            
            task = Task.query.get(task_id)
            if not task:
                continue
            
            # Validate team member assignments if RACI is being updated
            if 'raci' in task_data:
                project = task.project
                is_valid, error_message = validate_team_members(project, None, task_data['raci'])
                if not is_valid:
                    db.session.rollback()
                    return jsonify({'error': f'Task {task_id}: {error_message}'}), 400
            
            # Update PERT if provided
            if 'pert' in task_data:
                pert = task_data['pert']
                task.pert_optimistic = pert.get('optimistic', task.pert_optimistic)
                task.pert_most_likely = pert.get('mostLikely', task.pert_most_likely)
                task.pert_pessimistic = pert.get('pessimistic', task.pert_pessimistic)
                task.calculate_pert_expected()
            
            # Update RACI if provided
            if 'raci' in task_data:
                raci = task_data['raci']
                task.raci_responsible = raci.get('responsible', task.raci_responsible)
                task.raci_accountable = raci.get('accountable', task.raci_accountable)
                task.raci_consulted = raci.get('consulted', task.raci_consulted)
                task.raci_informed = raci.get('informed', task.raci_informed)
            
            task.updated_at = datetime.utcnow()
            updated_tasks.append(task)
        
        db.session.commit()
        
        return jsonify({
            'message': f'Successfully updated {len(updated_tasks)} tasks',
            'tasks': [task.to_dict() for task in updated_tasks]
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to bulk update tasks', 'message': str(e)}), 500

