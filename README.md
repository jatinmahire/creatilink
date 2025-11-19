# CreatiLink - Visual Media Marketplace

A comprehensive marketplace platform connecting customers with creative professionals including graphic designers, video editors, photographers, and videographers.

## Features

- **User Authentication**: Separate roles for customers and creators
- **Project Management**: Post projects, receive applications, assign creators
- **Real-time Chat**: Project-based messaging with SocketIO
- **Secure Payments**: Stripe integration for transactions
- **Reviews & Ratings**: Customer feedback system for creators
- **Creator Portfolios**: Showcase work and service packages
- **Admin Panel**: Platform management and analytics
- **Responsive Design**: Modern UI with Tailwind CSS

## Tech Stack

- **Backend**: Flask (Python 3.10+)
- **Database**: SQLite (dev) / PostgreSQL (production)
- **Real-time**: Flask-SocketIO with eventlet
- **Payments**: Stripe
- **Frontend**: HTML, Tailwind CSS, Vanilla JavaScript
- **Authentication**: Flask-Login
- **File Uploads**: Local storage (easily upgradable to S3)

## Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Virtual environment tool (venv or virtualenv)

## Installation

### 1. Clone or Extract the Project

Navigate to the project directory:
```bash
cd "d:/code/New folder (2)"
```

### 2. Create Virtual Environment

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**On Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Copy the example environment file:
```bash
copy .env.example .env   # Windows
# OR
cp .env.example .env     # Linux/Mac
```

Edit `.env` and configure:
```env
SECRET_KEY=your-very-secret-key-here-change-this
DATABASE_URL=sqlite:///creatilink.db
STRIPE_PUBLIC_KEY=pk_test_your_stripe_public_key
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
```

**Getting Stripe Keys** (for payment testing):
1. Go to https://dashboard.stripe.com/register
2. Create an account (use test mode)
3. Get your test API keys from https://dashboard.stripe.com/test/apikeys
4. Add them to your `.env` file

### 5. Initialize Database

The database will be created automatically on first run. To populate with sample data:

```bash
python seed.py
```

This creates:
- Admin user
- 3 sample customers
- 6 sample creators (across all categories)
- Sample projects in various states
- Applications, reviews, and transactions

### 6. Run the Application

```bash
python manage.py
```

The application will start on `http://localhost:5000`

## Test Accounts

After running `seed.py`, you can login with:

**Admin:**
- Email: `admin@creatilink.com`
- Password: `admin123`

**Sample Customer:**
- Email: `john@example.com`
- Password: `password123`

**Sample Creator:**
- Email: `emma@example.com` (Graphic Designer)
- Password: `password123`

More test accounts are listed in the seed script output.

## Project Structure

```
creatilink/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── models.py            # Database models
│   ├── auth.py              # Authentication routes
│   ├── main.py              # Main/landing page routes
│   ├── projects.py          # Project management routes
│   ├── chat.py              # Chat routes
│   ├── payments.py          # Payment integration
│   ├── dashboard.py         # User dashboards
│   ├── admin.py             # Admin panel
│   ├── socket_events.py     # SocketIO events
│   ├── templates/           # HTML templates
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── auth/           # Auth templates
│   │   ├── projects/       # Project templates
│   │   ├── dashboard/      # Dashboard templates
│   │   ├── chat/           # Chat templates
│   │   ├── payments/       # Payment templates
│   │   └── admin/          # Admin templates
│   └── static/
│       ├── css/
│       │   └── custom.css
│       ├── js/
│       │   ├── main.js
│       │   └── chat.js
│       └── uploads/        # User uploaded files
├── config.py                # Configuration
├── manage.py                # Application entry point
├── seed.py                  # Database seeding script
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
└── README.md               # This file
```

## Main User Flows

### For Customers:
1. Sign up as customer
2. Post a project (title, description, budget, deadline)
3. Review creator applications
4. Assign a creator
5. Chat and collaborate
6. Make payment via Stripe
7. Mark project complete
8. Leave review

### For Creators:
1. Sign up as creator
2. Complete profile setup (portfolio, skills, packages)
3. Browse open projects
4. Apply with quote and proposal
5. Get assigned by customer
6. Chat with customer
7. Receive payment
8. Get reviewed

## Stripe Payment Testing

Use these test card numbers in Stripe checkout:

- **Success**: `4242 4242 4242 4242`
- **Decline**: `4000 0000 0000 0002`
- **3D Secure**: `4000 0027 6000 3184`

Use any future expiry date, any 3-digit CVC, and any postal code.

## Development Notes

### Adding Static Files

Place CSS files in `app/static/css/`
Place JS files in `app/static/js/`
Place images in `app/static/images/`

### Database Migrations

When you modify models:

```bash
flask db init        # First time only
flask db migrate -m "Description of changes"
flask db upgrade
```

### Upload Folder

User uploads are stored in `app/static/uploads/`. For production, configure S3 or similar cloud storage.

### Switching to PostgreSQL

Update `.env`:
```env
DATABASE_URL=postgresql://username:password@localhost/creatilink
```

Install psycopg2:
```bash
pip install psycopg2-binary
```

## Docker Deployment (Optional)

### Build and Run

```bash
docker build -t creatilink .
docker run -p 5000:5000 --env-file .env creatilink
```

### Using Docker Compose

```bash
docker-compose up
```

This starts the Flask app and (optionally) PostgreSQL.

## Production Deployment

### Important Security Steps:

1. **Change SECRET_KEY** to a random string
2. **Use PostgreSQL** instead of SQLite
3. **Enable HTTPS** (use nginx/Apache as reverse proxy)
4. **Use production Stripe keys**
5. **Set DEBUG=False** in config
6. **Use a production WSGI server** (gunicorn is included)

### Run with Gunicorn:

```bash
gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5000 "app:create_app()"
```

## Troubleshooting

### Port Already in Use

Change the port in `manage.py`:
```python
socketio.run(app, port=5001)  # Use different port
```

### Module Not Found

Ensure virtual environment is activated and dependencies installed:
```bash
pip install -r requirements.txt
```

### Database Errors

Delete the database and recreate:
```bash
rm creatilink.db  # Delete old database
python seed.py    # Recreate and seed
```

### SocketIO Not Working

Ensure eventlet is installed:
```bash
pip install eventlet
```

## API Endpoints

### Authentication
- `POST /auth/signup` - User registration
- `POST /auth/login` - User login
- `GET /auth/logout` - User logout

### Projects
- `GET /projects` - List projects (with filters)
- `POST /projects/create` - Create project
- `GET /projects/<id>` - Project details
- `POST /projects/<id>/apply` - Apply to project
- `POST /projects/<id>/assign` - Assign creator

### Chat
- `GET /chat/<project_id>` - Chat room
- SocketIO events: `join_room`, `send_message`, `typing`

### Payments
- `POST /payment/create` - Create Stripe checkout
- `GET /payment/success` - Payment callback

## Contributing

This is an MVP. Potential improvements:

- Email notifications
- File transcoding for videos
- Advanced search/filters
- Message read receipts
- Escrow milestone payments
- Creator availability calendar
- Multi-language support

## License

MIT License - feel free to use for your projects!

## Support

For issues or questions:
- Check the code comments
- Review Flask documentation: https://flask.palletsprojects.com/
- Review Stripe documentation: https://stripe.com/docs

---

**Built with ❤️ using Flask and Tailwind CSS**
