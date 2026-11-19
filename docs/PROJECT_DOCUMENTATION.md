# Market Databank Generation and Sharing Platform — Technical Project Documentation

**Course Academic Project | INT253: Web Development in Python Using Django**

---

## 1. Project Introduction

The **Market Databank Generation and Sharing Platform** is a full-stack, database-backed enterprise web application developed in Python using the Django 5.2 LTS framework. The platform provides a centralized, secure repository where researchers, financial analysts, and business students can structure, store, query, analyze, and selectively share corporate market research datasets.

Traditional market research workflows often suffer from fragmented spreadsheet silos, untracked modifications, formula injection security risks, and lack of granular access control. Market Databank resolves these operational challenges by offering a structured Model-View-Template (MVT) architecture with strict Role-Based Access Control (RBAC), multi-format data exports (CSV with formula sanitization & ReportLab PDF generation), real-time database-driven analytics via Chart.js, and an institutional SaaS user interface.

---

## 2. Problem Statement

1. **Unstructured Data Silos:** Market research notes are commonly scattered across local spreadsheets, PDFs, and unstructured text documents, making cross-sector analysis difficult.
2. **Security & Injection Risks in Exports:** Standard CSV exports from web platforms frequently fail to sanitize formula syntax (`=`, `+`, `-`, `@`), leaving end users vulnerable to spreadsheet formula injection attacks.
3. **Encoding & Regional Currency Defects:** Spreadsheets opened in Microsoft Excel without a UTF-8 Byte Order Mark (BOM) frequently corrupt regional currency symbols (e.g., `₹`) and accented characters.
4. **All-or-Nothing Collaboration:** Traditional sharing mechanisms either lock users out completely or give unrestricted write permissions without auditing.
5. **Lack of Provenance Tracking:** Changes to research datasets often lack clear audit trails, making it impossible to verify data sources or determine when figures were updated.

---

## 3. Project Objectives

- **Centralized Data Repository:** Provide a normalized relational database schema for storing verified corporate market data across diverse economic sectors.
- **Granular RBAC Security:** Implement distinct **Owner**, **Editor**, and **Viewer** roles with strict object-level authorization across read, write, export, and delete operations.
- **Safe & Standardized Exports:** Deliver sanitized CSV exports with UTF-8 BOM encoding alongside publication-grade PDF dossiers generated using the ReportLab Platypus engine.
- **Macro & Personal Analytics:** Aggregate database metrics dynamically into Chart.js visualizations with client-side PNG image export capabilities.
- **Modern Institutional UI/UX:** Provide a responsive, accessible, financial research SaaS design with dark-mode navbar, offcanvas mobile navigation, and live form validation.

---

## 4. Scope & Boundaries

### In Scope:
- User registration, authentication, password strength validation, and profile management.
- Complete CRUD workflow for market datasets with 3-section financial form layout.
- Sector categorization, multi-parameter search, active filter pills, sorting, and pagination.
- Dataset sharing mechanism with invite cards, inline role toggles, and instant access revocation.
- Role-based CSV export with formula injection prevention and ReportLab PDF reporting.
- Personal dashboard analytics and global platform-wide intelligence charts.
- Comprehensive automated regression test suite covering authentication, CRUD, RBAC, and exports.

### Out of Scope:
- Live external third-party stock ticker scraping or automated real-time financial market APIs (all data is curated within the platform).
- Payment gateways or paid subscription tiers (designed as an academic research platform).

---

## 5. System Architecture & Module Descriptions

```
+--------------------------------------------------------------------------+
|                              PRESENTATION LAYER                          |
|   HTML5 + Bootstrap 5.3 + Chart.js 4.4 + Bootstrap Icons + Custom CSS/JS |
+--------------------------------------------------------------------------+
                                    │
                                    ▼
+--------------------------------------------------------------------------+
|                             APPLICATION LAYER                            |
|                                                                          |
|  [accounts]         [databank]           [sharing]          [analytics]  |
|  - Registration     - Datasets CRUD      - DataShare Model  - Aggregates |
|  - Login / Logout   - CSV Export (BOM)   - RBAC Enforcement - Chart APIs |
|  - User Profiles    - PDF Export (ReportLab) - Collaborator Admin - Trends|
|  - Password Policy  - ActivityLog Audit  - Safe Redirects                |
+--------------------------------------------------------------------------+
                                    │
                                    ▼
+--------------------------------------------------------------------------+
|                                DATA LAYER                                |
|          Django ORM + SQLite3 (PostgreSQL-compatible abstraction)        |
+--------------------------------------------------------------------------+
```

### Module Descriptions:

1. **`accounts` (Authentication & Security):**
   - Implements PBKDF2 password hashing with Django's `AUTH_PASSWORD_VALIDATORS`.
   - Real-time client-side password strength meter in `main.js` mirroring backend validator rules.
   - Session management with configurable session expiry based on "Remember Me".
   - Safe redirect verification via `url_has_allowed_host_and_scheme`.

2. **`databank` (Core Market Datasets & Reporting):**
   - Manages `Category`, `MarketData`, and `ActivityLog` models.
   - Provides public repository explorer, personalized owner dataset table, and detailed views.
   - Sanitizes CSV exports against formula injection (`sanitize_csv_cell`).
   - Implements multi-flow PDF generation using ReportLab Platypus (`reports.py`).

3. **`sharing` (Collaboration & Access Control):**
   - Enforces unique active sharing constraints via `DataShare` model.
   - Supports role delegation (`Viewer` vs `Editor`) through accessible selection cards.
   - Provides inline permission adjustment and immediate access revocation.
   - Validates redirect targets against open redirect vulnerabilities.

4. **`analytics` (Intelligence & Data Visualization):**
   - Computes server-side database aggregations (sector counts, average valuations, monthly trends).
   - Serves structured JSON context for responsive Chart.js rendering.
   - Provides REST-style JSON API endpoint (`/analytics/api/summary/`).

---

## 6. Security & Governance Policies

1. **Role-Based Access Control (RBAC):**
   - **Owner:** Exclusive authority to edit, delete, share, change roles, revoke access, and export.
   - **Editor:** Authorized to view insights, download exports, and edit pricing, market size, demand, and description. Cannot delete or re-share.
   - **Viewer:** Authorized to inspect metrics, read findings, and download sanitized exports. Strictly read-only.
   - **Public Visitor:** Can view public datasets and download exports. Cannot access private datasets.

2. **Spreadsheet Formula Injection Defense (CSV Injection / CWE-1236):**
   - Cells beginning with `=`, `+`, `-`, or `@` are automatically prepended with a single quote (`'`), ensuring spreadsheet software interprets them strictly as plain text strings rather than executable formulas.

3. **Open Redirect Defense (CWE-601):**
   - All `next` parameter redirects in authentication and sharing workflows are strictly validated against `url_has_allowed_host_and_scheme` with the request host.

4. **Cross-Site Request Forgery (CSRF):**
   - All form submissions (POST requests) require valid `{% csrf_token %}` tokens validated by Django's `CsrfViewMiddleware`.

5. **Cross-Site Scripting (XSS):**
   - Django's template engine auto-escapes all dynamic variables by default.

---

## 7. Export Implementations

### CSV Export:
- **Encoding:** UTF-8 with Byte Order Mark (`\ufeff`) written directly to response buffer.
- **Columns (17 total):** `ID`, `Title`, `Company Name`, `Category`, `Industry`, `Product/Service`, `Market Price`, `Market Demand`, `Market Size`, `Growth Rate (%)`, `Description`, `Data Source`, `Collection Date`, `Visibility`, `Creator`, `Created At`, `Updated At`.
- **Filename:** Formatted as `MarketDatabank_<SafeTitle>_<ID>.csv`.

### PDF Export:
- **Engine:** ReportLab Platypus (Page layout, `SimpleDocTemplate`, `Paragraph`, `Table`, `Spacer`, `KeepTogether`).
- **Styling:** Custom corporate color scheme (Navy `#14213D`, Accent Blue `#2563EB`, Grey borders).
- **Structure:** Institutional title block, metadata summary table, 4-cell financial KPI grid, qualitative findings narrative block, and research provenance footer.

---

## 8. Verification & Automated Testing

The platform maintains an automated test suite executed via Django's test runner:
- **Total Tests:** 33 automated tests.
- **Coverage Areas:** User registration, password validation, login/logout, CRUD operations, private dataset isolation, RBAC sharing rules, editor modifications, share revocation, safe redirects, CSV formula sanitization, and ReportLab PDF generation.
