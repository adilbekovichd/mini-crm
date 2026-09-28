# Mini CRM — Lead Management System

A high-performance, production-ready Mini CRM application built with **Python, Django 5, and Django REST Framework (DRF)**. Designed specifically for customer lead intake, lifecycle qualification, activity auditing, and analytics.

---

## 🌟 Key Features

1. **Lead Lifecycle Management**:
   - Status pipeline: `New` → `Contacted` → `Qualified` → `Won` → `Lost`
   - Real-time status update with immediate REST API persistence.
2. **Activity & Audit History (Bonus 1)**:
   - Automated tracking of all lead mutations, status changes, timestamps, and performing users.
   - Dedicated history timeline endpoint: `/api/v1/leads/{id}/activities/`.
3. **Analytics & Dashboard (Bonus 2)**:
   - High-level metric aggregation (`total`, `new`, `contacted`, `qualified`, `won`, `lost`).
   - Dynamic real-time dashboard endpoint: `/api/v1/dashboard/stats/`.
4. **Advanced REST API**:
   - Full CRUD operations with ModelViewSet.
   - Filtering by `status`, `source`, `assigned_to`, `created_after`, `created_before`.
   - Multi-field Search across `name`, `phone`, `email`, `source`, `note`.
   - Multi-direction Sorting/Ordering (`-created_at`, `name`, etc.).
   - Paginated responses with total pages and next/previous metadata.
   - Comprehensive payload validation and clean 400 Bad Request error envelopes.
5. **Interactive OpenAPI / Swagger Documentation (Bonus 4)**:
   - Auto-generated schemas powered by `drf-spectacular` at `/api/docs/` and `/api/redoc/`.
6. **Authentication & Security**:
   - SessionAuthentication for Web Dashboard.
   - TokenAuthentication for programmatic API clients (`/api/v1/auth/token/`).
   - CSRF protection and role-aware permissions.
7. **Production Containerization (Bonus 5)**:
   - Optimized `Dockerfile` & `docker-compose.yml` pre-configured with PostgreSQL and Gunicorn.

---

## 🏗️ Architecture & Project Structure

The project strictly follows Django separation of concerns:

```
mini_crm/
├── config/                  # Core settings, URL routing, WSGI/ASGI
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── leads/                   # Modular Lead application
│   ├── admin.py             # Rich Django admin configuration
│   ├── apps.py
│   ├── models.py            # Lead & LeadActivity relational models
│   ├── serializers.py       # DRF serializers, field & object-level validation
│   ├── views_api.py         # REST ModelViewSet, custom action, stats endpoint
│   ├── views_web.py         # Server-rendered web views (login, dashboard, CRM)
│   ├── filters.py           # django-filter FilterSets
│   ├── pagination.py        # StandardResultsSetPagination
│   ├── permissions.py       # Custom authorization classes
│   ├── urls_api.py          # API route definitions
│   ├── urls_web.py          # Frontend route definitions
│   └── tests.py             # Complete test suite
├── templates/               # Semantic HTML templates
│   ├── base.html            # Layout, sidebar, authenticated fetch utility
│   ├── auth/login.html
│   ├── dashboard.html       # Analytics overview consuming /api/v1/dashboard/stats/
│   └── leads/               # list.html, create.html, detail.html, edit.html
├── static/
│   └── css/style.css        # Clean responsive CRM UI design system
├── Dockerfile               # Multi-stage container definition
├── docker-compose.yml       # Web + PostgreSQL stack orchestration
├── requirements.txt         # Pinned python dependencies
├── manage.py
├── .env.example
└── README.md
```

---

## 🚀 Quickstart & Local Installation

### Prerequisites
- Python 3.10+
- `pip` and `virtualenv`

### 1. Clone & Environment Setup
```bash
git clone https://github.com/adilbekovichd/mini-crm.git
cd mini-crm

python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment Variables
```bash
cp .env.example .env
```
*(By default, SQLite is used if `DATABASE_URL` is commented out. For PostgreSQL, configure `DATABASE_URL` in `.env`)*.

### 3. Database Migration
```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Create Admin Superuser
```bash
python manage.py createsuperuser
```

### 5. Run Development Server
```bash
python manage.py runserver
```
Visit:
- **Web App**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Swagger API Docs**: [http://127.0.0.1:8000/api/docs/](http://127.0.0.1:8000/api/docs/)
- **Django Admin**: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

---

## 🐳 Docker Deployment

To launch the full PostgreSQL + Gunicorn stack with Docker Compose:

```bash
docker compose up --build -d
docker compose exec web python manage.py createsuperuser
```
The CRM will be immediately accessible on port `8000`.

---

## 🧪 Running Tests

Execute the automated test suite:

```bash
python manage.py test leads
```
Coverage includes:
- Authentication & permission enforcement
- CRUD operations (create, retrieve, update, delete)
- Serializer validation edge-cases
- Status transitions & automated `LeadActivity` history records
- Advanced filtering, searching, and pagination
- Dashboard metrics calculations

---

## 📡 API Reference

### Authentication
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/auth/token/` | Obtain DRF Token (`username`, `password`) |

Header for Token Auth:
```
Authorization: Token <your_token_key>
```

### Leads
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/leads/` | List leads (paginated, filterable, searchable) |
| `POST` | `/api/v1/leads/` | Create a new lead |
| `GET` | `/api/v1/leads/{id}/` | Retrieve lead details |
| `PUT` | `/api/v1/leads/{id}/` | Full update of lead |
| `PATCH` | `/api/v1/leads/{id}/` | Partial update (e.g. status change) |
| `DELETE` | `/api/v1/leads/{id}/` | Delete a lead |
| `GET` | `/api/v1/leads/{id}/activities/` | Get audit/activity timeline for lead |

### Analytics
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/dashboard/stats/` | Aggregate metrics (total, new, won, etc.) |

### Documentation
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/docs/` | Interactive Swagger UI |
| `GET` | `/api/redoc/` | ReDoc Documentation |
| `GET` | `/api/schema/` | Raw OpenAPI 3.0 YAML/JSON Schema |

---

## 🔍 Filter & Search Query Examples

- Filter by status:
  `GET /api/v1/leads/?status=qualified`
- Filter by source:
  `GET /api/v1/leads/?source=telegram`
- Multi-filter:
  `GET /api/v1/leads/?status=won&source=website`
- Search across fields:
  `GET /api/v1/leads/?search=alisher`
- Custom Sorting:
  `GET /api/v1/leads/?ordering=-created_at`
- Pagination:
  `GET /api/v1/leads/?page=2&page_size=20`
