from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from functools import wraps
from sqlalchemy import func
from app import db
from app.models import User, Project, Transaction, Application, Review

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    """Decorator to require admin access"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('Access denied. Admin privileges required.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/')
@admin_required
def dashboard():
    """Admin dashboard"""
    # User statistics
    total_users = User.query.count()
    total_customers = User.query.filter_by(role='customer').count()
    total_creators = User.query.filter_by(role='creator').count()
    active_users = User.query.filter_by(is_active=True).count()
    
    # Project statistics
    total_projects = Project.query.count()
    open_projects = Project.query.filter_by(status='open').count()
    active_projects = Project.query.filter(Project.status.in_(['assigned', 'in_progress'])).count()
    completed_projects = Project.query.filter_by(status='completed').count()
    
    # Transaction statistics
    total_transactions = Transaction.query.filter_by(status='completed').count()
    total_revenue = db.session.query(func.sum(Transaction.amount)).filter_by(status='completed').scalar() or 0
    
    # Platform fee (assume 10%)
    platform_fee = total_revenue * 0.10
    
    # Recent users
    recent_users = User.query.order_by(User.created_at.desc()).limit(10).all()
    
    # Recent projects
    recent_projects = Project.query.order_by(Project.created_at.desc()).limit(10).all()
    
    # Recent transactions
    recent_transactions = Transaction.query.filter_by(status='completed').order_by(Transaction.created_at.desc()).limit(10).all()
    
    return render_template(
        'admin/dashboard.html',
        total_users=total_users,
        total_customers=total_customers,
        total_creators=total_creators,
        active_users=active_users,
        total_projects=total_projects,
        open_projects=open_projects,
        active_projects=active_projects,
        completed_projects=completed_projects,
        total_transactions=total_transactions,
        total_revenue=total_revenue,
        platform_fee=platform_fee,
        recent_users=recent_users,
        recent_projects=recent_projects,
        recent_transactions=recent_transactions
    )


@admin_bp.route('/users')
@admin_required
def users():
    """Manage users"""
    page = request.args.get('page', 1, type=int)
    role = request.args.get('role')
    search = request.args.get('search')
    
    query = User.query
    
    if role:
        query = query.filter_by(role=role)
    if search:
        query = query.filter(
            (User.full_name.ilike(f'%{search}%')) |
            (User.email.ilike(f'%{search}%'))
        )
    
    users = query.order_by(User.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    
    return render_template('admin/users.html', users=users)


@admin_bp.route('/users/<int:user_id>/toggle-status', methods=['POST'])
@admin_required
def toggle_user_status(user_id):
    """Ban or unban a user"""
    user = User.query.get_or_404(user_id)
    
    # Prevent self-ban
    if user.id == current_user.id:
        return jsonify({'error': 'Cannot ban yourself'}), 400
    
    # Prevent banning other admins
    if user.is_admin:
        return jsonify({'error': 'Cannot ban admin users'}), 400
    
    user.is_active = not user.is_active
    db.session.commit()
    
    status = 'activated' if user.is_active else 'deactivated'
    flash(f'User {user.full_name} has been {status}.', 'success')
    
    return jsonify({'success': True, 'is_active': user.is_active}), 200


@admin_bp.route('/projects')
@admin_required
def projects():
    """View all projects"""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status')
    
    query = Project.query
    
    if status:
        query = query.filter_by(status=status)
    
    projects = query.order_by(Project.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    
    return render_template('admin/projects.html', projects=projects)


@admin_bp.route('/transactions')
@admin_required
def transactions():
    """View all transactions"""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status')
    
    query = Transaction.query
    
    if status:
        query = query.filter_by(status=status)
    
    transactions = query.order_by(Transaction.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    
    return render_template('admin/transactions.html', transactions=transactions)
