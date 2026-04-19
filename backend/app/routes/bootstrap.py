"""
Database seed via shared secret (no shell access required).
Set BOOTSTRAP_SECRET on the server, then POST with header X-Bootstrap-Secret.

- Empty users table: runs full seed_all().
- Already has users: runs seed_users() only (adds demo accounts if those emails are missing).
"""
import os
import secrets as stdlib_secrets

from flask import Blueprint, jsonify, request

from app import db
from app.models.user import User

bootstrap_bp = Blueprint('bootstrap', __name__)


@bootstrap_bp.route('/seed', methods=['POST'])
def bootstrap_seed():
    configured = os.getenv('BOOTSTRAP_SECRET', '').strip()
    if not configured:
        return jsonify({'error': 'Bootstrap is not configured'}), 404

    provided = (request.headers.get('X-Bootstrap-Secret') or '').strip()
    if not provided or len(provided) != len(configured):
        return jsonify({'error': 'Invalid or missing secret'}), 401
    if not stdlib_secrets.compare_digest(provided, configured):
        return jsonify({'error': 'Invalid or missing secret'}), 401

    try:
        from seed_database import seed_all, seed_users

        if User.query.count() == 0:
            seed_all()
            return jsonify(
                {
                    'ok': True,
                    'already_seeded': False,
                    'message': 'Full seed completed. You can log in (e.g. admin@example.com / admin123).',
                }
            )

        # DB už má nejakého používateľa (napr. z Sign up), ale demo účty môžu chýbať.
        # seed_users() je idempotentné — doplní len chýbajúce emaily.
        seed_users()
        return jsonify(
            {
                'ok': True,
                'already_seeded': True,
                'demo_users_merged': True,
                'message': 'Database had users; demo accounts (admin/manager/developer) were added if missing.',
            }
        )
    except Exception as e:
        db.session.rollback()
        return jsonify({'ok': False, 'error': str(e)}), 500
