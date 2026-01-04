<div align="center">
  <h1><img src="static/assets/qwitter-brand.svg" alt="Qwitter Brand" width="360"></h1>
  <p><strong>A Modern Twitter (X)-Inspired Social Platform</strong></p>
</div>

<br>

Qwitter is a thoughtfully engineered social networking platform inspired by Twitter (X), where users can share short text posts, interact through reposts and quotes, follow others, manage bookmarks, and personalize their experience with themes and settings.

This project represents a complete architectural refactor and feature consolidation, evolving Qwitter into a scalable, production-ready platform with both web and API support.

---

## 🌐 Live Demo

**🔗 Application:** https://qwitter.onrender.com

---

## 🚀 Key Features

### 🧑‍💻 Accounts & Profiles
- User registration and authentication
- Profile pages with bio, join date, and activity stats
- Follow / unfollow users
- View followers and following lists
- Account settings:
  - Change password
  - Change email
  - Change username
  - Deactivate account

### 📝 Posts & Interactions
- Create short text posts (up to 280 characters)
- Edit and delete your own posts
- Repost posts
- Quote posts with your own commentary
- Comment on posts
- Bookmark posts for later
- Pin posts to your profile
- View posts from users you follow

### 🎨 User Experience
- Light / Dark / System theme support
- Responsive layout for desktop and mobile
- Clean Bootstrap-based UI
- Toast-based feedback for actions (success, error, warnings)
- Graceful error handling with custom error pages

---

## 🔄 What's New in the Refactored Version

This version represents a complete architectural overhaul:

### Performance Improvements
- **Optimized database queries** — Reduced from 300+ queries to 1-3 per page load
- **Efficient data fetching** — Custom managers eliminate N+1 query problems
- **Fast feed loading** — Optimized queries for posts, user interactions, and counts

### Feature Enhancements
- **Proper repost/quote system** — Prevents circular references and duplicate reposts
- **Unified post model** — Supports original posts, reposts, and quotes seamlessly
- **Context-aware error pages** — User-friendly 404, 403, and 500 error handling
- **Smart interactions** — Prevents invalid actions (like reposting a repost)

### Infrastructure
- **Production-ready deployment** — Secure configuration with environment-based settings
- **Full REST API** — Complete API alongside the web interface for future expansion
- **Clean architecture** — Better separation of concerns and long-term maintainability

---

## 🛠️ Tech Stack

**Backend:**
- Django 5.1+
- Django REST Framework
- PostgreSQL (production) / SQLite (local)

**Frontend:**
- Django Templates
- Bootstrap 5
- JavaScript
- Jinja2

**Authentication:**
- Session Authentication
- JWT (Simple JWT)

**Deployment:**
- Render (web hosting)
- WhiteNoise (static file serving)

**API:**
- RESTful API with OpenAPI documentation
- JWT and session-based authentication

---

## ⚙️ Running Locally

```bash
# Clone the repository
git clone https://github.com/himanshuat/qwitter.git
cd qwitter

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create a superuser
python manage.py createsuperuser

# Start the development server
python manage.py runserver
```

Visit: http://127.0.0.1:8000/

---

## 🔧 Environment Setup

Create a `.env` file in the project root for local development:

```env
# Django Settings
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# Database (optional - uses SQLite by default in dev)
DATABASE_NAME=postgres
DATABASE_USER=your_db_user
DATABASE_PASSWORD=your_db_password
DATABASE_HOST=localhost
DATABASE_PORT=5432
```

For development, the default SQLite database works out of the box. PostgreSQL configuration is only needed for production-like environments.

---

## 🔮 Future Plans

- **Advanced search and discovery** — Find users and posts easily
- **Mobile application** — App for iOS and Android
- **Messaging** — Direct messages between users
- **Communities** — Topic-based groups and discussions
- **Notifications** — Real-time updates for interactions

---

**Qwitter is designed to grow — without losing simplicity.**