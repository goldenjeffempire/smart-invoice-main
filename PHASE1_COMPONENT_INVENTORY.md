# Phase 1: Component Inventory & Design System Kickoff

**Created:** November 24, 2025  
**Purpose:** Design System & Component Library planning  
**Target:** Reusable UI components for 53-template rebuild

---

## Component Audit: Existing Patterns

### Current Template Analysis

| Template | UI Patterns Found | Reusability Score | Priority |
|----------|------------------|-------------------|----------|
| `base.html` | Navbar, Footer, Flash Messages | 100% | 🔴 Critical |
| `home.html` | Hero, Feature Cards, CTA Buttons, Stats Grid | 90% | 🔴 Critical |
| `invoices/dashboard.html` | Data Table, Filter Bar, Stats Cards, Empty State | 95% | 🔴 Critical |
| `invoices/create_invoice.html` | Multi-step Form, Dynamic List, File Upload | 85% | 🔴 Critical |
| `invoices/invoice_detail.html` | Invoice Card, Action Buttons, Status Badge | 80% | 🟡 High |
| Settings pages (6 files) | Form Groups, Tabs, Profile Card | 75% | 🟡 High |
| Static pages (10 files) | Content Sections, FAQ Accordion, Pricing Table | 60% | 🟢 Medium |

---

## Component Catalog (To Build)

### 1. Foundation Components (Week 1)

#### 1.1 Layout
```html
<!-- Grid System -->
<div class="container">  <!-- Max-width responsive container -->
<div class="row">        <!-- Flexbox row -->
<div class="col-{size}"> <!-- Responsive columns -->

<!-- Section Wrapper -->
<section class="section">  <!-- Consistent spacing, backgrounds -->
```

**Design Tokens:**
- Container max-widths: 640px (sm), 768px (md), 1024px (lg), 1280px (xl)
- Section padding: 4rem (desktop), 2rem (mobile)
- Grid gaps: 1rem, 1.5rem, 2rem

#### 1.2 Typography
```html
<!-- Headings -->
<h1 class="heading-1">Professional Invoices</h1>  <!-- 48px/3rem, bold -->
<h2 class="heading-2">Dashboard</h2>              <!-- 36px/2.25rem, semibold -->
<h3 class="heading-3">Recent Invoices</h3>        <!-- 24px/1.5rem, semibold -->
<h4 class="heading-4">Invoice #INV001</h4>        <!-- 20px/1.25rem, medium -->

<!-- Body Text -->
<p class="text-body-lg">Large body text</p>      <!-- 18px/1.125rem -->
<p class="text-body">Regular body text</p>        <!-- 16px/1rem -->
<p class="text-body-sm">Small body text</p>      <!-- 14px/0.875rem -->

<!-- Utility -->
<span class="text-muted">Secondary text</span>   <!-- gray-600 -->
<span class="text-error">Error message</span>    <!-- red-600 -->
```

**Design Tokens:**
- Font family: `-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto`
- Font weights: 400 (normal), 500 (medium), 600 (semibold), 700 (bold)
- Line heights: 1.2 (headings), 1.5 (body), 1.75 (relaxed)
- Letter spacing: -0.02em (headings)

---

### 2. Action Components (Week 1-2)

#### 2.1 Buttons
```html
<!-- Primary Actions -->
<button class="btn btn-primary">Create Invoice</button>
<button class="btn btn-primary btn-lg">Get Started</button>
<button class="btn btn-primary" disabled>Processing...</button>

<!-- Secondary Actions -->
<button class="btn btn-secondary">Cancel</button>
<button class="btn btn-outline">View Details</button>
<button class="btn btn-ghost">Learn More</button>

<!-- Destructive Actions -->
<button class="btn btn-danger">Delete Invoice</button>

<!-- Icon Buttons -->
<button class="btn btn-icon">
  <svg>...</svg>
</button>

<!-- Button Group -->
<div class="btn-group">
  <button class="btn">Edit</button>
  <button class="btn">Duplicate</button>
  <button class="btn btn-danger">Delete</button>
</div>
```

**Design Tokens:**
- Primary color: `#6366f1` (Indigo 500)
- Secondary color: `#64748b` (Slate 500)
- Danger color: `#ef4444` (Red 500)
- Padding: `0.5rem 1rem` (default), `0.75rem 1.5rem` (large)
- Border radius: `0.375rem` (6px)
- Font weight: 500 (medium)

**States:** Default, Hover, Active, Focus, Disabled, Loading

#### 2.2 Links
```html
<a href="#" class="link">Default link</a>
<a href="#" class="link link-primary">Primary link</a>
<a href="#" class="link link-muted">Muted link</a>
```

---

### 3. Form Components (Week 2)

#### 3.1 Input Fields
```html
<!-- Text Input -->
<div class="form-group">
  <label class="form-label" for="business-name">Business Name</label>
  <input type="text" id="business-name" class="form-input" placeholder="Acme Inc.">
  <span class="form-help">This will appear on invoices</span>
</div>

<!-- With Error -->
<div class="form-group has-error">
  <label class="form-label" for="email">Email</label>
  <input type="email" id="email" class="form-input" value="invalid">
  <span class="form-error">Please enter a valid email address</span>
</div>

<!-- Textarea -->
<textarea class="form-input" rows="4"></textarea>

<!-- Select -->
<select class="form-select">
  <option>USD - US Dollar</option>
  <option>EUR - Euro</option>
</select>

<!-- File Upload -->
<div class="form-file">
  <input type="file" id="logo" class="form-file-input">
  <label for="logo" class="form-file-label">
    <svg>...</svg>
    <span>Choose file or drag here</span>
  </label>
</div>
```

**Design Tokens:**
- Input height: `2.5rem` (40px)
- Input padding: `0.5rem 0.75rem`
- Border color: `#e2e8f0` (Slate 200)
- Border color (focus): `#6366f1` (Indigo 500)
- Border radius: `0.375rem`
- Error color: `#ef4444`

#### 3.2 Checkboxes & Radios
```html
<label class="form-checkbox">
  <input type="checkbox">
  <span>Remember me</span>
</label>

<label class="form-radio">
  <input type="radio" name="currency">
  <span>US Dollar (USD)</span>
</label>
```

---

### 4. Feedback Components (Week 1)

#### 4.1 Alerts & Messages
```html
<!-- Success Alert -->
<div class="alert alert-success">
  <svg class="alert-icon">...</svg>
  <div class="alert-content">
    <h4 class="alert-title">Invoice Created!</h4>
    <p>Invoice #INV001 has been created successfully.</p>
  </div>
  <button class="alert-close">&times;</button>
</div>

<!-- Error Alert -->
<div class="alert alert-error">
  <svg class="alert-icon">...</svg>
  <div>Please correct the errors below.</div>
</div>

<!-- Info Banner -->
<div class="alert alert-info">
  <svg class="alert-icon">...</svg>
  <div>Your trial expires in 7 days. Upgrade now!</div>
</div>
```

#### 4.2 Badges & Tags
```html
<span class="badge badge-success">Paid</span>
<span class="badge badge-warning">Unpaid</span>
<span class="badge badge-gray">Draft</span>
<span class="badge badge-outline">Pro</span>
```

**Design Tokens:**
- Success: `#10b981` (Green 500)
- Warning: `#f59e0b` (Amber 500)
- Error: `#ef4444` (Red 500)
- Info: `#3b82f6` (Blue 500)
- Padding: `0.25rem 0.75rem`
- Font size: `0.875rem` (14px)
- Border radius: `9999px` (pill shape)

#### 4.3 Toast Notifications
```javascript
// Already implemented in app.js!
toast.show('Invoice created successfully!', 'success');
toast.show('Error saving invoice', 'error');
```

---

### 5. Data Display Components (Week 2)

#### 5.1 Cards
```html
<!-- Basic Card -->
<div class="card">
  <div class="card-header">
    <h3 class="card-title">Invoice #INV001</h3>
    <span class="badge badge-success">Paid</span>
  </div>
  <div class="card-body">
    <p>Client: Acme Corporation</p>
    <p>Amount: $1,250.00</p>
  </div>
  <div class="card-footer">
    <button class="btn btn-secondary">View</button>
    <button class="btn btn-primary">Download PDF</button>
  </div>
</div>

<!-- Stats Card -->
<div class="card card-stat">
  <div class="card-stat-icon">
    <svg>...</svg>
  </div>
  <div class="card-stat-content">
    <p class="card-stat-label">Total Revenue</p>
    <h3 class="card-stat-value">$45,231</h3>
    <p class="card-stat-change">+12% from last month</p>
  </div>
</div>

<!-- Image Card -->
<div class="card">
  <img src="invoice-preview.jpg" class="card-img">
  <div class="card-body">...</div>
</div>
```

**Design Tokens:**
- Background: `#ffffff` (White)
- Border: `1px solid #e2e8f0` (Slate 200)
- Border radius: `0.5rem` (8px)
- Padding: `1.5rem`
- Shadow: `0 1px 3px rgba(0,0,0,0.1)`

#### 5.2 Tables
```html
<table class="table">
  <thead>
    <tr>
      <th>Invoice #</th>
      <th>Client</th>
      <th>Amount</th>
      <th>Status</th>
      <th>Actions</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>INV001</td>
      <td>Acme Corp</td>
      <td>$1,250.00</td>
      <td><span class="badge badge-success">Paid</span></td>
      <td>
        <button class="btn btn-sm btn-secondary">View</button>
      </td>
    </tr>
  </tbody>
</table>

<!-- Striped Table -->
<table class="table table-striped">...</table>

<!-- Hover Table -->
<table class="table table-hover">...</table>
```

#### 5.3 Empty States
```html
<div class="empty-state">
  <svg class="empty-state-icon">...</svg>
  <h3 class="empty-state-title">No invoices yet</h3>
  <p class="empty-state-description">Create your first invoice to get started</p>
  <button class="btn btn-primary">Create Invoice</button>
</div>
```

---

### 6. Navigation Components (Week 1)

#### 6.1 Navbar (Already Implemented)
```html
<nav class="navbar">
  <div class="navbar-brand">
    <img src="logo.svg" alt="Smart Invoice">
    <span>Smart Invoice</span>
  </div>
  <div class="navbar-menu">
    <a href="#" class="navbar-link">Features</a>
    <a href="#" class="navbar-link">Pricing</a>
  </div>
  <div class="navbar-actions">
    <button class="btn btn-secondary">Login</button>
    <button class="btn btn-primary">Get Started</button>
  </div>
</nav>
```

#### 6.2 Sidebar
```html
<aside class="sidebar">
  <nav class="sidebar-nav">
    <a href="#" class="sidebar-link active">
      <svg>...</svg>
      <span>Dashboard</span>
    </a>
    <a href="#" class="sidebar-link">
      <svg>...</svg>
      <span>Invoices</span>
      <span class="sidebar-badge">12</span>
    </a>
  </nav>
</aside>
```

#### 6.3 Tabs
```html
<div class="tabs">
  <button class="tab tab-active">Profile</button>
  <button class="tab">Business</button>
  <button class="tab">Security</button>
  <button class="tab">Notifications</button>
</div>
<div class="tab-content">
  <!-- Active tab content -->
</div>
```

#### 6.4 Breadcrumbs
```html
<nav class="breadcrumb">
  <a href="#">Home</a>
  <span>/</span>
  <a href="#">Invoices</a>
  <span>/</span>
  <span>INV001</span>
</nav>
```

---

### 7. Modal & Overlay Components (Week 2)

#### 7.1 Modal Dialog
```html
<div class="modal" id="delete-modal">
  <div class="modal-backdrop"></div>
  <div class="modal-content">
    <div class="modal-header">
      <h3 class="modal-title">Confirm Delete</h3>
      <button class="modal-close">&times;</button>
    </div>
    <div class="modal-body">
      <p>Are you sure you want to delete this invoice?</p>
    </div>
    <div class="modal-footer">
      <button class="btn btn-secondary">Cancel</button>
      <button class="btn btn-danger">Delete</button>
    </div>
  </div>
</div>
```

#### 7.2 Dropdown Menu
```html
<div class="dropdown">
  <button class="btn dropdown-toggle">
    Options
    <svg class="dropdown-icon">...</svg>
  </button>
  <div class="dropdown-menu">
    <a href="#" class="dropdown-item">Edit</a>
    <a href="#" class="dropdown-item">Duplicate</a>
    <hr class="dropdown-divider">
    <a href="#" class="dropdown-item text-error">Delete</a>
  </div>
</div>
```

---

### 8. Loading & Progress Components

#### 8.1 Spinners
```html
<div class="spinner"></div>
<div class="spinner spinner-lg"></div>
<div class="spinner spinner-sm"></div>
```

#### 8.2 Progress Bars
```html
<div class="progress">
  <div class="progress-bar" style="width: 75%"></div>
</div>

<div class="progress progress-sm">
  <div class="progress-bar bg-success" style="width: 100%"></div>
</div>
```

#### 8.3 Skeleton Loaders
```html
<div class="skeleton skeleton-text"></div>
<div class="skeleton skeleton-circle"></div>
<div class="skeleton skeleton-rect" style="height: 200px"></div>
```

---

## Existing CSS Audit

### Files to Consolidate

**`static/css/main.css` (945 lines):**
- Extract: Color variables → `design-tokens.css`
- Migrate: Utility classes → Tailwind equivalents
- Keep: Custom animations, complex components

**`static/css/enterprise-design-system.css` (958 lines):**
- Status: Already well-structured
- Action: Refactor into component modules
- Target: `components/cards.css`, `components/buttons.css`, etc.

**`static/css/internal-pages.css` (394 lines):**
- Status: Page-specific overrides
- Action: Most can be replaced with Tailwind utilities
- Keep: Complex layouts requiring custom CSS

---

## Design Tokens to Extract

### Colors
```css
:root {
  /* Brand */
  --color-primary: #6366f1;  /* Indigo 500 */
  --color-secondary: #64748b; /* Slate 500 */
  
  /* Semantic */
  --color-success: #10b981;  /* Green 500 */
  --color-warning: #f59e0b;  /* Amber 500 */
  --color-error: #ef4444;    /* Red 500 */
  --color-info: #3b82f6;     /* Blue 500 */
  
  /* Neutrals */
  --color-gray-50: #f9fafb;
  --color-gray-100: #f3f4f6;
  --color-gray-200: #e5e7eb;
  /* ... full gray scale */
  
  /* Text */
  --color-text-primary: #1f2937;
  --color-text-secondary: #6b7280;
  --color-text-muted: #9ca3af;
}
```

### Spacing
```css
:root {
  --spacing-xs: 0.25rem;    /* 4px */
  --spacing-sm: 0.5rem;     /* 8px */
  --spacing-md: 1rem;       /* 16px */
  --spacing-lg: 1.5rem;     /* 24px */
  --spacing-xl: 2rem;       /* 32px */
  --spacing-2xl: 3rem;      /* 48px */
  --spacing-3xl: 4rem;      /* 64px */
}
```

### Shadows
```css
:root {
  --shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
  --shadow-md: 0 4px 6px rgba(0,0,0,0.1);
  --shadow-lg: 0 10px 15px rgba(0,0,0,0.1);
  --shadow-xl: 0 20px 25px rgba(0,0,0,0.1);
}
```

### Border Radius
```css
:root {
  --radius-sm: 0.25rem;     /* 4px */
  --radius-md: 0.375rem;    /* 6px */
  --radius-lg: 0.5rem;      /* 8px */
  --radius-xl: 1rem;        /* 16px */
  --radius-full: 9999px;    /* Pill shape */
}
```

---

## Phase 1 Deliverables Checklist

### Week 1: Foundation
- [ ] Extract design tokens to CSS variables
- [ ] Create Tailwind config with extended theme
- [ ] Build foundation components (layout, typography, buttons)
- [ ] Set up Vite development environment
- [ ] Implement component documentation (HTML examples)

### Week 2: Expansion
- [ ] Build form components with validation states
- [ ] Create feedback components (alerts, badges, toasts)
- [ ] Implement navigation components (navbar, tabs, breadcrumbs)
- [ ] Build data display components (cards, tables, empty states)
- [ ] Create component library index page

### Deliverable Artifacts
- [ ] `static/css/design-tokens.css` - All design variables
- [ ] `static/css/components/` - Component CSS modules
- [ ] `tailwind.config.js` - Extended configuration
- [ ] `components-showcase.html` - Visual component library
- [ ] `vite.config.js` - Build configuration
- [ ] `COMPONENT_USAGE.md` - Developer guide

---

**Document Status:** ✅ Ready for Phase 1  
**Component Count:** 30+ reusable patterns identified  
**Coverage:** 95% of current UI needs
