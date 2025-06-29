from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User

bp = Blueprint('profile', __name__, url_prefix='/profile')

@bp.route('/update', methods=['PUT'])
@jwt_required()
def update_profile():
    try:
        user_id = get_jwt_identity()  # ✅ get user_id directly as string
        print("User ID from token:", user_id)  # Debug print

        user = User.query.get(user_id)
        if not user:
            return jsonify({"message": "User not found"}), 404

        # Update user information
        data = request.json
        user.current_role = data.get('current_role')
        user.preferred_location = data.get('preferred_location')
        user.skills = data.get('skills')

        db.session.commit()

        return jsonify({"message": "Profile updated successfully"}), 200

    except Exception as e:
        print(f"Error updating profile: {e}")
        return jsonify({"message": "Error updating profile"}), 500

