# Update dashboard.py to filter deleted projects
with open('app/dashboard.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace customer projects query
old_customer = "projects = Project.query.filter_by(posted_by_id=current_user.id).order_by(Project.created_at.desc()).all()"
new_customer = """projects = Project.query.filter_by(posted_by_id=current_user.id).filter(
        Project.deleted_at == None
    ).order_by(Project.created_at.desc()).all()"""
content = content.replace(old_customer, new_customer)

# Replace creator active jobs query
old_creator = """active_jobs = Project.query.filter_by(assigned_to_id=current_user.id).filter(
        Project.status.in_(['assigned', 'in_progress', 'delivered'])
    ).all()"""
new_creator = """active_jobs = Project.query.filter_by(assigned_to_id=current_user.id).filter(
        Project.status.in_(['assigned', 'in_progress', 'delivered']),
        Project.deleted_at == None,
        Project.creator_left == False
    ).all()"""
content = content.replace(old_creator, new_creator)

# Replace completed jobs query
old_completed = """completed_jobs = Project.query.filter_by(
        assigned_to_id=current_user.id,
        status='completed'
    ).count()"""
new_completed = """completed_jobs = Project.query.filter_by(
        assigned_to_id=current_user.id,
        status='completed'
    ).filter(
        Project.deleted_at == None
    ).count()"""
content = content.replace(old_completed, new_completed)

with open('app/dashboard.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Updated dashboard.py to filter deleted projects")
