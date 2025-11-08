from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime
import uuid

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    userID = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(80), unique=True, nullable=False)
    hashed_password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    images = db.relationship('Image', backref='owner', lazy=True)

class Image(db.Model):
    __tablename__ = 'images'
    
    imageID = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    caption = db.Column(db.String(200))
    ownerUserID = db.Column(db.String(36), db.ForeignKey('users.userID'), nullable=False)
    originalURL = db.Column(db.String(500))
    thumbnailURL = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    file_name = db.Column(db.String(255))
