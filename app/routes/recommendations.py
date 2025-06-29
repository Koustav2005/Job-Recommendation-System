from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.models.job import Job
from app.models.resume import Resume
from app import db

bp = Blueprint('recommendations', __name__, url_prefix='/recommendations')

@bp.route('/', methods=['GET'])
@jwt_required()
def get_recommendations():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify(success=False, message="User not found"), 404

    resume = Resume.query.filter_by(user_id=user_id).first()
 
    if resume:
        resume_words = set(resume.content.lower().split())

    user_skills = set()
    if user.skills:
        user_skills = set(skill.strip().lower() for skill in user.skills.split(','))

    recommendations = []
    jobs = Job.query.all()

    for job in jobs:
        job_requirements = set(job.requirements.lower().split(','))

        match_score = len(job_requirements & user_skills) / len(job_requirements) if job_requirements else 0

        if match_score > 0:
            recommendations.append({
                'job_id': job.job_id,
                'title': job.title,
                'company': job.company,
                'location': job.location,
                'description': job.description,
                'requirements': job.requirements,
                'skills': job.requirements.split(','),
                'salary': job.salary,
                'posted_by': job.posted_by,
                'match_score': round(match_score, 2)
            })

    recommendations.sort(key=lambda x: x['match_score'], reverse=True)

    return jsonify(success=True, jobs=recommendations), 200
