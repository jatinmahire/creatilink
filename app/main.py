from flask import Blueprint, render_template
from app.models import User, Project
from sqlalchemy import func

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Landing page"""
    # Get featured creators (top rated)
    featured_creators = User.query.filter_by(
        role='creator',
        is_active=True
    ).order_by(User.rating.desc()).limit(6).all()
    
    # Get recent projects
    recent_projects = Project.query.filter_by(
        status='open'
    ).order_by(Project.created_at.desc()).limit(6).all()
    
    # Category stats
    categories = ['graphic_design', 'video_editing', 'photography', 'videography']
    category_stats = {}
    for cat in categories:
        count = User.query.filter_by(role='creator', domain=cat, is_active=True).count()
        category_stats[cat] = count
    
    return render_template(
        'index.html',
        featured_creators=featured_creators,
        recent_projects=recent_projects,
        category_stats=category_stats
    )


@main_bp.route('/about')
def about():
    """About page"""
    return render_template('about.html')


@main_bp.route('/how-it-works')
def how_it_works():
    """How it works page"""
    return render_template('how_it_works.html')
