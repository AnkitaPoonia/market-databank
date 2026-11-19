# Market Databank — Comprehensive User Guide

Welcome to the **Market Databank Generation and Sharing Platform**. This user guide outlines every user workflow from initial account setup to multi-user collaborative research and reporting.

---

## Table of Contents
1. [Account Registration & Authentication](#1-account-registration--authentication)
2. [Exploring the Databank](#2-exploring-the-databank)
3. [Personal Dashboard & Analytics](#3-personal-dashboard--analytics)
4. [Creating New Market Datasets](#4-creating-new-market-datasets)
5. [Managing Your Datasets](#5-managing-your-datasets)
6. [Dataset Details & Inspection](#6-dataset-details--inspection)
7. [Dataset Sharing & Collaboration (RBAC)](#7-dataset-sharing--collaboration-rbac)
8. [Exporting Data (CSV & PDF)](#8-exporting-data-csv--pdf)
9. [Macro Analytics & Chart Export](#9-macro-analytics--chart-export)
10. [User Profile Management](#10-user-profile-management)

---

## 1. Account Registration & Authentication

### Creating an Account
1. Navigate to `/accounts/register/` or click **Get Started Free** / **Register** in the top navigation bar.
2. Complete the registration form:
   - **Username:** Alphanumeric identifier (letters, digits, `@/./+/-/_`).
   - **Email:** Registered contact address.
   - **First & Last Name:** Personal or organizational name.
   - **Password:** Minimum 8 characters. Observe the real-time **Password Strength Indicator** and Django security validator checklist:
     - Minimum 8 characters
     - Not entirely numeric
     - Not similar to your username or email
     - Not a commonly compromised password
   - Use the **Show/Hide Password** eye toggle to confirm your entry.
3. Click **Create Institutional Account**. Upon successful validation, you are redirected to the login screen with a confirmation message.

### Signing In
1. Navigate to `/accounts/login/`.
2. Enter your registered username and password.
3. Check **Remember this browser** to retain your session across browser restarts.
4. If you navigated to a protected page prior to login, Django's validated `next` parameter returns you safely to your target page.

### Logging Out
- Open your user menu pill in the top navbar and click **Log Out**, or click **Logout** at the bottom of the sidebar. The system safely invalidates your session.

---

## 2. Exploring the Databank

Navigate to `/databank/explore/` (or press **Ctrl + K** from any page to focus the global search bar).

### Search & Filters
- **Keyword Search:** Queries dataset title, company name, industry, and product/service descriptions.
- **Sector Dropdown:** Filter by category (e.g. IT, Automobile, Healthcare).
- **Market Demand Dropdown:** Filter by High, Medium, or Low demand.
- **Sort Ordering:** Sort by newest first, oldest first, price (high-to-low), or price (low-to-high).
- **Active Filter Pills:** Active query parameters appear as interactive dismissible pills above the repository grid. Click the **×** on any pill to remove that specific filter.

### Grid vs. Table View Toggle
- Use the view switch buttons in the upper right to alternate between the **Card Grid** layout and the **Dense Table** view.
- Your selected preference is automatically remembered in your browser's `localStorage` for future visits.

---

## 3. Personal Dashboard & Analytics

Navigate to `/databank/dashboard/`.

### Key Performance Tiles
- **My Datasets:** Total number of datasets owned by your account.
- **Shared With Me:** Active datasets shared with you by other researchers.
- **Public Datasets:** Total accessible public datasets across the platform.
- **Sectors Covered:** Total distinct industry categories tracked.

### Data Visualizations
- **Datasets by Sector:** Interactive bar chart displaying your dataset distribution across categories.
- **Demand Breakdown:** Donut chart representing High, Medium, and Low liquidity profiles.
- **Download Chart:** Click **Save Chart as PNG** on either visualization to download a publication-ready image.

### Recent Activities Timeline
- Live audit log displaying recent actions (dataset creations, edits, sharing permissions, and CSV/PDF downloads).

---

## 4. Creating New Market Datasets

Navigate to `/databank/create/` or click the prominent **+ New Dataset** button in the top navigation.

The dataset generation form is divided into three structured financial sections:

### Section 1: Core Entity & Sector Identification
- **Dataset Title:** Descriptive name of your market research study.
- **Target Company:** Corporate entity under analysis (e.g. Tata Motors, Infosys).
- **Category:** Primary sector classification.
- **Industry Segment:** Specific market segment (e.g. Clean Energy Infrastructure).
- **Product / Service Line:** Key offering or product evaluated.

### Section 2: Valuation & Market Economics
- **Benchmark Price (₹):** Standard unit valuation or benchmark cost in Indian Rupees.
- **Market Demand:** Qualitative liquidity rating (`High`, `Medium`, or `Low`).
- **Estimated Market Size (₹):** Total Addressable Market (TAM). Optional.
- **Growth Rate (CAGR %):** Compound annual growth rate percentage. Optional.

### Section 3: Research Methodology & Governance
- **Market Description & Findings:** In-depth qualitative findings with real-time character counter.
- **Primary Data Source Citation:** Origin of research (e.g. Annual Report 2024, SEC 10-K, Industry Survey).
- **Collection Date:** Date when the data was recorded or published.
- **Accessibility & Visibility:** Choose `Public` (discoverable by all researchers) or `Private` (restricted to you and invited collaborators).

Click **Save & Publish Dataset** in the sticky action bar to save.

---

## 5. Managing Your Datasets

Navigate to `/databank/my-datasets/` to view and manage all datasets you own.

- Search and filter your personal inventory.
- Each row provides quick actions via a consolidated dropdown: **View Details**, **Edit Record**, **Manage Sharing**, **Download CSV**, **Download PDF**, and **Delete**.
- **Safe Deletion:** Deleting a dataset routes to a confirmation screen (`/databank/<pk>/delete/`) to prevent accidental data loss.

---

## 6. Dataset Details & Inspection

Navigate to `/databank/<pk>/` to review a comprehensive dataset dossier.

### Header Banner
- Badges displaying Category, Visibility (`Public` or `Private`), and Owner status (`Owner: You` or `Owner: @username`).
- Company name, collection date, and canonical **Copy Link** button.

### Consolidated Action Bar (Strictly RBAC Scoped)
- **Download CSV:** Downloads sanitized spreadsheet.
- **Download PDF:** Generates publication-ready PDF report.
- **Share Dataset:** Visible exclusively to dataset owners.
- **Edit Dataset:** Visible to owners and authorized editors.
- **Delete Dataset:** Visible exclusively to owners and staff.

### 4 Key Financial KPI Tiles
- **Benchmark Price:** Unit valuation in `₹`.
- **Market Demand:** High, Medium, or Low badge.
- **Est. Market Size:** Addressable market in `₹` or `N/A`.
- **Growth Rate (CAGR):** Percentage growth rate or `N/A`.

### 3 Functional Workflow Tabs
1. **Dataset Insights:** Complete qualitative findings and Enterprise Specifications card.
2. **Provenance & Audit Trail:** Source citation, collection dates, and chronological audit trail of all actions performed on the dataset.
3. **Access & Collaborators:**
   - For owners: Table of all active collaborators, with inline controls to switch permissions between `Viewer` and `Editor` or revoke access.
   - For collaborators: Card detailing your assigned privileges.

---

## 7. Dataset Sharing & Collaboration (RBAC)

Navigate to `/sharing/<dataset_id>/share/` (or click **Share Dataset** from the details page).

### Granting Access
1. **Target Dataset:** Pre-selected automatically.
2. **Recipient:** Enter the registered username or email of a colleague.
3. **Permission Card:** Select one of two accessible cards:
   - **Viewer:** Read-only access to view metrics and download CSV/PDF exports.
   - **Editor:** Collaborative access to view, download, and update pricing, market size, demand, and findings.
4. **Briefing Note (Optional):** Provide instructions or context for your colleague.
5. Click **Grant Sharing Access**.

### Managing Active Collaborators
- The right-hand column lists all current collaborators.
- **Update Permission:** Select `Viewer` or `Editor` from the inline dropdown and click **Update**.
- **Revoke Access:** Click **Revoke** with browser confirmation. The collaborator's access is immediately terminated.
- **Re-sharing:** If a revoked user is invited again, their record is cleanly reactivated with the new permission level.

### Shared With Me View
Navigate to `/sharing/shared-with-me/` to view all datasets shared with you, filterable by `Viewer` or `Editor` status.

---

## 8. Exporting Data (CSV & PDF)

### CSV Export
- Click **Download CSV** on any authorized dataset card or details page.
- **Excel Compatibility:** Written with UTF-8 BOM (`\ufeff`) ensuring characters like `₹` render cleanly in Microsoft Excel.
- **Security:** Cells beginning with `=`, `+`, `-`, or `@` are automatically sanitized to prevent formula injection attacks.

### PDF Dossier Export
- Click **Download PDF** to generate an executive report via ReportLab Platypus.
- Contains platform branding, economic KPI tables, qualitative findings, and provenance audit data.

---

## 9. Macro Analytics & Chart Export

Navigate to `/analytics/`.

- Review platform-wide intelligence: Total Datasets, Categories, Companies Tracked, and Average Benchmark Price.
- **Interactive Visualizations:**
  1. Sector Breakdown (Bar chart)
  2. Market Demand Distribution (Donut chart)
  3. Top Represented Companies (Horizontal bar chart)
  4. Average Benchmark Price by Sector (Bar chart)
  5. Dataset Creation Trends Over Time (Timeline line chart)
- Click **Export PNG** on any chart card to download the visualization directly.

---

## 10. User Profile Management

Navigate to `/accounts/profile/`.

- View your account creation date and live activity counts (Datasets Owned, Shared by You, Shared with You).
- Update your First Name, Last Name, and Email address with server-side validation.
