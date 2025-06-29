from app import db
from datetime import datetime

class Application(db.Model):
    __tablename__ = 'applications'
    app_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.job_id'))
    resume_id = db.Column(db.Integer, db.ForeignKey('resumes.resume_id'))
    status = db.Column(db.String(20), default='applied')  # Added status field
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Application {self.app_id}>'