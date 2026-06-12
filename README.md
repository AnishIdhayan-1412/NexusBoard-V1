# ⬡ NexusBoard — Social Community Platform

> A production-ready Django social platform. Build communities, share posts, vote, and discuss. Think Reddit, built by you.

---

## 🚀 Quick Start (Run Locally in 3 Steps)

```bash
# 1. Clone and enter the project
git clone https://github.com/YOUR_USERNAME/nexusboard.git
cd nexusboard

# 2. Set up Python environment
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Set up database and run
cp .env.example .env              # Copy environment config
python manage.py migrate          # Create database tables
python manage.py seed_data        # Load sample data
python manage.py runserver        # Start server
```

Open http://127.0.0.1:8000 — you're live!

**Test accounts:**
| Username | Password | Role |
|----------|----------|------|
| `admin` | `adminpass123` | Superuser |
| `user1` | `testpass123` | Regular user |
| `user2` | `testpass123` | Regular user |

Admin panel: http://127.0.0.1:8000/admin

---

## 🐳 Run with Docker (Recommended)

```bash
# Build and start everything
docker compose up --build

# In another terminal, seed data
docker compose exec web python manage.py seed_data
```

Visit http://localhost:8000

---

## ✨ Features

- **Communities** — Create and join communities (like subreddits)
- **Posts** — Text, link, and image posts
- **Voting** — Upvote/downvote posts with AJAX (no page reload)
- **Comments** — Nested threaded comments with replies
- **User Profiles** — Avatar, bio, follow/unfollow
- **Search** — Search posts and communities
- **Admin Panel** — Full Django admin for moderation
- **Health Check** — `/health/` endpoint for monitoring
- **Logging** — Rotating file logs in `logs/nexusboard.log`

---

## 🏗️ Project Structure

```
nexusboard/
├── accounts/          # User auth, profiles, follow system
├── communities/       # Communities, memberships
├── posts/             # Posts, comments, voting
├── core/              # Home, search, health check
├── templates/         # All HTML templates
├── static/            # CSS, JS, images
├── logs/              # Application logs (auto-created)
├── media/             # User uploads (auto-created)
├── Dockerfile         # Production Docker build
├── docker-compose.yml # Local development with PostgreSQL
├── railway.toml       # Deploy to Railway (free)
├── render.yaml        # Deploy to Render (free)
├── entrypoint.sh      # Production startup script
├── requirements.txt   # Python dependencies
└── .env.example       # Environment variable template
```

---

## 🌍 Deploy for Free (Step by Step)

### Option A: Railway (Recommended — Easiest)

1. Push your code to GitHub
2. Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub
3. Select your `nexusboard` repo
4. Railway auto-detects the `Dockerfile`
5. Add environment variables:
   ```
   SECRET_KEY=<generate a 50-char random string>
   DEBUG=False
   ALLOWED_HOSTS=.railway.app
   DATABASE_URL=<Railway provides this automatically with PostgreSQL plugin>
   ```
6. Add PostgreSQL: In Railway dashboard → New → Database → PostgreSQL
7. It auto-injects `DATABASE_URL` into your app
8. Your app is live at `https://nexusboard-xxx.railway.app` 🎉

### Option B: Render (Also Free)

1. Push to GitHub
2. Go to [render.com](https://render.com) → New → Web Service
3. Connect your GitHub repo
4. Render reads `render.yaml` automatically
5. Set environment variables (same as Railway)
6. Deploy!

### Environment Variables for Production

```env
DEBUG=False
SECRET_KEY=your-50-char-secret-key-generate-with-python-secrets
ALLOWED_HOSTS=.railway.app,.onrender.com,yourdomain.com
DATABASE_URL=postgres://user:pass@host:5432/dbname
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_PASSWORD=your-secure-password
DJANGO_SUPERUSER_EMAIL=admin@yourdomain.com
```

---

## 📊 Monitoring & Logs (DevOps Skills)

### View logs locally
```bash
tail -f logs/nexusboard.log          # Follow real-time logs
cat logs/nexusboard.log | grep ERROR # Filter errors only
```

### Docker logs
```bash
docker compose logs -f web           # Follow web container logs
docker compose logs -f --tail=50     # Last 50 lines all services
```

### Railway / Render logs
- Railway: Dashboard → your service → Logs tab (real-time streaming)
- Render: Dashboard → your service → Logs

### Health check endpoint
```bash
curl https://your-app.railway.app/health/
# Returns: {"status": "healthy", "django_version": [...], "app": "NexusBoard"}
```

### What to monitor
| Metric | Where to find it |
|--------|-----------------|
| App errors | `logs/nexusboard.log` or Railway Logs |
| DB connections | Django admin → check if admin loads |
| Response time | Railway metrics dashboard |
| Memory/CPU | Railway / Render resource graphs |

---

## 🔧 Development Commands

```bash
# Create migrations after model changes
python manage.py makemigrations
python manage.py migrate

# Reload sample data (won't duplicate)
python manage.py seed_data

# Open Django shell
python manage.py shell

# Collect static files
python manage.py collectstatic

# Run tests (add your own in tests.py!)
python manage.py test

# Generate a secret key
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

---

## 🧪 Adding Your Own Features (Next Steps)

| Feature | Where to add |
|---------|-------------|
| Notifications | New `notifications` app |
| Tags on posts | Add `tags` M2M to Post model |
| Post bookmarks | Add to accounts/models.py |
| Dark/light mode toggle | JS in base.html |
| Email notifications | Celery + Redis + Django email |
| Image CDN | Replace local media with Cloudinary |

---

## 🐛 Troubleshooting

| Problem | Fix |
|---------|-----|
| `No module named django` | Run `pip install -r requirements.txt` in venv |
| `ALLOWED_HOSTS` error | Add your domain to `ALLOWED_HOSTS` in `.env` |
| Static files 404 in prod | Run `python manage.py collectstatic` |
| Media files not showing | Check `MEDIA_URL` and `MEDIA_ROOT` in settings |
| DB connection error | Check `DATABASE_URL` in `.env` |
| Port already in use | `python manage.py runserver 8001` |

---

## 🔐 Security Checklist (Before Going Live)

- [ ] `DEBUG=False` in production
- [ ] Strong `SECRET_KEY` (50+ chars, never share it)
- [ ] `ALLOWED_HOSTS` set to your actual domain only
- [ ] HTTPS enforced (Railway/Render do this automatically)
- [ ] Admin URL changed (optional: `path('secret-admin/', admin.site.urls)`)
- [ ] Regular database backups enabled (Railway has this built-in)

---

Built with ❤️ using Django 5 · Bootstrap 5 · SQLite/PostgreSQL · Docker
