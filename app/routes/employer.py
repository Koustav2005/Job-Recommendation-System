from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from app.models.job import Job
from app.models.application import Application
from app.models.resume import Resume

bp = Blueprint('employer', __name__, url_prefix='/employer')

@bp.route('/profile', methods=['GET', 'PUT'])
@jwt_required()
def employer_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    # Check if user is an employer
    if user.role != 'employer':
        return jsonify({"message": "Access denied. Only employers can access this resource"}), 403
    
    if request.method == 'GET':
        # Return the employer's profile data
        profile_data = {
            "name": user.name,
            "email": user.email,
            "company_name": user.company_name,
            "industry": user.industry,
            "location": user.company_location, 
            "experience": user.experience,
            "website": user.company_website
        }
        return jsonify({"success": True, "profile": profile_data}), 200
    
    elif request.method == 'PUT':
        # Update the employer's profile
        data = request.get_json()
        
        if not data:
            return jsonify({"message": "No data provided"}), 400
        
        # Update user fields
        if 'company_name' in data:
            user.company_name = data['company_name']
        if 'industry' in data:
            user.industry = data['industry']
        if 'location' in data:
            user.company_location = data['location']
        if 'experience' in data:
            user.experience = data['experience']
        if 'website' in data:
            user.company_website = data['website']
        
        try:
            db.session.commit()
            return jsonify({"message": "Profile updated successfully"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": f"Error updating profile: {str(e)}"}), 500
