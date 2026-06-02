# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

轻食刻 (Fresh & Vitality) — a health-oriented diet management full-stack web application. Users can record meals, track nutrition, get AI-personalized diet plans, and interact with a community.

## Commands

### Install dependencies
```bash
cd 轻饮食软件后端
pip install -r requirements.txt
```

### Initialize database (first run or reset)
```bash
cd 轻饮食软件后端
python init_db.py          # seed with sample data
python init_db.py --force  # reset database
```

### Start dev server
```bash
cd 轻饮食软件后端
python app.py
```
- Frontend: `http://localhost:5000`
- Admin panel: `http://localhost:5000/admin`

### Test accounts
| Role | Account ID | Password |
|------|-----------|----------|
| Admin | admin | admin123 |
| Test User | linyouxue | 123456 |

### Data import scripts
```bash
python import_howtocook.py   # import recipes from HowToCook repo
python import_images.py      # download recipe images from GitHub
```

## Architecture

**Monolithic full-stack app** — Flask backend serves both REST API and frontend static files from a single process. No build step, no bundler, no SPA framework.

### Backend (`轻饮食软件后端/`)
- **Entry point:** `app.py` — `create_app()` factory initializes Flask, SQLAlchemy, CORS, Flask-Login, registers 7 API blueprints, sets up Flask-Admin
- **Config:** `config.py` — SECRET_KEY, SQLite URI, upload settings (16MB max)
- **Models** (`models/`): 11 tables across 5 files — `user.py`, `food.py`, `diet.py`, `community.py`, `achievement.py`
- **Routes** (`routes/`): 7 blueprints under `/api/` — auth, user, diet, food, community, achievement, upload
- **Admin** (`admin/`): Flask-Admin with 9 model views, search/filter/export
- **Database:** SQLite stored at `instance/light_diet.db`

### Frontend (`轻饮食软件前端/`)
- Pure vanilla JS, multi-page architecture (each page is a standalone `.html`)
- **`js/api.js`** — centralized API client, all fetch calls to backend
- **`js/common.js`** — navigation, auth checks, shared utilities
- **`js/components.js`** — reusable SVG components (ring progress, bar chart, radar chart)
- Tailwind CSS + Material Symbols loaded via CDN
- Auth token stored in `localStorage` as `user_{id}` string

### API Blueprints
| Blueprint | Prefix | Purpose |
|-----------|--------|---------|
| auth | `/api/auth` | register, login, logout |
| user | `/api/user` | profile CRUD, account-id, password |
| diet | `/api/diet` | meal records, calories, water, macros, radar |
| food | `/api/food` | list, detail, search, favorite |
| community | `/api/community` | posts, like, comment, follow |
| achievement | `/api/achievement` | badges, AI body-data/plan/apply |
| upload | `/api/upload` | image upload |

### Auth Flow
Login returns a `user_{id}` token (not JWT). Frontend stores it in `localStorage`, sends as `Bearer` in `Authorization` header. Server-side auth uses Flask-Login sessions with `session['user_id']`.

## Design System

Defined in `原型系统/fresh_vitality/DESIGN.md`. Material Design 3 inspired:
- Primary: `#1A5CB0` (trust blue), Accent: `#34D399` (health green)
- Rounded corners (12-16px), subtle shadows, glass-morphism effects
- Mobile-first responsive layout

## No Automated Tests

There are no test files or test frameworks configured. All testing is manual via the running application.
