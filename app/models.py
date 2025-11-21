from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class User(UserMixin, db.Model):
    """User model for customers and creators"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'customer' or 'creator'
    
    # Creator-specific fields
    domain = db.Column(db.String(50))  # e.g., 'graphic_design', 'video_editing'
    bio = db.Column(db.Text)
    skills = db.Column(db.Text)  # JSON string or comma-separated
    location = db.Column(db.String(100))
    rating = db.Column(db.Float, default=0.0)
    total_reviews = db.Column(db.Integer, default=0)
    
    # Payment details (for creators)
    upi_id = db.Column(db.String(100))  # Creator's UPI ID for payments
    
    # Profile image
    profile_image = db.Column(db.String(255))
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    projects_posted = db.relationship('Project', foreign_keys='Project.posted_by_id', backref='customer', lazy='dynamic')
    projects_assigned = db.relationship('Project', foreign_keys='Project.assigned_to_id', backref='creator', lazy='dynamic')
    applications = db.relationship('Application', backref='creator', lazy='dynamic')
    messages_sent = db.relationship('Message', backref='sender', lazy='dynamic')
    packages = db.relationship('Package', backref='creator', lazy='dynamic')
    uploads = db.relationship('Upload', backref='owner', lazy='dynamic')
    reviews_given = db.relationship('Review', foreign_keys='Review.reviewer_id', backref='reviewer', lazy='dynamic')
    reviews_received = db.relationship('Review', foreign_keys='Review.creator_id', backref='reviewed_creator', lazy='dynamic')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.email}>'


class Project(db.Model):
    """Project model for customer job postings"""
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # 'design', 'video_editing', 'photography', 'videography'
    budget = db.Column(db.Float, nullable=False)
    deadline = db.Column(db.Date)
    
    # Status: 'open', 'assigned', 'in_progress', 'completed', 'cancelled'
    status = db.Column(db.String(20), default='open')
    
    # Relationships
    posted_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # Delivery fields (Drive link instead of file upload)
    delivery_link = db.Column(db.String(500))  # Google Drive/Dropbox link
    delivery_note = db.Column(db.Text)  # Creator's delivery message
    delivered_at = db.Column(db.DateTime)  # When creator submitted delivery
    
    # Relationships
    applications = db.relationship('Application', backref='project', lazy='dynamic', cascade='all, delete-orphan')
    messages = db.relationship('Message', backref='project', lazy='dynamic', cascade='all, delete-orphan')
    transactions = db.relationship('Transaction', backref='project', lazy='dynamic')
    reviews = db.relationship('Review', backref='project', lazy='dynamic')
    
    def __repr__(self):
        return f'<Project {self.title}>'


class Application(db.Model):
    """Application model for creator proposals"""
    __tablename__ = 'applications'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    quote = db.Column(db.Float, nullable=False)
    message = db.Column(db.Text)
    delivery_days = db.Column(db.Integer)
    
    # Status: 'pending', 'accepted', 'rejected'
    status = db.Column(db.String(20), default='pending')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Application {self.id} for Project {self.project_id}>'


class Message(db.Model):
    """Message model for project chat"""
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    content = db.Column(db.Text, nullable=False)
    attachments = db.Column(db.Text)  # JSON string of file paths
    
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Message {self.id}>'


class Transaction(db.Model):
    """Transaction model for payments"""
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    amount = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(20), default='full')  # 'milestone' or 'full'
    
    # Status: 'pending', 'completed', 'refunded', 'failed'
    status = db.Column(db.String(20), default='pending')
    
    # Stripe data
    stripe_session_id = db.Column(db.String(255))
    stripe_payment_intent = db.Column(db.String(255))
    provider_payload = db.Column(db.Text)  # JSON string
    
    # UPI Payment Confirmation Fields
    customer_confirmed = db.Column(db.Boolean, default=False)  # Customer paid
    creator_confirmed = db.Column(db.Boolean, default=False)  # Creator received
    payment_confirmed_at = db.Column(db.DateTime)  # When both confirmed
    payment_screenshot = db.Column(db.String(500))  # Optional proof
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # Relationships
    customer = db.relationship('User', foreign_keys=[customer_id])
    creator = db.relationship('User', foreign_keys=[creator_id])
    
    def __repr__(self):
        return f'<Transaction {self.id}>'


class Review(db.Model):
    """Review model for creator ratings"""
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Customer
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    rating = db.Column(db.Integer, nullable=False)  # 1-5
    comment = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Review {self.id}>'


class Package(db.Model):
    """Service package model for creators"""
    __tablename__ = 'packages'
    
    id = db.Column(db.Integer, primary_key=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    tier = db.Column(db.String(20))  # 'basic', 'standard', 'premium'
    price = db.Column(db.Float, nullable=False)
    delivery_days = db.Column(db.Integer, nullable=False)
    revisions = db.Column(db.Integer, default=0)
    
    # Features as JSON string
    features = db.Column(db.Text)
    
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Package {self.title}>'


class Upload(db.Model):
    """Upload model for portfolio and project files"""
    __tablename__ = 'uploads'
    
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    file_path = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(50))  # 'image', 'video', 'document'
    file_size = db.Column(db.Integer)  # in bytes
    original_filename = db.Column(db.String(255))
    
    # Portfolio, project attachment, or message attachment
    upload_type = db.Column(db.String(50))  # 'portfolio', 'project', 'message'
    
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Upload {self.original_filename}>'


class Notification(db.Model):
    """Notification model for payment and delivery updates"""
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Notification details
    type = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    
    # Related entities
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    transaction_id = db.Column(db.Integer, db.ForeignKey('transactions.id'))
    
    # Status
    is_read = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='notifications')
    project = db.relationship('Project', backref='notifications')
    
    def __repr__(self):
        return f'<Notification {self.id}: {self.type}>'
