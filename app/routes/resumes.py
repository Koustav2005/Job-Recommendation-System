from flask import Blueprint, request, jsonify
from app import db
from app.models.resume import Resume
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import os

bp = Blueprint('resumes', __name__, url_prefix='/resumes')

UPLOAD_FOLDER = 'uploads/resumes'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt'}  # added .doc

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/', methods=['POST'])
@jwt_required()
def upload_resume():
    user_id = int(get_jwt_identity())

    if 'file' not in request.files:
        return jsonify(message="No file part in request."), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify(message="No file selected."), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        user_folder = os.path.join(UPLOAD_FOLDER, f"user_{user_id}")
        os.makedirs(user_folder, exist_ok=True)
        file_path = os.path.join(user_folder, secure_filename(filename))

        file.save(file_path)

        resume = Resume(user_id=user_id, content=file_path)
        db.session.add(resume)
        db.session.commit()

        return jsonify(message="Resume uploaded successfully.", resume_id=resume.resume_id, file_path=file_path), 201

    return jsonify(message="Invalid file type."), 400
   
