"""
Activity Logs API endpoints
"""
from flask import Blueprint, jsonify, request
from datetime import datetime
from app import db
from app.models.activity_log import ActivityLog
from app.models.user import User
from app.utils.auth import token_required, get_current_user, admin_required

activity_logs_bp = Blueprint('activity_logs', __name__)


@activity_logs_bp.route('/activity-logs', methods=['POST'])
@token_required
def create_activity_log():
    """Log a user action (called from frontend)"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 401

        data = request.get_json() or {}
        action = data.get('action')
        entity_type = data.get('entityType')
        project_id = data.get('projectId')
        entity_id = data.get('entityId')
        details = data.get('details', {})
        route = data.get('route')

        if not action or not entity_type:
            return jsonify({'error': 'action and entityType are required'}), 400

        ip_address = request.remote_addr if request else None

        log = ActivityLog(
            user_id=user.id,
            action=action,
            entity_type=entity_type,
            project_id=project_id,
            entity_id=entity_id,
            details=details,
            route=route,
            ip_address=ip_address,
        )
        db.session.add(log)
        db.session.commit()

        return jsonify(log.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create activity log', 'message': str(e)}), 500


@activity_logs_bp.route('/admin/activity-logs', methods=['GET'])
@admin_required
def get_activity_logs():
    """Get activity logs with filters (admin only)"""
    try:
        user_id = request.args.get('userId', type=int)
        project_id = request.args.get('projectId', type=int)
        action = request.args.get('action')
        entity_type = request.args.get('entityType')
        date_from = request.args.get('dateFrom')
        date_to = request.args.get('dateTo')
        search = request.args.get('search')
        page = request.args.get('page', 1, type=int)
        limit = min(request.args.get('limit', 50, type=int), 100)

        query = ActivityLog.query

        if user_id:
            query = query.filter(ActivityLog.user_id == user_id)
        if project_id:
            query = query.filter(ActivityLog.project_id == project_id)
        if action:
            query = query.filter(ActivityLog.action == action)
        if entity_type:
            query = query.filter(ActivityLog.entity_type == entity_type)
        if date_from:
            try:
                dt_from = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
                query = query.filter(ActivityLog.created_at >= dt_from)
            except (ValueError, TypeError):
                pass
        if date_to:
            try:
                dt_to = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
                query = query.filter(ActivityLog.created_at <= dt_to)
            except (ValueError, TypeError):
                pass
        if search:
            query = query.join(User).filter(
                db.or_(
                    User.name.ilike(f'%{search}%'),
                    User.email.ilike(f'%{search}%'),
                    ActivityLog.action.ilike(f'%{search}%'),
                    ActivityLog.entity_type.ilike(f'%{search}%'),
                )
            )

        query = query.order_by(ActivityLog.created_at.desc())
        pagination = query.paginate(page=page, per_page=limit, error_out=False)
        logs = pagination.items

        return jsonify({
            'logs': [log.to_dict() for log in logs],
            'total': pagination.total,
            'page': page,
            'limit': limit,
            'pages': pagination.pages,
        }), 200
    except Exception as e:
        return jsonify({'error': 'Failed to get activity logs', 'message': str(e)}), 500


@activity_logs_bp.route('/admin/activity-logs/actions', methods=['GET'])
@admin_required
def get_activity_actions():
    """Get distinct actions for filter dropdown (admin only)"""
    try:
        actions = db.session.query(ActivityLog.action).distinct().order_by(ActivityLog.action).all()
        return jsonify([a[0] for a in actions]), 200
    except Exception as e:
        return jsonify({'error': 'Failed to get actions', 'message': str(e)}), 500


@activity_logs_bp.route('/admin/activity-logs/entity-types', methods=['GET'])
@admin_required
def get_entity_types():
    """Get distinct entity types for filter dropdown (admin only)"""
    try:
        types = db.session.query(ActivityLog.entity_type).distinct().order_by(ActivityLog.entity_type).all()
        return jsonify([t[0] for t in types]), 200
    except Exception as e:
        return jsonify({'error': 'Failed to get entity types', 'message': str(e)}), 500
