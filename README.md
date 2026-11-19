# Market Databank Generation and Sharing Platform
### Full-Stack Web Application Using Python Django
**Course Academic Project | INT253: Web Development in Python Using Django**

---

## 1. Project Overview & Objective

The **Market Databank Generation and Sharing Platform** is a centralized, production-grade web application designed for students, market researchers, business analysts, and investment strategists to collect, structure, validate, analyze, and securely share corporate market intelligence.

Unlike generic spreadsheets or static prototypes, this platform implements a relational, database-backed architecture using **Python 3** and **Django 5.2 LTS**. It enforces granular Role-Based Access Control (RBAC), prevents CSV formula injection attacks, generates publication-quality PDF dossiers via ReportLab, computes real-time database analytics via Chart.js, and strictly isolates private corporate datasets while facilitating public market exploration.

---

## 2. Technology Stack

- **Backend Framework:** Python 3.13 / Django 5.2 LTS
- **Database:** SQLite (development; fully decoupled via Django ORM for PostgreSQL/MySQL production deployment)
- **Document & Report Generation:** ReportLab Platypus Engine, Pillow
- **Frontend & Styling:** HTML5, CSS3, Bootstrap 5.3, Bootstrap Icons
- **Data Visualization:** Chart.js 4.4 (Canvas charts with client-side PNG export)
- **Authentication & Security:** Django Built-in Authentication, PBKDF2 Password Hashing, CSRF Middleware, Session Management, CSV Formula Sanitization, Safe Redirect Enforcement
- **Architecture Pattern:** Model-View-Template (MVT)

---

## 3. Project Architecture & Directory Layout

```
MarketDatabank/
│
├── manage.py                          # Django management CLI utility
├── requirements.txt                   # Explicit project dependencies
├── README.md                          # Comprehensive documentation & viva guide
├── db.sqlite3                         # Local development database
├── .gitignore                         # Version control hygiene
├── .env.example                       # Environment configuration template
│
├── docs/                              # Detailed Technical & User Documentation
│   ├── PROJECT_DOCUMENTATION.md       # Comprehensive technical architecture & spec
│   ├── DATABASE_SCHEMA.md             # Authentic relational database schema
│   ├── USER_GUIDE.md                  # Complete end-to-end user & workflow guide
│   └── TESTING_REPORT.md              # Quality assurance & security testing report
│
├── market_databank/                   # Project Configuration Package
│   ├── __init__.py
│   ├── settings.py                    # Global settings, installed apps, security policies
│   ├── urls.py                        # Root URL router & custom error handlers
│   ├── asgi.py                        # ASGI deployment entrypoint
│   └── wsgi.py                        # WSGI deployment entrypoint
│
├── accounts/                          # App 1: Authentication & User Profiles
│   ├── migrations/                    # Database migrations
│   ├── templates/accounts/
│   │   ├── register.html              # User registration with password meter
│   │   ├── login.html                 # Login page with "Remember Me" & password toggle
│   │   └── profile.html               # Profile management & activity counter
│   ├── forms.py                       # Registration, Login, and Profile ModelForms
│   ├── views.py                       # User auth views & session handlers
│   ├── urls.py                        # Route definitions for accounts
│   ├── admin.py                       # Admin customization
│   └── tests.py                       # Automated authentication test suite (7 tests)
│
├── databank/                          # App 2: Core Market Data & Repositories
│   ├── management/commands/
│   │   ├── load_sample_market_data.py # Seeds illustrative categories & datasets
│   │   └── setup_admin.py             # Safe superuser initialization
│   ├── migrations/                    # Database migrations
│   ├── templates/databank/
│   │   ├── dashboard.html             # User personalized analytics dashboard
│   │   ├── explore.html               # Public/shared dataset explorer (Grid/Table view)
│   │   ├── my_datasets.html           # Owned dataset management table
│   │   ├── create_dataset.html        # 3-section financial dataset creation form
│   │   ├── dataset_detail.html        # 3-tab dataset breakdown & active shares
│   │   ├── edit_dataset.html          # Dataset update form (Owner/Editor)
│   │   └── delete_confirm.html        # Safe POST deletion confirmation
│   ├── models.py                      # Category, MarketData, and ActivityLog models
│   ├── forms.py                       # MarketDataModelForm with validators
│   ├── reports.py                     # ReportLab Platypus PDF dossier generator
│   ├── views.py                       # CRUD, search, filters, CSV (BOM) & PDF exports
│   ├── urls.py                        # Route definitions for databank
│   ├── admin.py                       # ModelAdmin with filters, search, and hierarchy
│   └── tests.py                       # Automated CRUD, search, CSV & PDF export tests (14 tests)
│
├── sharing/                           # App 3: Collaboration & RBAC Permissions
│   ├── migrations/                    # Database migrations
│   ├── templates/sharing/
│   │   ├── share_form.html            # Share invitation form with radio permission cards
│   │   └── shared_with_me.html        # Datasets shared with the current user
│   ├── models.py                      # DataShare model with uniqueness constraints
│   ├── forms.py                       # DataShareForm with email/user validation
│   ├── views.py                       # Share delegation, update, and revocation views
│   ├── urls.py                        # Route definitions for sharing
│   ├── admin.py                       # DataShare administration
│   └── tests.py                       # Automated RBAC, sharing & safe redirect tests (10 tests)
│
├── analytics/                         # App 4: Market Aggregations & Visualizations
│   ├── templates/analytics/
│   │   └── analytics.html             # Chart.js visualizations & PNG image export
│   ├── views.py                       # Aggregate ORM queries & JSON data API
│   ├── urls.py                        # Route definitions for analytics
│   └── tests.py                       # Automated analytics and API tests (2 tests)
│
├── templates/                         # Global Reusable Templates
│   ├── base.html                      # Root HTML master skeleton
│   ├── home.html                      # Public landing page with live DB metrics
│   ├── 403.html                       # Custom Forbidden / Access Denied error page
│   ├── 404.html                       # Custom Page Not Found error page
│   ├── 500.html                       # Custom Server Error error page
│   └── includes/
│       ├── navbar.html                # Top navigation bar with Ctrl+K search shortcut
│       ├── sidebar.html               # Responsive offcanvas-lg navigation sidebar
│       ├── footer.html                # Platform footer with course attribution
│       └── messages.html              # Bootstrap 5 alert message container
│
└── static/                            # Static Assets
    ├── css/
    │   └── style.css                  # Design system tokens, SaaS geometry & components
    └── js/
        └── main.js                    # UI interactions, password meter, copy-link & charts
```

---

## 4. The Four Django Applications

### 1. `accounts`
- **Purpose:** Manages user identity, registration, session authentication, and profile settings.
- **Key Features:** Form validation, Django password hashing (PBKDF2), interactive client-side password strength meter mirroring backend validators, password visibility toggles, session expiry control ("Remember Me"), safe redirect verification, and contribution activity summaries.

### 2. `databank`
- **Purpose:** The core repository engine for storing, organizing, and exporting market research.
- **Key Features:** Full CRUD lifecycle for market datasets with a 3-section structured financial layout, live description character counter, categorization by industry, multi-parameter search (title, company, industry, product), active dismissible filter pills, persistent Grid vs. Table view toggle, sorting, pagination, sanitized CSV exports with UTF-8 BOM, and publication-quality PDF dossiers generated using ReportLab.

### 3. `sharing`
- **Purpose:** Implements granular Role-Based Access Control (RBAC) across collaborative research teams.
- **Key Features:**
  - **Viewer:** Authorized to inspect dataset metrics and download CSV/PDF exports. Cannot modify records.
  - **Editor:** Authorized to modify dataset economics, pricing, demand, and qualitative findings. Cannot delete or re-share.
  - **Owner:** Retains exclusive deletion, sharing invitation, role modification, and access revocation rights.
  - Interactive selectable radio cards for permission assignment.
  - Open redirect defense on `next` redirect parameters.

### 4. `analytics`
- **Purpose:** Aggregates macro-economic market metrics across the entire platform.
- **Key Features:** Uses Django ORM aggregation functions (`Count`, `Avg`, `Min`, `Max`, `TruncMonth`) to generate real database-backed Chart.js visualizations (Sectors, Demand Distribution, Top Companies, Benchmark Pricing, and Creation Trends) with client-side PNG image export and a supplementary JSON API endpoint.

---

## 5. Complete URL & Routing Architecture

| App | URL Path | View Function | Name | Auth Required | Purpose |
|---|---|---|---|---|---|
| **Root** | `/` | `databank.views.home_view` | `home` | No | Public landing page |
| **Admin** | `/admin/` | `admin.site.urls` | `admin:index` | Staff | Django administration portal |
| **Accounts**| `/accounts/register/` | `accounts.views.register_view` | `accounts:register` | No | New user registration |
| **Accounts**| `/accounts/login/` | `accounts.views.login_view` | `accounts:login` | No | User authentication |
| **Accounts**| `/accounts/logout/` | `accounts.views.logout_view` | `accounts:logout` | Yes (POST) | Secure session logout |
| **Accounts**| `/accounts/profile/` | `accounts.views.profile_view` | `accounts:profile` | Yes | User profile and activity view |
| **Databank**| `/databank/dashboard/` | `databank.views.dashboard_view` | `databank:dashboard` | Yes | Personalized user dashboard |
| **Databank**| `/databank/explore/` | `databank.views.explore_view` | `databank:explore` | No / Yes | Search & explore public datasets |
| **Databank**| `/databank/my-datasets/` | `databank.views.my_datasets_view` | `databank:my_datasets`| Yes | Owned dataset management |
| **Databank**| `/databank/create/` | `databank.views.create_dataset_view` | `databank:create` | Yes | Create new market dataset |
| **Databank**| `/databank/<id>/` | `databank.views.dataset_detail_view` | `databank:detail` | Conditional | Inspect dataset details |
| **Databank**| `/databank/<id>/edit/` | `databank.views.edit_dataset_view` | `databank:edit` | Owner/Editor | Modify dataset records |
| **Databank**| `/databank/<id>/delete/` | `databank.views.delete_dataset_view` | `databank:delete` | Owner Only | Confirm & delete dataset (POST) |
| **Databank**| `/databank/<id>/export/csv/`| `databank.views.export_dataset_csv_view`| `databank:export_csv` | Authorized | Export sanitized CSV with BOM |
| **Databank**| `/databank/<id>/export/pdf/`| `databank.views.export_dataset_pdf_view`| `databank:export_pdf` | Authorized | Export ReportLab PDF dossier |
| **Sharing** | `/sharing/share/<id>/` | `sharing.views.share_dataset_view` | `sharing:share_dataset`| Owner Only | Share dataset with user |
| **Sharing** | `/sharing/update/<id>/`| `sharing.views.update_share_permission_view` | `sharing:update_share` | Owner Only | Update collaborator permission |
| **Sharing** | `/sharing/shared-with-me/`| `sharing.views.shared_with_me_view`| `sharing:shared_with_me`| Yes | View received shared datasets |
| **Sharing** | `/sharing/revoke/<id>/` | `sharing.views.revoke_share_view` | `sharing:revoke_share` | Owner Only | Revoke collaborator access |
| **Analytics**| `/analytics/` | `analytics.views.analytics_dashboard_view`| `analytics:dashboard`| Yes | Comprehensive macro charts |
| **Analytics**| `/analytics/api/data/` | `analytics.views.analytics_api_view` | `analytics:api_data` | Yes | REST JSON metrics endpoint |

---

## 6. Implementation of the INT253 Syllabus Units

The project was engineered specifically to demonstrate mastery over all six units of the **INT253: Web Development in Python Using Django** syllabus:

### Unit I: Introduction to Django
- **Virtual Environment & Tooling:** Configured in `.venv` with Python 3.13 and Django 5.2 LTS.
- **Project Structure:** Created via `django-admin startproject market_databank` and modularized using `startapp` into `accounts`, `databank`, `sharing`, and `analytics`.
- **Settings Configuration:** Configured `INSTALLED_APPS`, `TEMPLATES`, `STATIC_URL`, `STATICFILES_DIRS`, `DATABASES`, `AUTH_PASSWORD_VALIDATORS`, and custom `MESSAGE_TAGS`.

### Unit II: Views and URLs
- **Function-Based Views (FBVs):** Implemented in each app with clear separation of GET (presentation) and POST (data mutations).
- **URL Namespaces:** Utilized `namespace='accounts'`, `namespace='databank'`, `namespace='sharing'`, and `namespace='analytics'` with reverse URL resolution (`{% url 'databank:detail' dataset.pk %}`).
- **HTTP Handling:** Used `HttpResponse`, `JsonResponse`, `HttpResponseRedirect`, `redirect()`, and `get_object_or_404()`.
- **Custom Error Handlers:** Implemented `handler403`, `handler404`, and `handler500` rendering branded custom error templates.

### Unit III: Templates, Debugging and Testing
- **Django Template Language (DTL):** Master-child template inheritance via `templates/base.html` and reusable subcomponents (`navbar.html`, `sidebar.html`, `footer.html`, `messages.html`).
- **Template Filters & Tags:** `{{ dataset.market_price|floatformat:2 }}`, `{{ dataset.created_at|date:"M d, Y" }}`, `{{ dataset.created_at|timesince }}`, `{% for %}`, `{% if %}`, `{% url %}`, and `{% csrf_token %}`.
- **Automated Testing Suite:** 33 comprehensive unit and integration tests across all four applications executed via `manage.py test`.

### Unit IV: Forms in Django
- **Forms & ModelForms:** Custom `UserRegistrationForm`, `UserLoginForm`, `UserProfileUpdateForm`, `MarketDataForm`, and `DataShareForm`.
- **Security & Integrity:** Strict CSRF tokens (`{% csrf_token %}`) on every form.
- **Validation:** Implemented field-level (`clean_market_price`, `clean_collection_date`) and form-level (`clean()`) validation preventing future dates, negative prices, and duplicate accounts.
- **POST-Redirect-GET:** Applied on registration, dataset creation, editing, sharing, and profile updates to prevent duplicate form submissions.

### Unit V: Models, Migrations and Django Admin
- **Relational Models:** `Category`, `MarketData`, `DataShare`, and `ActivityLog` featuring `ForeignKey` relations, cascade/protect behaviors, text choices, and custom validation.
- **Database Indexing & Constraints:** Indexes on `title`, `company_name`, `industry`, and `visibility`. Unique constraints on active shares (`['dataset', 'shared_with']`).
- **Migrations:** Managed via `makemigrations` and `migrate`.
- **Django Admin Customization:** Custom `ModelAdmin` subclasses with `list_display`, `list_filter`, `search_fields`, `ordering`, `date_hierarchy`, `readonly_fields`, and organized `fieldsets`.

### Unit VI: Cookies, Sessions, Users and Authentication
- **User Authentication:** Built using `django.contrib.auth` with session management.
- **Protected Views:** Enforced with `@login_required` decorators and `PermissionDenied` exception raising for RBAC violations.
- **Sessions & Expiry:** "Remember Me" control via `request.session.set_expiry()` (session cookie vs. persistent 2-week cookie).
- **Client Cookies Demonstration:** Integrated in `static/js/main.js` to remember the user's preferred layout view.

---

## 7. Security Architecture & Threat Mitigations

1. **Password Security:** Passwords hashed with Django's default PBKDF2 with SHA256 hashing. Passwords are never stored or logged in plaintext.
2. **Access Control & Anti-Spoofing:** Backend views automatically bind `dataset.created_by = request.user`, ignoring any malicious user IDs submitted in request payloads.
3. **Data Scoping:** Private datasets are strictly filtered out of search results for unauthorized users. Direct URL access to private datasets without ownership or active share raises `PermissionDenied` (HTTP 403).
4. **Formula Injection (CSV Injection) Mitigation:** When exporting datasets to CSV, cells starting with `=`, `+`, `-`, or `@` are sanitized by prepending an apostrophe (`'`), preventing malicious execution in Excel or Calc.
5. **CSRF Protection:** Django's `CsrfViewMiddleware` is enabled across all forms; deletion and logout operations require POST with CSRF tokens.
6. **Open Redirect Prevention:** All `next` parameter redirects validate destination URLs using `url_has_allowed_host_and_scheme`.
7. **Excel UTF-8 BOM Compatibility:** CSV exports write a UTF-8 Byte Order Mark (`\ufeff`) ensuring currency symbols (`₹`) display correctly in Microsoft Excel.

---

## 8. Installation & Setup Instructions

### Prerequisites
- Python 3.10+ (Tested on Python 3.13)
- Windows PowerShell, macOS Terminal, or Linux Bash

### Step 1: Clone or Navigate to the Workspace
```powershell
cd c:\Users\ankit\Downloads\MarketDatabank
```

### Step 2: Initialize Virtual Environment
```powershell
python -m venv .venv
# On Windows:
.\.venv\Scripts\Activate.ps1
# On Linux/macOS:
source .venv/bin/activate
```

### Step 3: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 4: Apply Database Migrations
```powershell
python manage.py migrate
```

### Step 5: Initialize Administrator Superuser
To create an administrator account safely without hardcoded insecure credentials:
```powershell
# Interactive Django superuser prompt:
python manage.py createsuperuser

# Or automated locked initial setup:
python manage.py setup_admin --username admin --email admin@example.com
python manage.py changepassword admin
```

### Step 6: Load Illustrative Sample Market Databank
Populates realistic, illustrative categories and corporate market records (Tata Motors, Infosys, Reliance, Zomato, HDFC Bank):
```powershell
python manage.py load_sample_market_data
```

### Step 7: Run Automated Verification Tests
```powershell
python manage.py test
```
*Expected result: 33 tests passing (OK).*

### Step 8: Start Development Server
```powershell
python manage.py runserver
```
Visit the platform in your browser at: **`http://127.0.0.1:8000/`**

---

## 9. Completed Pages Checklist & Verification

- [x] **Page 1: Home Page (`/`)** — Landing page with live database counters, feature cards, workflow walkthrough, and direct navigation links.
- [x] **Page 2: Registration Page (`/accounts/register/`)** — User creation form with custom password strength validation, email uniqueness, and safe redirects.
- [x] **Page 3: Login Page (`/accounts/login/`)** — Authentication form with "Remember Me" session configuration and safe redirect handling.
- [x] **Page 4: User Dashboard (`/databank/dashboard/`)** — Real DB stats (created datasets, shared datasets, public datasets, categories), Quick Actions, recent activity timeline, and Chart.js visualizations.
- [x] **Page 5: Create Market Dataset (`/databank/create/`)** — Form with 12 validation fields, automatic creator association, and activity auditing.
- [x] **Page 6: My Datasets (`/databank/my-datasets/`)** — Owned dataset data table with search, category/demand/visibility filters, pagination, and action buttons.
- [x] **Page 7: Explore Databank (`/databank/explore/`)** — Public and shared dataset explorer with sorting (price, date), keyword search, sector filters, and Grid/Table view toggle.
- [x] **Page 8: Dataset Details (`/databank/<id>/`)** — Comprehensive metric display, provenance citation, active collaborator roster, and permission-conditioned action buttons.
- [x] **Page 9: Edit Dataset (`/databank/<id>/edit/`)** — Form pre-filled with existing metrics; accessible only to Owner or authorized Editor.
- [x] **Page 10: Delete Dataset (`/databank/<id>/delete/`)** — POST-enforced confirmation dialog preventing accidental deletion; accessible strictly to Owner.
- [x] **Page 11: Share Dataset (`/sharing/share/<id>/`)** — Collaboration invitation form with user validation, duplicate prevention, and Viewer/Editor role selection.
- [x] **Page 12: Shared With Me (`/sharing/shared-with-me/`)** — Table of received shared datasets with permission badges, search filters, and empty state.
- [x] **Page 13: Market Analytics (`/analytics/`)** — Macro analytics page with 5 dynamic Chart.js charts and JSON API integration.
- [x] **Page 14: User Profile (`/accounts/profile/`)** — User identity details, creation/sharing contribution counters, and profile update form.
- [x] **Custom Error Pages (`403.html`, `404.html`, `500.html`)** — Custom error pages maintaining brand aesthetic and navigation back to safe zones.
