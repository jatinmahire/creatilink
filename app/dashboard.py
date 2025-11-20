from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import func
from datetime import datetime, timedelta
from app.models import Project, Application, Transaction, User, Message

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/customer')
@login_required
def customer_dashboard():
    """Customer dashboard"""
    if current_user.role != 'customer':
        flash('Access denied.', 'warning')
        return redirect(url_for('main.index'))
    
    from app import db
    
    # Posted projects
    projects = Project.query.filter_by(posted_by_id=current_user.id).order_by(Project.created_at.desc()).all()
    
    # Statistics
    total_projects = len(projects)
    active_projects = len([p for p in projects if p.status in ['open', 'assigned', 'in_progress']])
    completed_projects = len([p for p in projects if p.status == 'completed'])
    
    # Total spent
    total_spent = db.session.query(func.sum(Transaction.amount)).filter_by(
        customer_id=current_user.id,
        status='completed'
    ).scalar() or 0
    
    # Recent transactions
    recent_transactions = Transaction.query.filter_by(customer_id=current_user.id).order_by(Transaction.created_at.desc()).limit(5).all()
    
    return render_template(
        'dashboard/customer.html',
        projects=projects,
        total_projects=total_projects,
        active_projects=active_projects,
        completed_projects=completed_projects,
        total_spent=total_spent,
        recent_transactions=recent_transactions
    )


@dashboard_bp.route('/creator')
@login_required
def creator_dashboard():
    """Creator dashboard"""
    if current_user.role != 'creator':
        flash('Access denied.', 'warning')
        return redirect(url_for('main.index'))
    
    from app import db
    
    # Active jobs (assigned to me)
    active_jobs = Project.query.filter_by(assigned_to_id=current_user.id).filter(
        Project.status.in_(['assigned', 'in_progress'])
    ).all()
    
    # My applications
    applications = Application.query.filter_by(creator_id=current_user.id).order_by(Application.created_at.desc()).limit(10).all()
    
    # Statistics
    completed_jobs = Project.query.filter_by(
        assigned_to_id=current_user.id,
        status='completed'
    ).count()
    
    pending_applications = Application.query.filter_by(
        creator_id=current_user.id,
        status='pending'
    ).count()
    
    # Total earnings
    total_earnings = db.session.query(func.sum(Transaction.amount)).filter_by(
        creator_id=current_user.id,
        status='completed'
    ).scalar() or 0
    
    # Recent earnings
    recent_earnings = Transaction.query.filter_by(
        creator_id=current_user.id,
        status='completed'
    ).order_by(Transaction.created_at.desc()).limit(5).all()
    
    # Unread messages count
    unread_messages = 0
    for job in active_jobs:
        unread = Message.query.filter_by(
            project_id=job.id,
            is_read=False
        ).filter(Message.sender_id != current_user.id).count()
        unread_messages += unread
    
    return render_template(
        'dashboard/creator.html',
        active_jobs=active_jobs,
        applications=applications,
        completed_jobs=completed_jobs,
        pending_applications=pending_applications,
        total_earnings=total_earnings,
        recent_earnings=recent_earnings,
        unread_messages=unread_messages
    )
