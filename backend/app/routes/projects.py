"""
Projects API endpoints
"""
from flask import Blueprint, request, jsonify
from app import db
from app.models.project import Project
from app.models.sprint import Sprint
from app.models.project_role import ProjectRole
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
        # progress is computed automatically from tasks_completed / total_tasks
        if 'status' in data:
            project.status = data['status']
        if 'dueDate' in data:
            project.due_date = datetime.fromisoformat(data['dueDate']) if data['dueDate'] else None
        if 'teamMemberIds' in data:
            project.team_member_ids = data['teamMemberIds']
        if 'tasksCompleted' in data:
            project.tasks_completed = data['tasksCompleted']
        if 'totalTasks' in data:
            project.total_tasks = data['totalTasks']
        if 'totalStoryPoints' in data:
            project.total_story_points = data['totalStoryPoints']
        if 'estimatedDuration' in data:
            project.estimated_duration = data['estimatedDuration']
        
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

