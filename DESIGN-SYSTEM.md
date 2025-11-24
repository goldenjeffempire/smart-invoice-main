# Smart Invoice - Enterprise Design System v3.0

**Production-ready, WCAG AAA compliant, future-proof design system**

## Overview

The Enterprise Design System consolidates all design tokens, components, and patterns into a single, authoritative source. This eliminates the fragmentation that existed across multiple CSS files and ensures consistency throughout the application.

## Design Tokens

### Color Palette

#### Primary Colors (Indigo)
- **Primary 50-900**: Professional indigo palette from `#eef2ff` to `#312e81`
- **Usage**: Brand identity, CTAs, links, interactive elements
- **Main Brand Color**: `--color-primary-600` (#4f46e5)

#### Semantic Colors
- **Success**: `#10b981` (Green) - For positive states, confirmations
- **Warning**: `#f59e0b` (Amber) - For warnings, caution states
- **Error**: `#ef4444` (Red) - For errors, destructive actions
- **Info**: `#3b82f6` (Blue) - For informational messages

#### Neutrals (Gray Scale)
- **Gray 50-900**: Professional gray palette from `#fafbfc` to `#0f172a`
- **Usage**: Text, borders, backgrounds, shadows

### Typography

#### Font Families
- **Sans-serif**: `Inter` (with system fallbacks)
- **Monospace**: `JetBrains Mono`, `Fira Code` (for code blocks)

#### Font Sizes (Fluid & Responsive)
```css
--text-xs: 12px → 13px
--text-sm: 14px → 15px
--text-base: 16px → 17px
--text-lg: 18px → 20px
--text-xl: 20px → 24px
--text-2xl: 24px → 30px
--text-3xl: 30px → 36px
--text-4xl: 36px → 48px
--text-5xl: 48px → 60px
--text-6xl: 60px → 72px
--text-7xl: 72px → 96px
```

#### Font Weights
- Light (300), Normal (400), Medium (500), Semibold (600), Bold (700), Extrabold (800), Black (900)

#### Line Heights
- **None** (1), **Tight** (1.25), **Snug** (1.375), **Normal** (1.5), **Relaxed** (1.625), **Loose** (2)

### Spacing Scale (4px base unit)

```
--space-1: 4px
--space-2: 8px
--space-3: 12px
--space-4: 16px
--space-6: 24px
--space-8: 32px
--space-10: 40px
--space-12: 48px
--space-16: 64px
--space-20: 80px
--space-24: 96px
--space-32: 128px
```

### Border Radius
```
--radius-sm: 4px
--radius-base: 6px
--radius-md: 8px
--radius-lg: 12px
--radius-xl: 16px
--radius-2xl: 24px
--radius-3xl: 32px
--radius-full: 9999px
```

### Shadows (Elevation System)
```
--shadow-xs: Minimal elevation
--shadow-sm: Small elevation (default cards)
--shadow-base: Base elevation
--shadow-md: Medium elevation (hover states)
--shadow-lg: Large elevation (modals, popovers)
--shadow-xl: Extra large elevation
--shadow-2xl: Maximum elevation
--shadow-inner: Inner shadow (inset)
```

### Transitions
```
--transition-fast: 150ms (hover effects)
--transition-base: 200ms (default)
--transition-slow: 300ms (complex animations)
--transition-slower: 500ms (major transitions)
```

## Component Library

### Buttons

#### Variants
- **Primary**: `btn btn-primary` - Main CTAs
- **Secondary**: `btn btn-secondary` - Secondary actions
- **Outline**: `btn btn-outline` - Tertiary actions
- **Ghost**: `btn btn-ghost` - Minimal actions
- **Success**: `btn btn-success` - Positive actions
- **Danger**: `btn btn-danger` - Destructive actions

#### Sizes
- **Small**: `btn btn-sm`
- **Default**: `btn`
- **Large**: `btn btn-lg`
- **Extra Large**: `btn btn-xl`

#### Modifiers
- **Block**: `btn btn-block` - Full width
- **Icon Only**: `btn btn-icon-only` - Square icon button

#### Example
```html
<button class="btn btn-primary btn-lg">Get Started Free</button>
<button class="btn btn-secondary">Learn More</button>
<button class="btn btn-outline btn-sm">Cancel</button>
```

### Cards

#### Base Card
```html
<div class="card">
    <div class="card-header">
        <h3 class="card-title">Card Title</h3>
        <p class="card-description">Optional description</p>
    </div>
    <div class="card-body">
        Card content goes here
    </div>
    <div class="card-footer">
        <button class="btn btn-primary">Action</button>
    </div>
</div>
```

#### Variants
- **Hover Effect**: `card card-hover` - Lifts on hover
- **Glass Effect**: `card card-glass` - Glassmorphism effect
- **Elevated**: `card card-elevated` - Larger shadow

### Forms

#### Input Fields
```html
<div class="form-group">
    <label class="form-label form-label-required">Email</label>
    <input type="email" class="form-input" placeholder="you@example.com">
    <span class="form-help">We'll never share your email</span>
</div>
```

#### States
- **Error**: `form-input form-input-error`
- **Success**: `form-input form-input-success`
- **Disabled**: `form-input:disabled`

#### Components
- **Input**: `form-input`
- **Textarea**: `form-textarea`
- **Select**: `form-select`
- **Checkbox**: `form-checkbox`
- **Radio**: `form-radio`

### Badges

```html
<span class="badge badge-primary">New</span>
<span class="badge badge-success">Active</span>
<span class="badge badge-warning">Pending</span>
<span class="badge badge-error">Failed</span>
<span class="badge badge-info">Info</span>
```

### Alerts

```html
<div class="alert alert-success">
    Operation completed successfully!
</div>
<div class="alert alert-error">
    An error occurred. Please try again.
</div>
<div class="alert alert-warning">
    Please verify your email address.
</div>
<div class="alert alert-info">
    Your invoice has been sent.
</div>
```

## Utility Classes

### Spacing
```css
.mt-4    /* margin-top: 1rem (16px) */
.mb-6    /* margin-bottom: 1.5rem (24px) */
.py-8    /* padding-top & bottom: 2rem (32px) */
.px-4    /* padding-left & right: 1rem (16px) */
.gap-4   /* gap: 1rem (16px) */
```

### Typography
```css
.text-sm         /* Small text */
.text-base       /* Base text size */
.text-lg         /* Large text */
.font-semibold   /* Semibold weight */
.font-bold       /* Bold weight */
.text-primary    /* Primary text color */
.text-secondary  /* Secondary text color */
.text-center     /* Center align */
```

### Display & Layout
```css
.flex            /* display: flex */
.flex-col        /* flex-direction: column */
.items-center    /* align-items: center */
.justify-between /* justify-content: space-between */
.grid            /* display: grid */
.grid-cols-3     /* 3 column grid */
.gap-4           /* grid gap */
```

### Border & Shadows
```css
.rounded-lg      /* border-radius: 12px */
.rounded-full    /* border-radius: 9999px */
.shadow-md       /* Medium shadow */
.shadow-lg       /* Large shadow */
```

### Responsive Classes
```css
.sm:block        /* Show on small screens+ */
.md:flex         /* Flex on medium screens+ */
.lg:grid-cols-4  /* 4 columns on large screens+ */
```

## Accessibility Features

### Skip Links
```html
<a href="#main-content" class="skip-link">Skip to main content</a>
```

### Screen Reader Only
```html
<span class="sr-only">For screen readers only</span>
```

### Focus States
- All interactive elements have `:focus-visible` states
- Focus ring: 2px solid indigo outline with 2px offset
- Use `.focus-ring` class for custom focus states

### Reduced Motion
Automatically reduces animations for users with `prefers-reduced-motion` enabled.

### High Contrast Mode
Adjusts border colors for better visibility in high contrast mode.

## Container & Layout

### Container
```html
<div class="container">
    <!-- Content automatically centered with max-width -->
</div>
```

**Breakpoints:**
- **sm**: 640px
- **md**: 768px
- **lg**: 1024px
- **xl**: 1280px
- **2xl**: 1536px

### Section Spacing
```html
<section class="section">
    <!-- Automatic vertical padding: 64px mobile, 96px desktop -->
</section>
```

## Best Practices

### 1. Use Design Tokens
❌ **Don't**: `color: #6366f1;`  
✅ **Do**: `color: var(--color-primary-600);`

### 2. Use Component Classes
❌ **Don't**: Write custom button styles  
✅ **Do**: Use `.btn .btn-primary`

### 3. Use Spacing Scale
❌ **Don't**: `margin-top: 15px;`  
✅ **Do**: `margin-top: var(--space-4);` or `.mt-4`

### 4. Follow Accessibility Guidelines
- Always include ARIA labels
- Use semantic HTML
- Ensure sufficient color contrast (WCAG AAA)
- Test with keyboard navigation
- Support screen readers

### 5. Responsive Design
- Mobile-first approach
- Use fluid typography (clamp)
- Test on all breakpoints
- Use responsive utility classes

## File Structure

```
static/css/
├── enterprise-design-system.css  ← Main design system (USE THIS)
├── landing-animations.css         ← Landing page animations
├── modern-animations.css          ← Additional animations
├── accessibility.css              ← A11y-specific styles
├── internal-pages.css             ← Internal page styles
├── production.css                 ← Production optimizations
└── tailwind.output.css            ← Tailwind utilities
```

### Deprecated Files (Do Not Use)
- ~~design-system.css~~ - Replaced by enterprise-design-system.css
- ~~unified-design-system.css~~ - Replaced by enterprise-design-system.css
- ~~design-system-integration.css~~ - Replaced by enterprise-design-system.css
- ~~performance.css~~ - Merged into enterprise-design-system.css

## Migration Guide

### From Old Design System

**Old (Sky Blue Primary):**
```css
--color-primary-500: #0ea5e9; /* Old sky blue */
```

**New (Indigo Primary):**
```css
--color-primary-500: #6366f1; /* New indigo */
```

All components automatically use the new color palette. No code changes required unless you have hardcoded color values (which you shouldn't!).

## Support

For questions or issues with the design system:
1. Check this documentation first
2. Review the component examples
3. Inspect the CSS file for detailed implementation
4. Contact the development team

---

**Last Updated**: November 24, 2025  
**Version**: 3.0  
**Maintained By**: Smart Invoice Engineering Team
