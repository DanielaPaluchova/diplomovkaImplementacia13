"""
Fix avatar column to support base64 images
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import db, create_app
from sqlalchemy import text

app = create_app()

with app.app_context():
    try:
        # Change avatar column from String(500) to Text to support base64 images
        db.session.execute(text('ALTER TABLE team_members ALTER COLUMN avatar TYPE TEXT'))
        db.session.commit()
        print("✅ Successfully updated avatar column to TEXT")
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error updating avatar column: {e}")

