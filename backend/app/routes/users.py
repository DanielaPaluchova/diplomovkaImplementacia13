"""
User API endpoints
"""
from flask import Blueprint, jsonify
from app.models.user import User
from app.models.team_member import TeamMember
from app.models.project import Project
from app.utils.auth import token_required

users_bp = Blueprint('users', __name__)


@users_bp.route('/users', methods=['GET'])
@token_required
def get_users():
    """Get all users (for owner/assignee selection)"""
    try:
        users = User.query.all()
        return jsonify([user.to_dict() for user in users]), 200
    except Exception as e:
        return jsonify({'error': 'Failed to get users', 'message': str(e)}), 500


@users_bp.route('/team-members', methods=['GET'])
@token_required
def get_team_members():
    """Get all team members (for epic owner/task assignee selection)"""
    try:
        members = TeamMember.query.all()
        return jsonify([member.to_dict() for member in members]), 200
    except Exception as e:
        return jsonify({'error': 'Failed to get team members', 'message': str(e)}), 500


@users_bp.route('/projects/<int:project_id>/team-members', methods=['GET'])
@token_required
def get_project_team_members(project_id):
    """Get team members assigned to a specific project"""
    try:
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': 'Project not found'}), 404

        # Source of truth for project membership is project.team_member_ids.
        member_ids = project.team_member_ids or []
        if not member_ids:
            return jsonify([]), 200

        members = TeamMember.query.filter(TeamMember.id.in_(member_ids)).all()
        members_by_id = {member.id: member for member in members}

        # Preserve member order from project.team_member_ids
        ordered_members = [members_by_id[mid] for mid in member_ids if mid in members_by_id]
        return jsonify([member.to_dict() for member in ordered_members]), 200
    except Exception as e:
        return jsonify({'error': 'Failed to get project team members', 'message': str(e)}), 500
