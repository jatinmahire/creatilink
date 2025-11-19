"""
Seed script to populate database with sample data
Run this script after database initialization
"""

from app import create_app, db
from app.models import User, Project, Application, Package, Review, Transaction
from datetime import datetime, timedelta
import random

def seed_database():
    """Populate database with sample data"""
    app = create_app()
    
    with app.app_context():
        print("Clearing existing data...")
        db.drop_all()
        db.create_all()
        
        print("Creating admin user...")
        admin = User(
            full_name="Admin User",
            email="admin@creatilink.com",
            role="customer",
            is_admin=True
        )
        admin.set_password("admin123")
        db.session.add(admin)
        
        print("Creating sample customers...")
        customers = []
        customer_data = [
            ("John Smith", "john@example.com"),
            ("Sarah Johnson", "sarah@example.com"),
            ("Mike Davis", "mike@example.com"),
        ]
        
        for name, email in customer_data:
            customer = User(
                full_name=name,
                email=email,
                role="customer"
            )
            customer.set_password("password123")
            customers.append(customer)
            db.session.add(customer)
        
        print("Creating sample creators...")
        creators = []
        creator_data = [
            ("Emma Wilson", "emma@example.com", "graphic_design", "Professional graphic designer with 5+ years experience", "Photoshop, Illustrator, InDesign", 4.8),
            ("David Brown", "david@example.com", "video_editing", "Expert video editor specializing in commercial content", "Premiere Pro, After Effects, DaVinci Resolve", 4.9),
            ("Lisa Garcia", "lisa@example.com", "photography", "Wedding and event photographer", "Canon, Adobe Lightroom, Portrait Photography", 4.7),
            ("James Taylor", "james@example.com", "videography", "Cinematic videographer for brands and events", "RED Camera, DJI Drone, Color Grading", 4.6),
            ("Sophie Anderson", "sophie@example.com", "graphic_design", "Brand identity designer and illustrator", "Figma, Procreate, Branding", 4.5),
            ("Alex Martinez", "alex@example.com", "video_editing", "YouTube content editor and motion designer", "Final Cut Pro, Motion Graphics, Thumbnails", 4.8),
        ]
        
        for name, email, domain, bio, skills, rating in creator_data:
            creator = User(
                full_name=name,
                email=email,
                role="creator",
                domain=domain,
                bio=bio,
                skills=skills,
                rating=rating,
                total_reviews=random.randint(5, 25)
            )
            creator.set_password("password123")
            creators.append(creator)
            db.session.add(creator)
        
        db.session.commit()
        print(f"Created {len(customers)} customers and {len(creators)} creators")
        
        print("Creating sample packages...")
        package_data = [
            ("Basic Logo Design", "Simple logo with 2 concepts", "basic", 150, 3, 2),
            ("Standard Logo Package", "Logo + brand colors + 3 revisions", "standard", 350, 5, 3),
            ("Premium Branding", "Complete brand identity package", "premium", 800, 10, 5),
        ]
        
        for creator in creators[:2]:  # Add packages for first 2 creators
            for title, desc, tier, price, days, revisions in package_data:
                package = Package(
                    creator_id=creator.id,
                    title=title,
                    description=desc,
                    tier=tier,
                    price=price,
                    delivery_days=days,
                    revisions=revisions,
                    is_active=True
                )
                db.session.add(package)
        
        db.session.commit()
        print("Created sample packages")
        
        print("Creating sample projects...")
        project_data = [
            ("Logo Design for Tech Startup", "Need a modern, minimalist logo for a SaaS company", "graphic_design", 500, 'open'),
            ("Wedding Video Editing", "Edit 4 hours of wedding footage into a 10-minute highlight reel", "video_editing", 800, 'open'),
            ("Product Photography", "Need 20 professional photos of our new product line", "photography", 600, 'open'),
            ("Company Promotional Video", "Create a 2-minute promotional video for our services", "videography", 1200, 'open'),
            ("Social Media Graphics", "Design 10 Instagram posts for our campaign", "graphic_design", 300, 'assigned'),
            ("YouTube Video Editing", "Edit weekly vlog content (30 minutes of footage)", "video_editing", 200, 'in_progress'),
        ]
        
        projects = []
        for i, (title, desc,category, budget, status) in enumerate(project_data):
            project = Project(
                title=title,
                description=desc,
                category=category,
                budget=budget,
                status=status,
                posted_by_id=customers[i % len(customers)].id,
                deadline=(datetime.now() + timedelta(days=random.randint(7, 30))).date()
            )
            
            # Assign creator to some projects
            if status in ['assigned', 'in_progress', 'completed']:
                project.assigned_to_id = creators[i % len(creators)].id
            
            if status == 'completed':
                project.completed_at = datetime.now() - timedelta(days=random.randint(1, 10))
            
            projects.append(project)
            db.session.add(project)
        
        db.session.commit()
        print(f"Created {len(projects)} projects")
        
        print("Creating sample applications...")
        for project in projects[:4]:  # First 4 open projects
            for creator in random.sample(creators, 3):  # 3 random creators apply
                application = Application(
                    project_id=project.id,
                    creator_id=creator.id,
                    quote=project.budget * random.uniform(0.8, 1.2),
                    message=f"I'd love to work on this project. I have experience in {creator.domain}.",
                    delivery_days=random.randint(3, 14),
                    status='pending'
                )
                db.session.add(application)
        
        db.session.commit()
        print("Created sample applications")
        
        print("Creating sample reviews...")
        completed_projects = [p for p in projects if p.status == 'completed']
        for project in completed_projects:
            review = Review(
                project_id=project.id,
                reviewer_id=project.posted_by_id,
                creator_id=project.assigned_to_id,
                rating=random.randint(4, 5),
                comment="Great work! Very professional and delivered on time."
            )
            db.session.add(review)
        
        db.session.commit()
        print("Created sample reviews")
        
        print("Creating sample transactions...")
        for project in projects:
            if project.status in ['in_progress', 'completed']:
                transaction = Transaction(
                    project_id=project.id,
                    customer_id=project.posted_by_id,
                    creator_id=project.assigned_to_id,
                    amount=project.budget,
                    type='full',
                    status='completed' if project.status == 'completed' else 'pending',
                    completed_at=datetime.now() if project.status == 'completed' else None
                )
                db.session.add(transaction)
        
        db.session.commit()
        print("Created sample transactions")
        
        print("\n" + "="*50)
        print("Database seeded successfully!")
        print("="*50)
        print("\nTest Accounts:")
        print("-" * 50)
        print("\nAdmin:")
        print("  Email: admin@creatilink.com")
        print("  Password: admin123")
        print("\nCustomers:")
        for name, email in customer_data:
            print(f"  {name}: {email} / password123")
        print("\nCreators:")
        for name, email, domain, _, _, _ in creator_data:
            print(f"  {name} ({domain}): {email} / password123")
        print("\n" + "="*50)


if __name__ == '__main__':
    seed_database()
