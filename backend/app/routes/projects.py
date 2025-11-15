"""
Projects API endpoints
"""
from flask import Blueprint, request, jsonify
from app import db
from app.models.project import Project
from app.models.sprint import Sprint
from app.models.project_role import ProjectRole
from app.models.optimization_log import OptimizationLog
from app.utils.auth import token_required
from datetime import datetime

projects_bp = Blueprint('projects', __name__)


@projects_bp.route('/', methods=['GET'])
@token_required
def get_projects():
    """Get all projects"""
    try:
        include_details = request.args.get('details', 'false').lower() == 'true'
        projects = Project.query.all()
        return jsonify([project.to_dict(include_details=include_details) for project in projects]), 200
    except Exception as e:
        return jsonify({'error': 'Failed to get projects', 'message': str(e)}), 500


@projects_bp.route('/<int:project_id>', methods=['GET'])
@token_required
def get_project(project_id):
    """Get single project with full details"""
    try:
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        return jsonify(project.to_dict(include_details=True)), 200
    except Exception as e:
        return jsonify({'error': 'Failed to get project', 'message': str(e)}), 500


@projects_bp.route('/', methods=['POST'])
@token_required
def create_project():
    """Create new project"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('name'):
            return jsonify({'error': 'Project name is required'}), 400
        
        project = Project(
            name=data['name'],
            description=data.get('description', ''),
            template=data.get('template'),
            icon=data.get('icon', 'folder'),
            status=data.get('status', 'In Progress'),
            due_date=datetime.fromisoformat(data['dueDate']) if data.get('dueDate') else None,
            team_member_ids=data.get('teamMemberIds', [])
        )
        
        db.session.add(project)
        db.session.flush()  # Get project.id
        
        # Add project roles if provided
        if data.get('roles'):
            for role_data in data['roles']:
                role = ProjectRole(
                    project_id=project.id,
                    member_id=role_data['memberId'],
                    role=role_data.get('role', 'developer'),
                    can_edit=role_data.get('permissions', {}).get('canEdit', True),
                    can_delete=role_data.get('permissions', {}).get('canDelete', False),
                    can_manage_team=role_data.get('permissions', {}).get('canManageTeam', False),
                    can_manage_sprints=role_data.get('permissions', {}).get('canManageSprints', False)
                )
                db.session.add(role)
        
        db.session.commit()
        
        return jsonify(project.to_dict(include_details=True)), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create project', 'message': str(e)}), 500


@projects_bp.route('/<int:project_id>', methods=['PUT'])
@token_required
def update_project(project_id):
    """Update project"""
    try:
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        data = request.get_json()
        
        # Update fields
        if 'name' in data:
            project.name = data['name']
        if 'description' in data:
            project.description = data['description']
        if 'template' in data:
            project.template = data['template']
        if 'icon' in data:
            project.icon = data['icon']
        # progress, tasksCompleted, and totalTasks are computed automatically from tasks relationship
        if 'status' in data:
            project.status = data['status']
        if 'dueDate' in data:
            project.due_date = datetime.fromisoformat(data['dueDate']) if data['dueDate'] else None
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
        # tasksCompleted and totalTasks are now computed dynamically - no longer updated manually
        if 'totalStoryPoints' in data:
            project.total_story_points = data['totalStoryPoints']
        if 'estimatedDuration' in data:
            project.estimated_duration = data['estimatedDuration']
        if 'raciWeights' in data:
            project.raci_weights = data['raciWeights']
        if 'pertWeights' in data:
            project.pert_weights = data['pertWeights']
        if 'maxStoryPointsPerPerson' in data:
            project.max_story_points_per_person = data['maxStoryPointsPerPerson']
        
        project.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify(project.to_dict(include_details=True)), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update project', 'message': str(e)}), 500


@projects_bp.route('/<int:project_id>', methods=['DELETE'])
@token_required
def delete_project(project_id):
    """Delete project"""
    try:
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        db.session.delete(project)
        db.session.commit()
        
        return jsonify({'message': 'Project deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete project', 'message': str(e)}), 500


# Sprint endpoints
@projects_bp.route('/<int:project_id>/sprints', methods=['POST'])
@token_required
def create_sprint(project_id):
    """Create new sprint for project"""
    try:
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        data = request.get_json()
        
        sprint = Sprint(
            project_id=project_id,
            name=data['name'],
            goal=data.get('goal', ''),
            start_date=datetime.fromisoformat(data['startDate']),
            end_date=datetime.fromisoformat(data['endDate']),
            status=data.get('status', 'planned'),
            task_ids=data.get('taskIds', [])
        )
        
        db.session.add(sprint)
        db.session.commit()
        
        return jsonify(sprint.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create sprint', 'message': str(e)}), 500


@projects_bp.route('/<int:project_id>/sprints/<int:sprint_id>', methods=['PUT'])
@token_required
def update_sprint(project_id, sprint_id):
    """Update sprint"""
    try:
        sprint = Sprint.query.filter_by(id=sprint_id, project_id=project_id).first()
        if not sprint:
            return jsonify({'error': 'Sprint not found'}), 404
        
        data = request.get_json()
        
        if 'name' in data:
            sprint.name = data['name']
        if 'goal' in data:
            sprint.goal = data['goal']
        if 'startDate' in data:
            sprint.start_date = datetime.fromisoformat(data['startDate'])
        if 'endDate' in data:
            sprint.end_date = datetime.fromisoformat(data['endDate'])
        if 'status' in data:
            sprint.status = data['status']
        # totalTasks, completedTasks, and taskIds are computed automatically from tasks relationship
        
        sprint.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify(sprint.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update sprint', 'message': str(e)}), 500


@projects_bp.route('/<int:project_id>/sprints/<int:sprint_id>', methods=['DELETE'])
@token_required
def delete_sprint(project_id, sprint_id):
    """Delete sprint"""
    try:
        sprint = Sprint.query.filter_by(id=sprint_id, project_id=project_id).first()
        if not sprint:
            return jsonify({'error': 'Sprint not found'}), 404
        
        db.session.delete(sprint)
        db.session.commit()
        
        return jsonify({'message': 'Sprint deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete sprint', 'message': str(e)}), 500


# PERT/CPM endpoints
@projects_bp.route('/<int:project_id>/critical-path', methods=['GET'])
@token_required
def calculate_critical_path(project_id):
    """
    Calculate critical path using CPM (Critical Path Method)
    Returns: critical path task IDs, early/late start/finish times, slack for each task
    """
    try:
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        tasks = project.tasks
        if not tasks:
            return jsonify({
                'criticalPath': [],
                'taskSchedule': {},
                'projectDuration': 0
            }), 200
        
        # Build task info dictionary
        task_info = {}
        for task in tasks:
            task_info[task.id] = {
                'id': task.id,
                'name': task.name,
                'duration': task.pert_expected or 0,
                'dependencies': task.dependencies or [],
                'dependents': []  # Will be populated
            }
        
        # Build dependents list (reverse dependencies)
        for task_id, info in task_info.items():
            for dep_id in info['dependencies']:
                if dep_id in task_info:
                    task_info[dep_id]['dependents'].append(task_id)
        
        # Forward pass - Calculate Early Start (ES) and Early Finish (EF)
        # Use topological sort to process tasks in dependency order
        def topological_sort():
            visited = set()
            stack = []
            
            def dfs(task_id):
                if task_id in visited:
                    return
                visited.add(task_id)
                
                for dep_id in task_info[task_id]['dependencies']:
                    if dep_id in task_info:
                        dfs(dep_id)
                
                stack.append(task_id)
            
            for task_id in task_info.keys():
                if task_id not in visited:
                    dfs(task_id)
            
            return stack
        
        sorted_tasks = topological_sort()
        
        # Calculate ES and EF
        for task_id in sorted_tasks:
            info = task_info[task_id]
            
            # ES = max(EF of all predecessors) or 0
            if info['dependencies']:
                es = max(
                    task_info[dep_id].get('ef', 0) 
                    for dep_id in info['dependencies'] 
                    if dep_id in task_info
                )
            else:
                es = 0
            
            info['es'] = es
            info['ef'] = es + info['duration']
        
        # Project duration is the maximum EF
        project_duration = max(info['ef'] for info in task_info.values()) if task_info else 0
        
        # Backward pass - Calculate Late Start (LS) and Late Finish (LF)
        # Process in reverse topological order
        for task_id in reversed(sorted_tasks):
            info = task_info[task_id]
            
            # LF = min(LS of all successors) or project_duration
            if info['dependents']:
                lf = min(
                    task_info[dep_id].get('ls', project_duration)
                    for dep_id in info['dependents']
                    if dep_id in task_info
                )
            else:
                lf = project_duration
            
            info['lf'] = lf
            info['ls'] = lf - info['duration']
        
        # Calculate slack and identify critical path
        critical_path = []
        task_schedule = {}
        
        for task_id, info in task_info.items():
            slack = info['ls'] - info['es']
            info['slack'] = slack
            
            is_critical = abs(slack) < 0.01  # Account for floating point precision
            
            if is_critical:
                critical_path.append(task_id)
            
            task_schedule[task_id] = {
                'taskId': task_id,
                'taskName': info['name'],
                'duration': info['duration'],
                'earlyStart': round(info['es'], 2),
                'earlyFinish': round(info['ef'], 2),
                'lateStart': round(info['ls'], 2),
                'lateFinish': round(info['lf'], 2),
                'slack': round(slack, 2),
                'isCritical': is_critical
            }
        
        return jsonify({
            'criticalPath': critical_path,
            'taskSchedule': task_schedule,
            'projectDuration': round(project_duration, 2)
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to calculate critical path', 'message': str(e)}), 500


@projects_bp.route('/<int:project_id>/pert-settings', methods=['PATCH'])
@token_required
def update_pert_settings(project_id):
    """Update PERT diagram settings (manual edges, layout settings)"""
    try:
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        data = request.get_json()
        
        if 'pertManualEdges' in data:
            project.pert_manual_edges = data['pertManualEdges']
        
        if 'pertLayoutSettings' in data:
            project.pert_layout_settings = data['pertLayoutSettings']
        
        project.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify(project.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update PERT settings', 'message': str(e)}), 500


@projects_bp.route('/<int:project_id>/configuration', methods=['GET'])
@token_required
def get_project_configuration(project_id):
    """Get project RACI and PERT configuration"""
    try:
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        # Default values
        default_raci_weights = {
            'responsible': 0.6,
            'accountable': 0.45,
            'consulted': 0.3,
            'informed': 0.05
        }
        
        default_pert_weights = {
            'optimistic': 1,
            'mostLikely': 4,
            'pessimistic': 1
        }
        
        return jsonify({
            'raciWeights': project.raci_weights or default_raci_weights,
            'pertWeights': project.pert_weights or default_pert_weights,
            'maxStoryPointsPerPerson': project.max_story_points_per_person
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get configuration', 'message': str(e)}), 500


@projects_bp.route('/<int:project_id>/configuration', methods=['PUT'])
@token_required
def update_project_configuration(project_id):
    """Update project RACI and PERT configuration"""
    try:
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        data = request.get_json()
        
        # Validate RACI weights if provided
        if 'raciWeights' in data:
            weights = data['raciWeights']
            if not all(0 <= weights.get(key, 0) <= 1 for key in ['responsible', 'accountable', 'consulted', 'informed']):
                return jsonify({'error': 'RACI weights must be between 0 and 1'}), 400
            project.raci_weights = weights
        
        # Validate PERT weights if provided
        if 'pertWeights' in data:
            weights = data['pertWeights']
            if not all(weights.get(key, 0) > 0 for key in ['optimistic', 'mostLikely', 'pessimistic']):
                return jsonify({'error': 'PERT weights must be positive'}), 400
            project.pert_weights = weights
        
        # Validate max story points
        if 'maxStoryPointsPerPerson' in data:
            max_sp = data['maxStoryPointsPerPerson']
            if max_sp <= 0:
                return jsonify({'error': 'Max story points must be positive'}), 400
            project.max_story_points_per_person = max_sp
        
        project.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'raciWeights': project.raci_weights,
            'pertWeights': project.pert_weights,
            'maxStoryPointsPerPerson': project.max_story_points_per_person
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update configuration', 'message': str(e)}), 500


# Optimization Log endpoints
@projects_bp.route('/<int:project_id>/optimization-logs', methods=['GET'])
@token_required
def get_optimization_logs(project_id):
    """Get optimization logs for a project"""
    try:
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        # Get query parameters
        limit = request.args.get('limit', type=int, default=50)
        optimization_type = request.args.get('type', None)
        
        # Build query
        query = OptimizationLog.query.filter_by(project_id=project_id)
        
        if optimization_type:
            query = query.filter_by(optimization_type=optimization_type)
        
        # Order by created_at descending (newest first)
        logs = query.order_by(OptimizationLog.created_at.desc()).limit(limit).all()
        
        return jsonify({
            'logs': [log.to_dict() for log in logs],
            'total': len(logs)
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get optimization logs', 'message': str(e)}), 500


@projects_bp.route('/<int:project_id>/members/<int:member_id>/role', methods=['PUT'])
@token_required
def update_member_role(project_id, member_id):
    """Update member's role in project"""
    try:
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        data = request.get_json()
        new_role = data.get('role')
        
        if not new_role:
            return jsonify({'error': 'Role is required'}), 400
        
        if new_role not in ['owner', 'admin', 'developer', 'viewer']:
            return jsonify({'error': 'Invalid role'}), 400
        
        # Check if member is in project
        if not project.team_member_ids or member_id not in project.team_member_ids:
            return jsonify({'error': 'Member not found in project'}), 404
        
        # Find existing role or create new one
        role = ProjectRole.query.filter_by(project_id=project_id, member_id=member_id).first()
        
        if role:
            # Update existing role
            role.role = new_role
            # Update permissions based on new role
            if new_role == 'owner':
                role.can_edit = True
                role.can_delete = True
                role.can_manage_team = True
                role.can_manage_sprints = True
            elif new_role == 'admin':
                role.can_edit = True
                role.can_delete = True
                role.can_manage_team = True
                role.can_manage_sprints = True
            elif new_role == 'developer':
                role.can_edit = True
                role.can_delete = False
                role.can_manage_team = False
                role.can_manage_sprints = False
            elif new_role == 'viewer':
                role.can_edit = False
                role.can_delete = False
                role.can_manage_team = False
                role.can_manage_sprints = False
        else:
            # Create new role
            role = ProjectRole(
                project_id=project_id,
                member_id=member_id,
                role=new_role,
                can_edit=new_role in ['owner', 'admin', 'developer'],
                can_delete=new_role in ['owner', 'admin'],
                can_manage_team=new_role in ['owner', 'admin'],
                can_manage_sprints=new_role in ['owner', 'admin']
            )
            db.session.add(role)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Role updated successfully',
            'role': {
                'memberId': role.member_id,
                'role': role.role,
                'permissions': {
                    'canEdit': role.can_edit,
                    'canDelete': role.can_delete,
                    'canManageTeam': role.can_manage_team,
                    'canManageSprints': role.can_manage_sprints
                }
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update member role', 'message': str(e)}), 500
