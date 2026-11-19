# Market Databank — Database Schema Reference

This document provides the authentic relational database schema for the Market Databank Generation and Sharing Platform, directly reflecting the Django models defined in `databank/models.py`, `sharing/models.py`, and Django's built-in authentication system.

---

## Entity Relationship Overview

```
       +-------------------+
       |     auth_user     |
       +-------------------+
         | 1             1 |
         |               |
         | *             | *
+-----------------+   +--------------------+
|  databank_      |   |  sharing_datashare |
|  marketdata     |   +--------------------+
+-----------------+        | *
  | *           | 1        |
  |             |          |
  | 1           +----------+
+-----------------+
| databank_       |
| category        |
+-----------------+
  | 1
  |
  | *
+-----------------+
| databank_       |
| activitylog     |
+-----------------+
```

---

## 1. `auth_user` (Django Built-in User)
Tracks registered users, authentication credentials, and administrative privileges.

| Column | Data Type | Nullable | Default | Description |
|---|---|---|---|---|
| `id` | BigAutoField | No | Auto | Primary key |
| `username` | VarChar(150) | No | — | Unique username for platform login |
| `email` | VarChar(254) | No | — | User contact & invitation email |
| `password` | VarChar(128) | No | — | PBKDF2 with SHA-256 password hash |
| `first_name` | VarChar(150) | No | '' | Given name |
| `last_name` | VarChar(150) | No | '' | Surname |
| `is_staff` | Boolean | No | False | Grants Django admin dashboard access |
| `is_active` | Boolean | No | True | Account status flag |
| `is_superuser` | Boolean | No | False | Full administrative permissions |
| `last_login` | DateTime | Yes | Null | Timestamp of most recent authentication |
| `date_joined` | DateTime | No | Now | Account creation timestamp |

---

## 2. `databank_category` (Market Sector Classification)
Defines high-level market sectors for structured classification.

| Column | Data Type | Nullable | Default | Description |
|---|---|---|---|---|
| `id` | BigAutoField | No | Auto | Primary key |
| `name` | VarChar(100) | No | — | Unique sector name (e.g. IT, Healthcare, Automobile) |
| `description` | Text | Yes | '' | Detailed sector scope and definitions |
| `created_at` | DateTime | No | Auto (now) | Category timestamp |

**Indexes & Constraints:**
- `UNIQUE(name)`

---

## 3. `databank_marketdata` (Core Market Datasets)
Stores individual corporate market intelligence records with financial metrics and provenance.

| Column | Data Type | Nullable | Default | Description |
|---|---|---|---|---|
| `id` | BigAutoField | No | Auto | Primary key |
| `title` | VarChar(200) | No | — | Descriptive title of market study |
| `company_name` | VarChar(150) | No | — | Subject corporation or organization |
| `category_id` | BigInt (FK) | No | — | References `databank_category.id` (`on_delete=PROTECT`) |
| `industry` | VarChar(100) | No | — | Industry segment (e.g. Clean Energy Infrastructure) |
| `product_service` | VarChar(200) | No | — | Specific product or service line evaluated |
| `market_price` | Decimal(12,2) | No | — | Benchmark unit price in INR (min: 0.00) |
| `market_demand` | VarChar(20) | No | 'Medium' | Qualitative demand (`High`, `Medium`, `Low`) |
| `market_size` | Decimal(15,2) | Yes | Null | Estimated Total Addressable Market in INR (min: 0.00) |
| `market_growth_rate` | Decimal(5,2) | Yes | Null | CAGR % (-100.00% to +1000.00%) |
| `description` | Text | No | — | In-depth findings and qualitative analysis |
| `data_source` | VarChar(255) | No | — | Primary source citation (e.g. SEC Filing, Annual Report) |
| `collection_date` | Date | No | — | Date when data was collected/published |
| `visibility` | VarChar(10) | No | 'Private' | Visibility state: `Public` or `Private` |
| `created_by_id` | BigInt (FK) | No | — | References `auth_user.id` (`on_delete=CASCADE`) |
| `created_at` | DateTime | No | Auto (now) | Record creation timestamp |
| `updated_at` | DateTime | No | Auto (update) | Last modified timestamp |

**Indexes & Constraints:**
- Index on `title`
- Index on `company_name`
- Index on `industry`
- Index on `created_at`

---

## 4. `sharing_datashare` (Role-Based Access Control)
Manages granular dataset sharing permissions among users.

| Column | Data Type | Nullable | Default | Description |
|---|---|---|---|---|
| `id` | BigAutoField | No | Auto | Primary key |
| `dataset_id` | BigInt (FK) | No | — | Target dataset (`databank_marketdata.id`, CASCADE) |
| `shared_by_id` | BigInt (FK) | No | — | Owner granting access (`auth_user.id`, CASCADE) |
| `shared_with_id` | BigInt (FK) | No | — | Collaborator receiving access (`auth_user.id`, CASCADE) |
| `permission` | VarChar(10) | No | 'Viewer' | Granted access: `Viewer` or `Editor` |
| `message` | Text | Yes | '' | Optional context note from sharer |
| `shared_at` | DateTime | No | Auto (now) | Timestamp when access was granted |
| `is_active` | Boolean | No | True | Toggle for access revocation & reactivation |

**Indexes & Constraints:**
- `UniqueConstraint(fields=['dataset', 'shared_with'], condition=Q(is_active=True))`
- Clean method enforcement: `shared_by != shared_with` and `shared_with != dataset.created_by`.

---

## 5. `databank_activitylog` (Audit Trail & Activity Logging)
Maintains an immutable record of significant user actions across the platform.

| Column | Data Type | Nullable | Default | Description |
|---|---|---|---|---|
| `id` | BigAutoField | No | Auto | Primary key |
| `user_id` | BigInt (FK) | No | — | User who executed action (`auth_user.id`, CASCADE) |
| `action` | VarChar(100) | No | — | Action title (e.g. `Created Dataset`, `Exported CSV`, `Shared Dataset`) |
| `dataset_id` | BigInt (FK) | Yes | Null | Associated dataset (`databank_marketdata.id`, SET_NULL) |
| `details` | Text | Yes | '' | Structured audit metadata or action description |
| `timestamp` | DateTime | No | Auto (now) | Timestamp of event execution |

**Ordering:**
- `ordering = ['-timestamp']`
