from flask import Blueprint, request, jsonify, send_from_directory, url_for, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from app.models.job import Job
from app.models.application import Application
from app.models.resume import Resume
from datetime import datetime
import os
from urllib.parse import quote

UPLOAD_FOLDER = 'uploads/resumes'
bp = Blueprint('applications', __name__, url_prefix='/applications')

@bp.route('/', methods=['POST'])
@jwt_required()
def apply_job():
    data = request.json
    user_id = get_jwt_identity()  # Assuming get_jwt_identity returns the user_id directly
    
    # Check if required data is present
    if 'job_id' not in data:
        return jsonify({"success": False, "message": "Job ID is required"}), 400
    
    # Check if already applied to this job
    existing_application = Application.query.filter_by(
        user_id=user_id, 
        job_id=data['job_id']
    ).first()
    
    if existing_application:
        return jsonify({"success": False, "message": "You have already applied to this job"}), 400
    
    # Create new application without requiring resume_id
    application = Application(
        user_id=user_id,
        job_id=data['job_id'],
        # resume_id is now optional
        resume_id=data.get('resume_id', None)  # Will be None if not provided
    )
    
    try:
        db.session.add(application)
        db.session.commit()
        return jsonify({"success": True, "message": "Job application submitted successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"Error submitting application: {str(e)}"}), 500


@bp.route('/status', methods=['GET'])
@jwt_required()
def get_application_status():
    user_id = get_jwt_identity()  # Assuming get_jwt_identity returns the user_id directly
    
    # Fetch applications for the logged-in user
    applications = Application.query.filter_by(user_id=user_id).all()
    
    # Prepare a list of application statuses
    app_statuses = []
    for app in applications:
        try:
            job = Job.query.get(app.job_id)
            if job:
                app_statuses.append({
                    'job_title': job.title,
                    'company_name': job.company,
                    'status': app.status,  # Fixed status since we don't have a status field yet
                    'applied_at': app.applied_at.strftime('%Y-%m-%d %H:%M:%S') if app.applied_at else None
                })
        except Exception as e:
            # Log the error but continue processing other applications
            print(f"Error fetching job details for application {app.app_id}: {str(e)}")
    
    return jsonify({'success': True, 'applications': app_statuses}), 200



@bp.route('/employer', methods=['GET'])
@jwt_required()
def get_applications_for_employer():
    employer_id = get_jwt_identity()

    # Verify user is an employer
    user = User.query.get(employer_id)
    if not user or user.role != 'employer':
        return jsonify({"success": False, "message": "Access denied. Only employers can view applications"}), 403

    # 1. Get jobs posted by this employer
    jobs = Job.query.filter_by(posted_by=employer_id).all()
    job_ids = [job.job_id for job in jobs]

    if not job_ids:
        return jsonify({"success": True, "applications": []}), 200

    # 2. Get applications for these jobs
    applications = Application.query.filter(Application.job_id.in_(job_ids)).all()

    # 3. Prepare response data
    data = []
    for app in applications:
        job = Job.query.get(app.job_id)
        applicant = User.query.get(app.user_id)
        
        if job and applicant:
            # Get skills array (either parse from comma-separated string or empty array)
            skills = []
            if applicant.skills:
                skills = [skill.strip() for skill in applicant.skills.split(',')]
                
            app_data = {
                "application_id": app.app_id,  # Use the correct field name
                "user_id": applicant.user_id,
                "job_id": job.job_id,
                "applicant_name": applicant.name,
                "job_title": job.title,
                "skills": skills,
                "status": app.status if hasattr(app, 'status') and app.status else 'applied',
                "applied_at": app.applied_at.strftime('%Y-%m-%d %H:%M:%S') if app.applied_at else None
            }
            data.append(app_data)

    return jsonify({"success": True, "applications": data})

@bp.route('/<int:application_id>/status', methods=['PUT'])
@jwt_required()
def update_application_status(application_id):
    employer_id = get_jwt_identity()
    
    # Verify user is an employer
    user = User.query.get(employer_id)
    if not user or user.role != 'employer':
        return jsonify({"success": False, "message": "Access denied. Only employers can update application status"}), 403
    
    # Get application
    application = Application.query.get(application_id)
    if not application:
        return jsonify({"success": False, "message": "Application not found"}), 404
    
    # Verify employer owns the job
    job = Job.query.get(application.job_id)
    if not job or job.posted_by != employer_id:
        return jsonify({"success": False, "message": "Access denied. You can only update applications for your own jobs"}), 403
    
    data = request.get_json()
    if not data or 'status' not in data:
        return jsonify({"success": False, "message": "Status is required"}), 400
    
    # Update status
    try:
        # First check if status attribute exists (handling potential schema issues)
        if hasattr(application, 'status'):
            application.status = data['status']
        else:
            # If the status field doesn't exist, we can't update it
            return jsonify({"success": False, "message": "Status field not available in application schema"}), 500
        
        db.session.commit()
        return jsonify({"success": True, "message": "Application status updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"Error updating application status: {str(e)}"}), 500

@bp.route('/<int:application_id>/resume', methods=['GET'])
@jwt_required()
def get_resume_by_application(application_id):
    employer_id = get_jwt_identity()

    employer = User.query.get(employer_id)
    if not employer or employer.role != 'employer':
        return jsonify({"success": False, "message": "Access denied. Only employers can view resumes"}), 403

    application = Application.query.get(application_id)
    if not application:
        return jsonify({"success": False, "message": "Application not found"}), 404

    resume = Resume.query.filter_by(user_id=application.user_id).first()
    if not resume:
        return jsonify({"success": False, "message": "Resume not found"}), 404

    # Normalize path to URL format
    relative_path = os.path.relpath(resume.content, UPLOAD_FOLDER).replace("\\", "/")
    encoded_path = quote(relative_path)  # URL-safe

    view_url = url_for('applications.view_resume', filename=encoded_path, _external=True)
    print("Serving resume file path:", resume.content)
    print("Relative path:", relative_path)
    print("URL:", view_url)

    return jsonify({"success": True, "resume_url": view_url}), 200

@bp.route('/view/<path:filename>')
def view_resume(filename):
    uploads_dir = os.path.abspath(UPLOAD_FOLDER)
    try:
        # Reconstruct full file path safely
        return send_from_directory(directory=uploads_dir, path=filename)
    except FileNotFoundError:
        abort(404)
