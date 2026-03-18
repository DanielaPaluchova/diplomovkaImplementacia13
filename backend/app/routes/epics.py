"""
Epic API endpoints for strategic planning
"""
from flask import Blueprint, request, jsonify
from app import db
from app.models.epic import Epic
from app.models.task import Task
from app.models.project import Project
from app.utils.auth import token_required
from datetime import datetime

epics_bp = Blueprint('epics', __name__)


def has_circular_dependency_epic(epic_id, dependencies, project_id):
    """
    Check if adding dependencies would create a circular dependency between epics.
    Uses DFS to detect cycles in the dependency graph.
    
    Args:
        epic_id: ID of the epic being updated/created
        dependencies: List of epic IDs that this epic depends on
        project_id: ID of the project
        
    Returns:
        tuple: (has_cycle: bool, error_message: str or None)
    """
    if not dependencies:
        return False, None
    
    # Build dependency graph for all epics in the project
    all_epics = Epic.query.filter_by(project_id=project_id).all()
    dependency_graph = {}
    
    for epic in all_epics:
        if epic.id == epic_id:
            # Use the new dependencies for the current epic
            dependency_graph[epic.id] = dependencies or []
        else:
            dependency_graph[epic.id] = epic.dependencies or []
    
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
    
    # Check for cycles starting from the current epic
    if has_cycle_dfs(epic_id):
        return True, 'Circular dependency detected. An epic cannot depend on itself directly or indirectly.'
    
    return False, None


@epics_bp.route('/projects/<int:project_id>/epics', methods=['GET'])
@token_required
def get_epics(project_id):
    """Get all epics for a project"""
    try:
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        include_tasks = request.args.get('include_tasks', 'false').lower() == 'true'
        
        epics = Epic.query.filter_by(project_id=project_id).all()
        return jsonify([epic.to_dict(include_tasks=include_tasks) for epic in epics]), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get epics', 'message': str(e)}), 500


@epics_bp.route('/projects/<int:project_id>/epics/<int:epic_id>', methods=['GET'])
@token_required
def get_epic(project_id, epic_id):
    """Get single epic with details"""
    try:
        epic = Epic.query.filter_by(id=epic_id, project_id=project_id).first()
        if not epic:
            return jsonify({'error': 'Epic not found'}), 404

        include_tasks = request.args.get('include_tasks', 'true').lower() == 'true'
        return jsonify(epic.to_dict(include_tasks=include_tasks)), 200

    except Exception as e:
        return jsonify({'error': 'Failed to get epic', 'message': str(e)}), 500


@epics_bp.route('/projects/<int:project_id>/epics', methods=['POST'])
@token_required
def create_epic(project_id):
    """Create new epic"""
    try:
        # Verify project exists
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        data = request.get_json()
        
        # Validate required fields
        if not data.get('name'):
            return jsonify({'error': 'Epic name is required'}), 400
        
        # Parse dates if provided
        start_date = None
        target_date = None
        if data.get('startDate'):
            try:
                start_date = datetime.fromisoformat(data['startDate'].replace('Z', '+00:00')).date()
            except:
                start_date = None
        if data.get('targetDate'):
            try:
                target_date = datetime.fromisoformat(data['targetDate'].replace('Z', '+00:00')).date()
            except:
                target_date = None
        
        # Create epic
        epic = Epic(
            project_id=project_id,
            name=data['name'],
            description=data.get('description', ''),
            status=data.get('status', 'to_do'),
            owner_id=data.get('ownerId'),
            priority=data.get('priority', 'medium'),
            labels=data.get('labels', []),
            start_date=start_date,
            target_date=target_date,
            business_value=data.get('businessValue', 0),
            target_release=data.get('targetRelease'),
            diagram_position_x=data.get('diagramPositionX'),
            diagram_position_y=data.get('diagramPositionY')
        )
        
        # PERT data
        pert = data.get('pert', {})
        if pert:
            epic.pert_optimistic = pert.get('optimistic')
            epic.pert_most_likely = pert.get('mostLikely')
            epic.pert_pessimistic = pert.get('pessimistic')
            epic.calculate_pert_expected()
        
        db.session.add(epic)
        db.session.flush()  # Get epic ID before validating dependencies
        
        # Dependencies (validate after epic has ID)
        if 'dependencies' in data and data.get('dependencies'):
            dependencies = data['dependencies']
            has_cycle, cycle_error = has_circular_dependency_epic(epic.id, dependencies, project_id)
            if has_cycle:
                db.session.rollback()
                return jsonify({'error': cycle_error}), 400
            epic.dependencies = dependencies
        
        db.session.commit()
        
        return jsonify(epic.to_dict(include_tasks=True)), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create epic', 'message': str(e)}), 500


@epics_bp.route('/projects/<int:project_id>/epics/<int:epic_id>', methods=['PUT'])
@token_required
def update_epic(project_id, epic_id):
    """Update epic"""
    try:
        epic = Epic.query.filter_by(id=epic_id, project_id=project_id).first()
        if not epic:
            return jsonify({'error': 'Epic not found'}), 404
        
        data = request.get_json()
        
        # Update basic fields
        if 'name' in data:
            epic.name = data['name']
        if 'description' in data:
            epic.description = data['description']
        if 'status' in data:
            epic.status = data['status']
        if 'ownerId' in data:
            epic.owner_id = data['ownerId']
        if 'priority' in data:
            epic.priority = data['priority']
        if 'labels' in data:
            epic.labels = data['labels']
        if 'startDate' in data:
            try:
                epic.start_date = datetime.fromisoformat(data['startDate'].replace('Z', '+00:00')).date() if data['startDate'] else None
            except:
                epic.start_date = None
        if 'targetDate' in data:
            try:
                epic.target_date = datetime.fromisoformat(data['targetDate'].replace('Z', '+00:00')).date() if data['targetDate'] else None
            except:
                epic.target_date = None
        if 'businessValue' in data:
            epic.business_value = data['businessValue']
        if 'targetRelease' in data:
            epic.target_release = data['targetRelease']
        if 'diagramPositionX' in data:
            epic.diagram_position_x = data['diagramPositionX']
        if 'diagramPositionY' in data:
            epic.diagram_position_y = data['diagramPositionY']
        
        # Update PERT data
        if 'pert' in data:
            pert = data['pert']
            if 'optimistic' in pert:
                epic.pert_optimistic = pert['optimistic']
            if 'mostLikely' in pert:
                epic.pert_most_likely = pert['mostLikely']
            if 'pessimistic' in pert:
                epic.pert_pessimistic = pert['pessimistic']
            epic.calculate_pert_expected()
        
        # Update dependencies (with circular dependency validation)
        if 'dependencies' in data:
            dependencies = data['dependencies']
            if dependencies:
                has_cycle, cycle_error = has_circular_dependency_epic(epic.id, dependencies, project_id)
                if has_cycle:
                    return jsonify({'error': cycle_error}), 400
            epic.dependencies = dependencies
        
        epic.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify(epic.to_dict(include_tasks=True)), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update epic', 'message': str(e)}), 500


@epics_bp.route('/projects/<int:project_id>/epics/<int:epic_id>', methods=['DELETE'])
@token_required
def delete_epic(project_id, epic_id):
    """Delete epic (tasks will have epic_id set to NULL due to ON DELETE SET NULL)"""
    try:
        epic = Epic.query.filter_by(id=epic_id, project_id=project_id).first()
        if not epic:
            return jsonify({'error': 'Epic not found'}), 404
        
        # ON DELETE SET NULL will automatically set epic_id = NULL for all tasks
        db.session.delete(epic)
        db.session.commit()
        
        return jsonify({'message': 'Epic deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete epic', 'message': str(e)}), 500


@epics_bp.route('/projects/<int:project_id>/epics/critical-path', methods=['GET'])
@token_required
def calculate_epic_critical_path(project_id):
    """
    Calculate critical path for epics using CPM (Critical Path Method)
    Epic duration = sum of PERT expected times of all tasks in the epic (or manual PERT)
    Returns: critical path epic IDs, early/late start/finish times, slack for each epic
    """
    try:
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        epics = Epic.query.filter_by(project_id=project_id).all()
        if not epics:
            return jsonify({
                'criticalPath': [],
                'epicSchedule': {},
                'projectDuration': 0,
                'projectVariance': 0,
                'projectStdDev': 0
            }), 200
        
        # Build epic info dictionary
        epic_info = {}
        for epic in epics:
            # Calculate epic duration
            # If epic has manual PERT estimates, use those
            if epic.pert_expected is not None:
                duration = epic.pert_expected
            else:
                # Otherwise, sum PERT expected times of all tasks in the epic
                tasks_in_epic = Task.query.filter_by(epic_id=epic.id).all()
                duration = sum(task.pert_expected or 0 for task in tasks_in_epic)
            
            epic_info[epic.id] = {
                'id': epic.id,
                'name': epic.name,
                'duration': duration,
                'dependencies': epic.dependencies or [],
                'dependents': []  # Will be populated
            }
        
        # Build dependents list (reverse dependencies)
        for epic_id, info in epic_info.items():
            for dep_id in info['dependencies']:
                if dep_id in epic_info:
                    epic_info[dep_id]['dependents'].append(epic_id)
        
        # Forward pass - Calculate Early Start (ES) and Early Finish (EF)
        def topological_sort():
            visited = set()
            stack = []
            
            def dfs(epic_id):
                if epic_id in visited:
                    return
                visited.add(epic_id)
                
                for dep_id in epic_info[epic_id]['dependencies']:
                    if dep_id in epic_info:
                        dfs(dep_id)
                
                stack.append(epic_id)
            
            for epic_id in epic_info.keys():
                if epic_id not in visited:
                    dfs(epic_id)
            
            return stack
        
        sorted_epics = topological_sort()
        
        # Calculate ES and EF
        for epic_id in sorted_epics:
            info = epic_info[epic_id]
            
            # ES = max(EF of all predecessors) or 0
            if info['dependencies']:
                es = max(
                    epic_info[dep_id].get('ef', 0) 
                    for dep_id in info['dependencies'] 
                    if dep_id in epic_info
                )
            else:
                es = 0
            
            info['es'] = es
            info['ef'] = es + info['duration']
        
        # Project duration is the maximum EF
        project_duration = max(info['ef'] for info in epic_info.values()) if epic_info else 0
        
        # Backward pass - Calculate Late Start (LS) and Late Finish (LF)
        for epic_id in reversed(sorted_epics):
            info = epic_info[epic_id]
            
            # LF = min(LS of all successors) or project_duration
            if info['dependents']:
                lf = min(
                    epic_info[dep_id].get('ls', project_duration)
                    for dep_id in info['dependents']
                    if dep_id in epic_info
                )
            else:
                lf = project_duration
            
            info['lf'] = lf
            info['ls'] = lf - info['duration']
            info['slack'] = info['ls'] - info['es']
        
        # Critical path: epics with zero slack
        critical_path = [
            epic_id for epic_id, info in epic_info.items() 
            if abs(info['slack']) < 0.01  # Use small epsilon for float comparison
        ]
        
        # PERT variance for each epic: σ² = ((P-O)/6)²
        # Epic-level: use epic PERT if available; else sum task variances
        for epic in epics:
            variance = 0.0
            if epic.pert_optimistic is not None and epic.pert_pessimistic is not None:
                std_dev = (epic.pert_pessimistic - epic.pert_optimistic) / 6.0
                variance = std_dev ** 2
            else:
                tasks_in_epic = Task.query.filter_by(epic_id=epic.id).all()
                for task in tasks_in_epic:
                    if task.pert_optimistic is not None and task.pert_pessimistic is not None:
                        task_std = (task.pert_pessimistic - task.pert_optimistic) / 6.0
                        variance += task_std ** 2
            epic_info[epic.id]['variance'] = variance
        
        # Project PERT stats: sum variances of epics on critical path
        project_variance = sum(
            epic_info[epic_id]['variance'] 
            for epic_id in critical_path 
            if epic_id in epic_info
        )
        project_std_dev = (project_variance ** 0.5) if project_variance > 0 else 0.0
        
        # Build response
        epic_schedule = {
            epic_id: {
                'epicId': info['id'],
                'epicName': info['name'],
                'duration': round(info['duration'], 2),
                'earlyStart': round(info['es'], 2),
                'earlyFinish': round(info['ef'], 2),
                'lateStart': round(info['ls'], 2),
                'lateFinish': round(info['lf'], 2),
                'slack': round(info['slack'], 2),
                'isCritical': abs(info['slack']) < 0.01,
                'variance': round(info['variance'], 4)
            }
            for epic_id, info in epic_info.items()
        }
        
        return jsonify({
            'criticalPath': critical_path,
            'epicSchedule': epic_schedule,
            'projectDuration': round(project_duration, 2),
            'projectVariance': round(project_variance, 4),
            'projectStdDev': round(project_std_dev, 2)
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to calculate critical path', 'message': str(e)}), 500
