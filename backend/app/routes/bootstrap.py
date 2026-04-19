"""
One-time database seed via shared secret (no shell access required).
Set BOOTSTRAP_SECRET on the server, then POST with header X-Bootstrap-Secret.
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

    if User.query.count() > 0:
        return jsonify(
            {
                'ok': True,
                'already_seeded': True,
                'message': 'Database already contains users; seed was skipped.',
            }
        )

    try:
        from seed_database import seed_all

        seed_all()
        return jsonify(
            {
                'ok': True,
                'already_seeded': False,
                'message': 'Seed completed. You can log in (e.g. admin@example.com / admin123).',
            }
        )
    except Exception as e:
        db.session.rollback()
        return jsonify({'ok': False, 'error': str(e)}), 500
