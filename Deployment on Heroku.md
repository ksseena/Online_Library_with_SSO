# Django Library Management System

This is a **Django-based Library Management System** that allows users to manage books, track borrowing, and authenticate using **Auth0 SSO**. This guide provides instructions for deploying the application on **Heroku**.

---

## 🚀 **Deployment on Heroku**

### **1️⃣ Prerequisites**
- [Sign up for a Heroku account](https://signup.heroku.com/)
- [Install Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
- [Install Git](https://git-scm.com/downloads)
- [Install PostgreSQL](https://www.postgresql.org/download/) (Optional, for local development)

---

### **2️⃣ Install Required Packages**
Inside your Django project, install these dependencies:
```sh
pip install gunicorn psycopg2-binary whitenoise
```
- `gunicorn` - Runs Django on Heroku.
- `psycopg2-binary` - PostgreSQL adapter.
- `whitenoise` - Manages static files in production.

---

### **3️⃣ Configure `settings.py` for Production**
#### 📌 Update `ALLOWED_HOSTS`
```python
import os

ALLOWED_HOSTS = ["your-heroku-app-name.herokuapp.com"]
```
#### 📌 Configure Static Files for Whitenoise
```python
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # Add this line
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
```
At the **bottom** of `settings.py`, add:
```python
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
```

---

### **4️⃣ Prepare for Heroku Deployment**
#### 📌 Create a `Procfile`
Inside your project root, create a file named `Procfile` (without any extension):
```sh
echo "web: gunicorn library_management.wsgi --log-file -" > Procfile
```
#### 📌 Create a `.gitignore` file
```sh
echo -e "venv/\n*.pyc\n__pycache__/\ndb.sqlite3\n.env" > .gitignore
```

---

### **5️⃣ Push Code to GitHub**
```sh
git init
git add .
git commit -m "Initial commit for Heroku deployment"
git branch -M main
git remote add origin https://github.com/yourusername/library_management.git
git push -u origin main
```

---

### **6️⃣ Deploy to Heroku**
#### 📌 Login to Heroku
```sh
heroku login
```
#### 📌 Create a New Heroku App
```sh
heroku create your-heroku-app-name
```
#### 📌 Add Heroku PostgreSQL (Database)
```sh
heroku addons:create heroku-postgresql:hobby-dev
```
Get database URL:
```sh
heroku config
```
#### 📌 Set Up Django Environment Variables
```sh
heroku config:set SECRET_KEY="your-secret-key"
heroku config:set DEBUG=False
heroku config:set DJANGO_SETTINGS_MODULE=library_management.settings
```
#### 📌 Push Code to Heroku
```sh
git push heroku main
```
#### 📌 Run Migrations on Heroku
```sh
heroku run python manage.py migrate
```
#### 📌 Collect Static Files
```sh
heroku run python manage.py collectstatic --noinput
```

---

### **7️⃣ Open the Application**
```sh
heroku open
```
Your Django **Library Management System** is now **LIVE**! 🎉

---

## ✅ **Additional Steps**

#### 📌 Add a Custom Domain
```sh
heroku domains:add yourdomain.com
```
Set up **CNAME** records in your DNS provider.

#### 📌 Monitor Logs
```sh
heroku logs --tail
```

#### 📌 Restart the App
```sh
heroku restart
```

Let me know if you need any help! 🚀

