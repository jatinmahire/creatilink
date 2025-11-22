# 🆓 Deploy CreatiLink on Render.com - FREE (No Credit Card Required)

## ✅ Your Code is Ready!
Repository: https://github.com/jatinmahire/creatilink.git

---

## 🚀 Free Deployment Steps

### Step 1: Sign Up on Render (FREE)

1. Go to [render.com](https://render.com/)
2. Click **"Get Started for Free"**
3. Sign up using your **GitHub account** (easiest method)
4. NO credit card required for the free tier! ✅

---

### Step 2: Create PostgreSQL Database (FREE)

1. In Render Dashboard, click **"New +"** at the top right
2. Select **"PostgreSQL"**
3. Fill in:
   - **Name**: `creatilink-db`
   - **Database**: `creatilink`
   - **User**: `creatilink_user`
   - **Region**: Pick closest to you (e.g., **Singapore** or **Frankfurt**)
   - **Instance Type**: Select **"Free"** ⭐
4. Click **"Create Database"**
5. Wait for it to show "Available" (takes ~1 minute)
6. **IMPORTANT**: Click on the database name, then copy the **"Internal Database URL"** 
   - It looks like: `postgres://creatilink_user:xxxxx@dpg-xxxxx/creatilink`
   - Keep this URL safe for Step 3!

---

### Step 3: Create Web Service (FREE)

1. Click **"New +"** again
2. Select **"Web Service"**
3. Click **"Connect a repository"** → Select **"GitHub"**
4. Find and select your **`creatilink`** repository
5. Fill in the settings:

   **Basic Settings:**
   - **Name**: `creatilink-app` (or any name you like)
   - **Region**: Same as your database (e.g., Singapore)
   - **Branch**: `main`
   - **Root Directory**: Leave blank
   - **Runtime**: **Python 3**
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --worker-class eventlet -w 1 manage:app`

   **Instance Type:**
   - Select **"Free"** ⭐ (512 MB RAM, spins down after inactivity)

6. Scroll down to **"Environment Variables"** and click **"Add Environment Variable"**
7. Add these variables one by one:

   | Key | Value |
   |-----|-------|
   | `PYTHON_VERSION` | `3.10.11` |
   | `FLASK_ENV` | `production` |
   | `SECRET_KEY` | Any random text (e.g., `mysecretkey12345abcdef`) |
   | `DATABASE_URL` | Paste the **Internal Database URL** from Step 2 |
   | `STRIPE_PUBLIC_KEY` | Leave blank for now (add later when needed) |
   | `STRIPE_SECRET_KEY` | Leave blank for now |

8. Click **"Create Web Service"**

---

### Step 4: Wait for Deployment (3-5 minutes)

Render will now:
- Install all Python packages
- Connect to the database
- Start your application

You'll see a build log. Wait until it shows **"Live"** with a green dot ✅

---

### Step 5: Initialize Database (One-time Setup)

1. Once your service shows **"Live"**, click on **"Shell"** tab in the left menu
2. A terminal will open. Type this command:
   ```bash
   python seed.py
   ```
3. Press Enter and wait for it to finish
4. You should see: `Database seeded successfully!`

---

## 🎉 Your Website is Now LIVE!

Your URL will be: `https://creatilink-app.onrender.com` (or whatever name you chose)

### 🔐 Login as Admin
- URL: `https://creatilink-app.onrender.com/auth/login`
- Email: `admin@creatilink.com`
- Password: `admin123`

---

## ⚠️ Free Tier Limitations

1. **Spins Down**: After 15 minutes of inactivity, the server sleeps. First visitor will wait ~30 seconds while it wakes up.
2. **750 Hours/Month**: Free tier gives you 750 hours per month (enough for one app running 24/7).
3. **No Credit Card**: 100% free, no surprises!

---

## 📝 Optional: Add Custom Domain (Later)

If you want a custom domain:
1. Buy a domain (e.g., from Namecheap, GoDaddy)
2. In Render, go to Settings → Custom Domain
3. Add your domain and follow the DNS instructions

---

## 🆘 Troubleshooting

**"Application Error" or 500 Error?**
- Click **"Logs"** tab in Render
- Check if database is connected
- Make sure you ran `python seed.py`

**Slow first load?**
- This is normal for free tier (server sleeps)
- Consider upgrading to paid tier later ($7/month for always-on)

---

## ✅ Checklist

- [x] Code pushed to GitHub
- [ ] PostgreSQL database created on Render (FREE)
- [ ] Web service created on Render (FREE)
- [ ] Database initialized with `python seed.py`
- [ ] Website accessible at Render URL

**You're all set! No credit card needed!** 🎉
