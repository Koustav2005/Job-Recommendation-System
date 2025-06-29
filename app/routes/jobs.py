from flask import Blueprint, request, jsonify
from app import db
from app.models.job import Job
from flask_jwt_extended import jwt_required, get_jwt_identity

bp = Blueprint('jobs', __name__, url_prefix='/jobs')

@bp.route('/', methods=['POST'])
@jwt_required()
def post_job():
    user_id = get_jwt_identity()  # Assuming user_id is a string now
    print("JWT Identity:", user_id)  # Debugging output

    # No need to check if user_id is a dictionary; it should be a string
    posted_by = user_id  # Directly use the user_id

    data = request.json
    required_fields = ['title', 'description', 'company', 'location', 'salary', 'requirements']
    for field in required_fields:
        if field not in data:
            return jsonify(message=f"Missing field: {field}"), 400

    job = Job(
        title=data['title'],
        description=data['description'],
        company=data['company'],
        location=data['location'],
        salary=data['salary'],
        requirements=data['requirements'],
        posted_by=posted_by,
        employer_id=user_id  # Use the user_id directly
    )

    db.session.add(job)
    db.session.commit()
    return jsonify(message="Job posted successfully"), 201

@bp.route('/', methods=['GET'])
def list_jobs():
    jobs = Job.query.all()
    return jsonify([
    {
        'job_id': j.job_id,
        'title': j.title,
        'description': j.description,
        'company': j.company,
        'location': j.location,
        'salary': j.salary,
        'requirements': j.requirements,
        'posted_by': j.posted_by
    } for j in jobs
]), 200

