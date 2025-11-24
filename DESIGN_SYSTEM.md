# Smart Invoice Design System
**Version:** 1.0.0  
**Date:** November 23, 2025

## Color Palette

### Primary Colors
```css
--color-primary-50: #eef2ff;
--color-primary-100: #e0e7ff;
--color-primary-200: #c7d2fe;
--color-primary-300: #a5b4fc;
--color-primary-400: #818cf8;
--color-primary-500: #6366f1;  /* Primary brand color */
--color-primary-600: #4f46e5;
--color-primary-700: #4338ca;
--color-primary-800: #3730a3;
--color-primary-900: #312e81;
```

### Secondary Colors
```css
--color-secondary-500: #8b5cf6;  /* Purple accent */
--color-accent-500: #ec4899;      /* Pink accent */
```

### Semantic Colors
```css
--color-success: #10b981;
--color-warning: #f59e0b;
--color-error: #ef4444;
--color-info: #3b82f6;
```

### Neutral Colors
```css
--color-gray-50: #f9fafb;
--color-gray-100: #f3f4f6;
--color-gray-200: #e5e7eb;
--color-gray-300: #d1d5db;
--color-gray-400: #9ca3af;
--color-gray-500: #6b7280;
--color-gray-600: #4b5563;
--color-gray-700: #374151;
--color-gray-800: #1f2937;
--color-gray-900: #111827;
```

## Typography

### Font Families
- **Primary:** Inter, system-ui, -apple-system, sans-serif
- **Monospace:** 'Courier New', monospace

### Font Sizes
```css
--text-xs: 0.75rem;     /* 12px */
--text-sm: 0.875rem;    /* 14px */
--text-base: 1rem;      /* 16px */
--text-lg: 1.125rem;    /* 18px */
--text-xl: 1.25rem;     /* 20px */
--text-2xl: 1.5rem;     /* 24px */
--text-3xl: 1.875rem;   /* 30px */
--text-4xl: 2.25rem;    /* 36px */
--text-5xl: 3rem;       /* 48px */
--text-6xl: 3.75rem;    /* 60px */
```

### Font Weights
- **Normal:** 400
- **Medium:** 500
- **Semibold:** 600
- **Bold:** 700
- **Extrabold:** 800
- **Black:** 900

### Line Heights
- **Tight:** 1.25
- **Snug:** 1.375
- **Normal:** 1.5
- **Relaxed:** 1.625
- **Loose:** 2

## Spacing System

### Base Unit: 0.25rem (4px)

```css
--space-1: 0.25rem;   /* 4px */
--space-2: 0.5rem;    /* 8px */
--space-3: 0.75rem;   /* 12px */
--space-4: 1rem;      /* 16px */
--space-5: 1.25rem;   /* 20px */
--space-6: 1.5rem;    /* 24px */
--space-8: 2rem;      /* 32px */
--space-10: 2.5rem;   /* 40px */
--space-12: 3rem;     /* 48px */
--space-16: 4rem;     /* 64px */
--space-20: 5rem;     /* 80px */
--space-24: 6rem;     /* 96px */
```

## Border Radius

```css
--radius-sm: 0.125rem;   /* 2px */
--radius-base: 0.25rem;  /* 4px */
--radius-md: 0.375rem;   /* 6px */
--radius-lg: 0.5rem;     /* 8px */
--radius-xl: 0.75rem;    /* 12px */
--radius-2xl: 1rem;      /* 16px */
--radius-3xl: 1.5rem;    /* 24px */
--radius-full: 9999px;   /* Fully rounded */
```

## Shadows

```css
--shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
--shadow-base: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1);
--shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
--shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
--shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);
--shadow-2xl: 0 25px 50px -12px rgb(0 0 0 / 0.25);
```

## Animation System

### Timing Functions
```css
--ease-linear: linear;
--ease-in: cubic-bezier(0.4, 0, 1, 1);
--ease-out: cubic-bezier(0, 0, 0.2, 1);
--ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
```

### Durations
```css
--duration-75: 75ms;
--duration-100: 100ms;
--duration-150: 150ms;
--duration-200: 200ms;
--duration-300: 300ms;
--duration-500: 500ms;
--duration-700: 700ms;
--duration-1000: 1000ms;
```

### Keyframe Animations
- **fadeIn:** Opacity 0 → 1
- **fadeOut:** Opacity 1 → 0
- **slideUp:** TranslateY(20px) → 0
- **slideDown:** TranslateY(-20px) → 0
- **slideRight:** TranslateX(-20px) → 0
- **slideLeft:** TranslateX(20px) → 0
- **scaleUp:** Scale(0.95) → 1
- **bounce:** Subtle bounce effect
- **pulse:** Subtle scaling pulse
- **shimmer:** Gradient shimmer effect

## Component Library

### Buttons

#### Primary Button
```html
<button class="btn btn-primary">
  Primary Action
</button>
```
- Background: Primary-600
- Hover: Primary-700
- Padding: 12px 24px
- Border radius: lg
- Shadow: md
- Transition: 200ms

#### Secondary Button
- Border: 2px Primary-600
- Color: Primary-600
- Background: Transparent
- Hover: Primary-50 background

#### Ghost Button
- No border
- Color: Gray-700
- Hover: Gray-100 background

### Cards

#### Standard Card
```html
<div class="card">
  <div class="card-header">Title</div>
  <div class="card-body">Content</div>
  <div class="card-footer">Actions</div>
</div>
```
- Background: White
- Border: 1px Gray-200
- Border radius: xl
- Shadow: sm
- Hover: shadow-md transition

### Forms

#### Input Field
```html
<input class="input-field" type="text" placeholder="Enter text">
```
- Border: 1px Gray-300
- Focus: 2px Primary-500 ring
- Padding: 10px 14px
- Border radius: md

#### Label
```html
<label class="label-field">Field Name</label>
```
- Font size: sm
- Font weight: medium
- Color: Gray-700
- Margin bottom: 2

### Badges

#### Status Badges
- **Success:** Green background, white text
- **Warning:** Yellow background, dark text
- **Error:** Red background, white text
- **Info:** Blue background, white text
- **Neutral:** Gray background, dark text

### Icons
- Size: 20px × 20px (base)
- Stroke width: 2px
- Color: Inherit from parent

## Responsive Breakpoints

```css
--breakpoint-sm: 640px;   /* Mobile landscape */
--breakpoint-md: 768px;   /* Tablet portrait */
--breakpoint-lg: 1024px;  /* Tablet landscape */
--breakpoint-xl: 1280px;  /* Desktop */
--breakpoint-2xl: 1536px; /* Large desktop */
```

## Grid System

### Container
- Max width: 1280px
- Padding: 20px (mobile), 40px (desktop)
- Margin: 0 auto

### Grid Columns
- 12-column grid system
- Gap: 24px (desktop), 16px (mobile)

## Accessibility Guidelines

### Color Contrast
- **Normal text:** Minimum 4.5:1 ratio
- **Large text:** Minimum 3:1 ratio
- **UI components:** Minimum 3:1 ratio

### Focus States
- All interactive elements must have visible focus states
- Focus ring: 2px Primary-500
- Focus ring offset: 2px

### Motion
- Respect `prefers-reduced-motion` media query
- Provide alternatives for animated content

## Usage Examples

### Hero Section
```html
<section class="hero-section">
  <div class="container">
    <h1 class="hero-title">Welcome to Smart Invoice</h1>
    <p class="hero-subtitle">Professional invoicing made simple</p>
    <div class="hero-actions">
      <button class="btn btn-primary btn-lg">Get Started</button>
      <button class="btn btn-secondary btn-lg">Learn More</button>
    </div>
  </div>
</section>
```

### Feature Card
```html
<div class="feature-card">
  <div class="feature-icon">💰</div>
  <h3 class="feature-title">Multi-Currency Support</h3>
  <p class="feature-description">Invoice clients in any currency worldwide</p>
</div>
```

### Stat Card
```html
<div class="stat-card">
  <div class="stat-label">Total Revenue</div>
  <div class="stat-value">$24,500</div>
  <div class="stat-change positive">+12.5%</div>
</div>
```

## Component States

### Interactive States
1. **Default:** Base state
2. **Hover:** Cursor interaction
3. **Active:** Click/press state
4. **Focus:** Keyboard focus
5. **Disabled:** Non-interactive state
6. **Loading:** Async operation state

### Feedback States
1. **Success:** Green theme
2. **Error:** Red theme
3. **Warning:** Yellow theme
4. **Info:** Blue theme

## Implementation Guidelines

### CSS Class Naming
- Use BEM methodology: `block__element--modifier`
- Keep classes semantic and descriptive
- Avoid overly specific selectors

### Performance
- Use CSS transforms for animations (GPU-accelerated)
- Minimize repaints and reflows
- Lazy load images below the fold
- Use will-change sparingly

### Maintainability
- Keep related styles together
- Use CSS variables for theming
- Document complex styling decisions
- Follow the design system consistently

---
*Design System created for Smart Invoice Platform*
*Ensures consistency, accessibility, and scalability*
