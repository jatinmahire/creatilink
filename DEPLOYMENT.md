# 🚀 Deployment Guide for CreatiLink

This guide covers how to deploy your Flask + SocketIO application to a live hosting environment.

## 📋 Prerequisites

1.  **GitHub Account**: Push your code to a GitHub repository.
2.  **Hosting Account**: We recommend **Render.com** or **Railway.app** as they support Python, PostgreSQL, and WebSockets (SocketIO) out of the box.

---

## 🛠️ Preparation Steps (Already Done)

We have already prepared your project for deployment:
1.  ✅ **`requirements.txt`**: Lists all dependencies (including `gunicorn` and `eventlet`).
2.  ✅ **`Procfile`**: Tells the server how to run your app (`gunicorn --worker-class eventlet ...`).
3.  ✅ **`config.py`**: Configured to read from environment variables.

---

## ☁️ Option 1: Deploy to Render.com (Recommended)

Render is excellent for this project because it offers a free tier for both the web service and PostgreSQL database, and handles WebSockets well.

### Step 1: Create Database
1.  Log in to [Render Dashboard](https://dashboard.render.com/).
2.  Click **New +** -> **PostgreSQL**.
3.  **Name**: `creatilink-db`
4.  **Region**: Choose one close to you (e.g., Singapore, Frankfurt).
5.  **Plan**: Free (for hobby projects) or Starter.
6.  Click **Create Database**.
7.  **Copy the "Internal Database URL"** (starts with `postgres://...`). You'll need this soon.

### Step 2: Create Web Service
1.  Click **New +** -> **Web Service**.
2.  Connect your GitHub repository.
3.  **Name**: `creatilink-app`
4.  **Runtime**: Python 3
5.  **Build Command**: `pip install -r requirements.txt`
6.  **Start Command**: `gunicorn --worker-class eventlet -w 1 manage:app`
7.  **Plan**: Free or Starter.

### Step 3: Environment Variables
Scroll down to "Environment Variables" and add these:

| Key | Value |
| :--- | :--- |
| `PYTHON_VERSION` | `3.10.0` (or your local version) |
| `FLASK_APP` | `manage.py` |
| `FLASK_ENV` | `production` |
| `SECRET_KEY` | Generate a random string (e.g., `openssl rand -hex 32`) |
| `DATABASE_URL` | Paste the **Internal Database URL** from Step 1 |
| `STRIPE_PUBLIC_KEY` | Your Stripe Public Key (`pk_test_...`) |
| `STRIPE_SECRET_KEY` | Your Stripe Secret Key (`sk_test_...`) |
| `STRIPE_WEBHOOK_SECRET`| Your Stripe Webhook Secret |

### Step 4: Deploy
1.  Click **Create Web Service**.
2.  Render will start building your app. This takes a few minutes.
3.  Once you see "Live", your app is online!

---

## 🐳 Option 2: Deploy with Docker

If you have a VPS (like DigitalOcean Droplet or AWS EC2), you can use Docker.

### Step 1: Build & Run
On your server, run:

```bash
# 1. Clone your repo
git clone https://github.com/yourusername/creatilink.git
cd creatilink

# 2. Create .env file with production values
nano .env
# (Paste contents from .env.example and update values)

# 3. Build and Run
docker-compose up -d --build
```

### Step 2: Database Migration
Initialize the database inside the container:

```bash
docker-compose exec web python manage.py db upgrade
# OR to seed initial data:
docker-compose exec web python seed.py
```

---

## ⚙️ Post-Deployment Tasks

### 1. Initialize the Database
After your app is live on Render/Railway, you need to create the tables.

**On Render:**
1.  Go to your Web Service dashboard.
2.  Click **Shell** (on the left).
3.  Run this Python script to create tables:
    ```bash
    python seed.py
    ```
    *(Note: This will create the admin user and sample data)*

### 2. Configure Stripe Webhooks
1.  Go to your [Stripe Dashboard](https://dashboard.stripe.com/webhooks).
2.  Add Endpoint: `https://your-app-name.onrender.com/payment/webhook`
3.  Select events: `checkout.session.completed`
4.  Copy the **Signing Secret** and update your `STRIPE_WEBHOOK_SECRET` env var in Render.

---

## 🛡️ Production Checklist

- [ ] **SECRET_KEY**: Ensure it's a long, random string.
- [ ] **Debug Mode**: Ensure `FLASK_ENV` is set to `production` (disables debug mode).
- [ ] **HTTPS**: Render/Railway handle SSL automatically (✅).
- [ ] **Database**: Use PostgreSQL, not SQLite (✅ config.py handles this).
- [ ] **Stripe Keys**: Use live keys for real payments, test keys for testing.

## 🆘 Troubleshooting

**"Method Not Allowed" / 400 Bad Request on SocketIO:**
- Ensure you are using `gunicorn --worker-class eventlet`. Standard workers don't support WebSockets well.

**Database Errors:**
- Check `DATABASE_URL` is correct.
- Ensure you ran `python seed.py` or `flask db upgrade` to create tables.

**Static Files Not Loading:**
- Flask serves static files automatically, but for high traffic, consider using WhiteNoise or Nginx.
