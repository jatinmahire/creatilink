# 🚀 Easiest Way to Host CreatiLink on Render.com

We have set up your project with a **Render Blueprint** (`render.yaml`). This allows you to deploy the entire application (Database + Web Server) in just a few clicks.

## Step 1: Push Code to GitHub
(If you haven't already)

1.  Create a new repository on [GitHub](https://github.com/new) named `creatilink`.
2.  Run these commands in your terminal:
    ```bash
    git remote add origin https://github.com/YOUR_USERNAME/creatilink.git
    git branch -M main
    git push -u origin main
    ```

## Step 2: Deploy on Render

1.  Go to [dashboard.render.com](https://dashboard.render.com/).
2.  Click **New +** and select **Blueprint**.
3.  Connect your GitHub account and select the `creatilink` repository.
4.  Give it a name (e.g., `creatilink-production`).
5.  Click **Apply**.

Render will automatically:
*   Create a PostgreSQL Database.
*   Create the Web Service.
*   Link them together.
*   Deploy your code.

## Step 3: Final Setup (One-time)

Once the deployment is finished (green "Live" badge):

1.  Go to the **Shell** tab of your new Web Service in Render.
2.  Run this command to set up the admin user and data:
    ```bash
    python seed.py
    ```

## 🎉 That's it!
Your website is now live!
