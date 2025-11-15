"""
Teams API endpoints
"""
from flask import Blueprint, request, jsonify
from app import db
from app.models.team_member import TeamMember
from app.models.project import Project
from app.models.task import Task
from app.utils.auth import token_required
from datetime import datetime
from sqlalchemy import or_, func

teams_bp = Blueprint('teams', __name__)


def calculate_member_metrics(member_id):
    """Calculate active projects, workload, and story points for a team member"""
    # Calculate active projects
    # Get all projects and check if member is in team_member_ids array
    all_projects = Project.query.all()
    projects_as_member = sum(1 for p in all_projects if p.team_member_ids and member_id in p.team_member_ids)
    
    # Count projects where member has assigned tasks (via RACI)
    all_tasks = Task.query.all()
    projects_with_tasks = len(set(
        task.project_id for task in all_tasks 
        if (task.raci_responsible and member_id in task.raci_responsible) or 
           task.raci_accountable == member_id
    ))
    
    # Use the max to avoid double counting
    active_projects = max(projects_as_member, projects_with_tasks)
    
    # Calculate workload based on tasks in ACTIVE SPRINTS only (not all incomplete tasks)
    # This matches the frontend WorkloadDashboard calculation
    from app.models.sprint import Sprint
    
    # Get all active sprints
    active_sprints = Sprint.query.filter_by(status='active').all()
    active_sprint_ids = [sprint.id for sprint in active_sprints]
    
    # Filter tasks: in active sprint, assigned to member (Sprint Commitment)
    active_sprint_tasks = [
        task for task in all_tasks
        if task.sprint_id in active_sprint_ids and (
               task.raci_responsible and member_id in task.raci_responsible
           )
    ]
    
    total_story_points = sum(task.story_points or 0 for task in active_sprint_tasks)
    
    # Get member's max capacity
    member = TeamMember.query.get(member_id)
    max_capacity = member.max_story_points if member else 20
    
    # Calculate workload as percentage based on member's max capacity
    # Don't cap at 100% - show real overload
    workload = int((total_story_points / max_capacity) * 100) if max_capacity > 0 else 0
    
    return active_projects, workload, total_story_points


@teams_bp.route('/', methods=['GET'])
@token_required
def get_teams():
    """Get all team members"""
    try:
        team_members = TeamMember.query.all()
        result = []
        for member in team_members:
            active_projects, workload, total_story_points = calculate_member_metrics(member.id)
            result.append(member.to_dict(active_projects=active_projects, workload=workload, total_story_points=total_story_points))
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': 'Failed to get team members', 'message': str(e)}), 500


@teams_bp.route('/<int:member_id>', methods=['GET'])
@token_required
def get_team_member(member_id):
    """Get single team member"""
    try:
        member = TeamMember.query.get(member_id)
        if not member:
            return jsonify({'error': 'Team member not found'}), 404
        active_projects, workload, total_story_points = calculate_member_metrics(member.id)
        return jsonify(member.to_dict(active_projects=active_projects, workload=workload, total_story_points=total_story_points)), 200
    except Exception as e:
        return jsonify({'error': 'Failed to get team member', 'message': str(e)}), 500


@teams_bp.route('/', methods=['POST'])
@token_required
def create_team_member():
    """Create new team member"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('name') or not data.get('email') or not data.get('role'):
            return jsonify({'error': 'Name, email, and role are required'}), 400
        
        # Check if email already exists
        if TeamMember.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already exists'}), 409
        
        member = TeamMember(
            name=data['name'],
            email=data['email'],
            role=data['role'],
            system_role=data.get('systemRole'),
            avatar=data.get('avatar', 'https://cdn.quasar.dev/img/avatar.png'),
            status=data.get('status', 'offline'),
            skills=data.get('skills', []),
            max_story_points=data.get('maxStoryPoints', 20)
        )
        
        db.session.add(member)
        db.session.commit()
        
        # Calculate metrics for the new member
        active_projects, workload, total_story_points = calculate_member_metrics(member.id)
        return jsonify(member.to_dict(active_projects=active_projects, workload=workload, total_story_points=total_story_points)), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create team member', 'message': str(e)}), 500


@teams_bp.route('/<int:member_id>', methods=['PUT'])
@token_required
def update_team_member(member_id):
    """Update team member"""
    try:
        member = TeamMember.query.get(member_id)
        if not member:
            return jsonify({'error': 'Team member not found'}), 404
        
        data = request.get_json()
        
        # Update fields
        if 'name' in data:
            member.name = data['name']
        if 'email' in data:
            member.email = data['email']
        if 'role' in data:
            member.role = data['role']
        if 'systemRole' in data:
            member.system_role = data['systemRole']
        if 'avatar' in data:
            member.avatar = data['avatar']
        if 'status' in data:
            member.status = data['status']
        if 'skills' in data:
            member.skills = data['skills']
        if 'maxStoryPoints' in data:
            member.max_story_points = data['maxStoryPoints']
        
        member.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Calculate metrics for the updated member
        active_projects, workload, total_story_points = calculate_member_metrics(member.id)
        return jsonify(member.to_dict(active_projects=active_projects, workload=workload, total_story_points=total_story_points)), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update team member', 'message': str(e)}), 500


@teams_bp.route('/<int:member_id>', methods=['DELETE'])
@token_required
def delete_team_member(member_id):
    """Delete team member and cleanup RACI assignments"""
    try:
        member = TeamMember.query.get(member_id)
        if not member:
            return jsonify({'error': 'Team member not found'}), 404
        
        # Import cleanup function
        from app.routes.tasks import cleanup_member_from_tasks
        
        # Remove member from all RACI roles in all tasks
        updated_tasks = cleanup_member_from_tasks(member_id)
        
        # Remove member from all projects
        from app.models.project import Project
        projects = Project.query.all()
        for project in projects:
            if project.team_member_ids and member_id in project.team_member_ids:
                project.team_member_ids = [m for m in project.team_member_ids if m != member_id]
                db.session.add(project)
        
        # Delete member
        db.session.delete(member)
        db.session.commit()
        
        return jsonify({
            'message': 'Team member deleted successfully',
            'tasksUpdated': updated_tasks
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete team member', 'message': str(e)}), 500

