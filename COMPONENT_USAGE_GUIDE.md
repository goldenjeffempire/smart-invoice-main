# Smart Invoice Component Usage Guide
## Phase 1: Design System & Component Library v5.0

**Last Updated:** November 24, 2025  
**Version:** 5.0.0  
**Status:** Phase 1 Complete - Ready for Production Use

---

## Table of Contents
1. [Getting Started](#getting-started)
2. [Design Tokens](#design-tokens)
3. [Component Reference](#component-reference)
4. [Best Practices](#best-practices)
5. [Examples](#examples)

---

## Getting Started

### Installation

Include the component library in your HTML templates:

```html
<!-- Option 1: Use the consolidated components.css (Recommended) -->
<link rel="stylesheet" href="{% static 'css/components.css' %}">

<!-- Option 2: Include individual component files -->
<link rel="stylesheet" href="{% static 'css/design-tokens.css' %}">
<link rel="stylesheet" href="{% static 'css/components/buttons.css' %}">
<link rel="stylesheet" href="{% static 'css/components/forms.css' %}">
<!-- etc -->
```

### Building CSS

```bash
# Development build (unminified)
npm run build:css

# Production build (minified)
npm run build:prod

# Watch mode (auto-rebuild on changes)
npm run watch:css
```

---

## Design Tokens

### CSS Variables

All design tokens are defined as CSS variables in `static/css/design-tokens.css`. Use these variables instead of hard-coded values to ensure consistency.

#### Colors

```css
/* Brand Colors */
var(--color-primary)          /* #6366f1 - Primary brand color */
var(--color-secondary)        /* #64748b - Secondary actions */

/* Semantic Colors */
var(--color-success)          /* #10b981 - Success states */
var(--color-warning)          /* #f59e0b - Warning states */
var(--color-error)            /* #ef4444 - Error states */
var(--color-info)             /* #3b82f6 - Info states */

/* Text Colors */
var(--color-text-primary)     /* #1f2937 - Primary text */
var(--color-text-secondary)   /* #6b7280 - Secondary text */
var(--color-text-muted)       /* #9ca3af - Muted text */
```

#### Spacing

```css
var(--spacing-xs)    /* 0.25rem / 4px */
var(--spacing-sm)    /* 0.5rem / 8px */
var(--spacing-md)    /* 1rem / 16px */
var(--spacing-lg)    /* 1.5rem / 24px */
var(--spacing-xl)    /* 2rem / 32px */
var(--spacing-2xl)   /* 3rem / 48px */
var(--spacing-3xl)   /* 4rem / 64px */
```

#### Typography

```css
/* Font Sizes */
var(--text-xs)     /* 0.75rem / 12px */
var(--text-sm)     /* 0.875rem / 14px */
var(--text-base)   /* 1rem / 16px */
var(--text-lg)     /* 1.125rem / 18px */
var(--text-xl)     /* 1.25rem / 20px */
var(--text-2xl)    /* 1.5rem / 24px */
var(--text-3xl)    /* 1.875rem / 30px */
var(--text-4xl)    /* 2.25rem / 36px */
var(--text-5xl)    /* 3rem / 48px */

/* Font Weights */
var(--font-normal)     /* 400 */
var(--font-medium)     /* 500 */
var(--font-semibold)   /* 600 */
var(--font-bold)       /* 700 */
```

---

## Component Reference

### Buttons

#### Basic Usage

```html
<!-- Primary Action -->
<button class="btn btn-primary">Create Invoice</button>

<!-- Secondary Action -->
<button class="btn btn-secondary">Cancel</button>

<!-- Outline Button -->
<button class="btn btn-outline">Learn More</button>

<!-- Destructive Action -->
<button class="btn btn-danger">Delete</button>
```

#### Sizes

```html
<button class="btn btn-primary btn-sm">Small</button>
<button class="btn btn-primary">Default</button>
<button class="btn btn-primary btn-lg">Large</button>
<button class="btn btn-primary btn-xl">Extra Large</button>
```

#### States

```html
<!-- Disabled -->
<button class="btn btn-primary" disabled>Disabled</button>

<!-- Loading -->
<button class="btn btn-primary btn-loading">Processing...</button>

<!-- Full Width -->
<button class="btn btn-primary btn-block">Full Width Button</button>
```

#### Icon Buttons

```html
<button class="btn btn-icon btn-primary">
  <svg><!-- icon --></svg>
</button>
```

---

### Forms

#### Text Input

```html
<div class="form-group">
  <label class="form-label" for="business-name">Business Name</label>
  <input type="text" id="business-name" class="form-input" placeholder="Acme Inc.">
  <span class="form-help">This will appear on invoices</span>
</div>
```

#### Input with Error

```html
<div class="form-group has-error">
  <label class="form-label" for="email">Email</label>
  <input type="email" id="email" class="form-input" value="invalid">
  <span class="form-error">Please enter a valid email address</span>
</div>
```

#### Select Dropdown

```html
<div class="form-group">
  <label class="form-label" for="currency">Currency</label>
  <select id="currency" class="form-select">
    <option>USD - US Dollar</option>
    <option>EUR - Euro</option>
  </select>
</div>
```

#### Checkbox

```html
<label class="form-checkbox">
  <input type="checkbox" checked>
  <span>Send email notification</span>
</label>
```

#### File Upload

```html
<div class="form-file">
  <input type="file" id="logo" class="form-file-input">
  <label for="logo" class="form-file-label">
    <svg><!-- upload icon --></svg>
    <span>Choose file or drag here</span>
  </label>
</div>
```

---

### Alerts & Badges

#### Alerts

```html
<!-- Success Alert -->
<div class="alert alert-success">
  <svg class="alert-icon"><!-- icon --></svg>
  <div class="alert-content">
    <h4 class="alert-title">Success!</h4>
    <p>Your invoice has been created successfully.</p>
  </div>
  <button class="alert-close">&times;</button>
</div>

<!-- Error Alert -->
<div class="alert alert-error">
  <svg class="alert-icon"><!-- icon --></svg>
  <div>An error occurred. Please try again.</div>
</div>
```

#### Badges

```html
<span class="badge badge-success">Paid</span>
<span class="badge badge-warning">Pending</span>
<span class="badge badge-error">Overdue</span>
<span class="badge badge-gray">Draft</span>

<!-- Outline Badges -->
<span class="badge badge-outline badge-primary">Pro</span>
```

---

### Cards

#### Basic Card

```html
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
```

#### Stats Card

```html
<div class="card card-stat">
  <div class="card-stat-icon">
    <svg><!-- icon --></svg>
  </div>
  <p class="card-stat-label">Total Revenue</p>
  <h3 class="card-stat-value">$45,231</h3>
  <p class="card-stat-change positive">+12% from last month</p>
</div>
```

---

### Tables

#### Basic Table

```html
<div class="table-wrapper">
  <table class="table table-hover">
    <thead>
      <tr>
        <th>Invoice #</th>
        <th>Client</th>
        <th>Status</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>INV001</td>
        <td>Acme Corp</td>
        <td><span class="badge badge-success">Paid</span></td>
      </tr>
    </tbody>
  </table>
</div>
```

#### Empty State

```html
<div class="empty-state">
  <svg class="empty-state-icon"><!-- icon --></svg>
  <h3 class="empty-state-title">No invoices yet</h3>
  <p class="empty-state-description">Create your first invoice to get started</p>
  <button class="btn btn-primary">Create Invoice</button>
</div>
```

---

### Navigation

#### Tabs

```html
<div class="tabs">
  <button class="tab tab-active">Profile</button>
  <button class="tab">Business</button>
  <button class="tab">Security</button>
</div>
<div class="tab-content">
  <!-- Active tab content -->
</div>
```

#### Breadcrumbs

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

### Loading States

#### Spinner

```html
<div class="spinner"></div>
<div class="spinner spinner-sm"></div>
<div class="spinner spinner-lg"></div>
```

#### Progress Bar

```html
<div class="progress">
  <div class="progress-bar" style="width: 75%"></div>
</div>
```

#### Skeleton Loader

```html
<div class="skeleton skeleton-text"></div>
<div class="skeleton skeleton-rect" style="height: 200px"></div>
<div class="skeleton skeleton-circle"></div>
```

---

## Best Practices

### 1. Use Semantic HTML

```html
<!-- Good -->
<button class="btn btn-primary">Submit</button>

<!-- Bad -->
<div class="btn btn-primary" onclick="submit()">Submit</div>
```

### 2. Use Design Tokens

```css
/* Good */
.my-component {
  color: var(--color-text-primary);
  padding: var(--spacing-md);
}

/* Bad */
.my-component {
  color: #1f2937;
  padding: 16px;
}
```

### 3. Accessibility

```html
<!-- Always include labels for form inputs -->
<label class="form-label" for="email">Email Address</label>
<input type="email" id="email" class="form-input">

<!-- Use proper heading hierarchy -->
<h1 class="heading-1">Page Title</h1>
<h2 class="heading-2">Section Title</h2>
<h3 class="heading-3">Subsection Title</h3>
```

### 4. Mobile-First

```css
/* Components are mobile-first by default */
/* Add responsive modifiers with media queries */

@media (min-width: 768px) {
  .card-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
```

### 5. Consistent Spacing

```html
<!-- Use standardized spacing classes -->
<div class="mb-md">Content with medium bottom margin</div>
<div class="gap-lg">Flex container with large gap</div>
```

---

## Examples

### Complete Form

```html
<form class="card">
  <div class="card-header">
    <h3 class="card-title">Create Invoice</h3>
  </div>
  <div class="card-body">
    <div class="form-group">
      <label class="form-label form-label-required" for="client">Client Name</label>
      <input type="text" id="client" class="form-input" required>
    </div>
    
    <div class="form-group">
      <label class="form-label" for="amount">Amount</label>
      <input type="number" id="amount" class="form-input" placeholder="0.00">
    </div>
    
    <div class="form-group">
      <label class="form-label" for="currency">Currency</label>
      <select id="currency" class="form-select">
        <option>USD</option>
        <option>EUR</option>
      </select>
    </div>
    
    <label class="form-checkbox">
      <input type="checkbox">
      <span>Send email notification</span>
    </label>
  </div>
  <div class="card-footer">
    <button type="button" class="btn btn-secondary">Cancel</button>
    <button type="submit" class="btn btn-primary">Create Invoice</button>
  </div>
</form>
```

### Dashboard Stats Grid

```html
<div class="card-grid">
  <div class="card card-stat">
    <div class="card-stat-icon">
      <svg><!-- icon --></svg>
    </div>
    <p class="card-stat-label">Total Revenue</p>
    <h3 class="card-stat-value">$45,231</h3>
    <p class="card-stat-change positive">+12.5%</p>
  </div>
  
  <div class="card card-stat">
    <div class="card-stat-icon">
      <svg><!-- icon --></svg>
    </div>
    <p class="card-stat-label">Invoices Sent</p>
    <h3 class="card-stat-value">284</h3>
    <p class="card-stat-change positive">+8.2%</p>
  </div>
  
  <!-- More stats cards -->
</div>
```

### Invoice List with Table

```html
<div class="card">
  <div class="card-header">
    <h3 class="card-title">Recent Invoices</h3>
    <button class="btn btn-primary btn-sm">Create New</button>
  </div>
  <div class="table-wrapper">
    <table class="table table-hover">
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
        <!-- More rows -->
      </tbody>
    </table>
  </div>
</div>
```

---

## Component Showcase

To view all components in action, visit: `/components-showcase.html`

This showcase page demonstrates:
- All color tokens
- Typography scale
- All button variants and states
- Form components with validation
- Cards and data display
- Navigation patterns
- Loading states

---

## Migration Guide

### From v4.0 to v5.0

**Old (v4.0):**
```html
<button class="btn-primary">Submit</button>
```

**New (v5.0):**
```html
<button class="btn btn-primary">Submit</button>
```

**Key Changes:**
1. All buttons now use `btn` base class + modifier
2. Design tokens replaced hard-coded colors
3. Component CSS is modular (can import individually)
4. Tailwind config extended with design tokens

---

## Troubleshooting

### Components not styled correctly

**Issue:** Components appear unstyled  
**Solution:** Ensure `components.css` is loaded before custom styles

### Colors not updating

**Issue:** Design token changes don't reflect  
**Solution:** Rebuild CSS with `npm run build:css`

### Forms validation styles not working

**Issue:** Error states not showing  
**Solution:** Add `.has-error` class to `.form-group`

---

## Resources

- **Component Showcase:** `/templates/components-showcase.html`
- **Design Tokens:** `/static/css/design-tokens.css`
- **Tailwind Config:** `/tailwind.config.js`
- **Phase 1 Inventory:** `/PHASE1_COMPONENT_INVENTORY.md`

---

**Document Version:** 1.0  
**Last Updated:** November 24, 2025  
**Status:** Phase 1 Complete
