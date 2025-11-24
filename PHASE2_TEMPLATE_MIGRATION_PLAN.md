# PHASE 2: Template Migration & Enhanced Landing Page

**Estimated Effort:** 100-200 tool calls  
**Timeline:** 2-3 weeks

---

## PART A: Legacy Template Cleanup & Migration

### Step 1: Template Audit (5-10 tool calls)
- Identify all 15+ templates currently in use
- Document template dependencies and imports
- List duplicate components across templates
- Map current page structure to new component system

### Step 2: Create Template Base (10-15 tool calls)
- Create `base-modern.html` with new component architecture
- Implement navbar and footer as reusable components
- Set up template inheritance structure
- Create layout blocks for common patterns

### Step 3: Migrate Core Templates (50-100 tool calls)
- Dashboard template
- Invoice creation template
- Invoice detail template
- Settings templates (5 variants)
- Admin templates (3 variants)
- Auth templates (signup, login, password reset)

### Step 4: Migrate Static Pages (20-30 tool calls)
- Home/landing page (enhanced in Part B)
- Features page
- Pricing page
- Templates page
- FAQ page
- Contact page
- About page
- Careers page
- Legal pages (terms, privacy)
- Support pages

### Step 5: Remove Legacy Assets (10-20 tool calls)
- Delete unused CSS files
- Remove duplicate images
- Clean up old JS files
- Archive legacy templates (backup only)

---

## PART B: Landing Page Modern Redesign

### Hero Section (20-30 tool calls)
- Pixel-perfect headline + subheadline
- Professional background (gradient or image)
- Primary CTA button (Sign Up, Demo)
- Secondary CTA (Docs, Learn More)
- Optional: animated background or scroll-triggered animations

### Feature Showcase (30-40 tool calls)
- Feature cards (6-8 key features)
- Icons and descriptions
- Interactive feature tabs or accordion
- Benefits section with icons and copy

### Pricing Section (15-20 tool calls)
- 3-tier pricing matrix
- Feature comparison table
- Tier cards with CTAs
- FAQ toggle items
- Money-back guarantee banner

### Social Proof & Trust (15-20 tool calls)
- Testimonials carousel or cards
- Company logos (if applicable)
- Statistics/metrics
- Trust badges (SSL, certifications)

### Newsletter Signup (10-15 tool calls)
- Email capture form
- Success/error messaging
- Mobile-responsive design
- GDPR compliance messaging

### Footer (10-15 tool calls)
- Company info + links
- Product links
- Resources section
- Contact information
- Social media links
- Legal links

### SEO & Metadata (15-20 tool calls)
- Meta tags (title, description, keywords)
- Open Graph tags
- Twitter card tags
- JSON-LD structured data (Organization, SoftwareApplication)
- sitemap.xml generation
- robots.txt configuration
- Canonical URLs

### Micro-interactions & Animation (20-30 tool calls)
- CSS transitions on hover states
- Intersection Observer for scroll animations
- Smooth scrolling between sections
- Button click feedback
- Form validation animations
- Optional: Lottie animations for illustrations

---

## PART C: Critical App Flow Improvements

### Dashboard Page (15-20 tool calls)
- Redesigned layout with new component system
- Improved invoice list table
- Dashboard cards for key metrics
- Quick action buttons
- Filters and search improvements

### Invoice Creation Page (20-30 tool calls)
- Multi-step form redesign
- Form field validation improvements
- Line items table with add/remove
- Customer selection/creation
- Payment terms selector
- Template selector

### Invoice Detail Page (15-20 tool calls)
- Clean invoice display
- Actions sidebar (edit, delete, email, PDF)
- Status indicator
- Payment information
- Line items display

---

## Technical Implementation

### Component Usage in Templates
```html
<!-- Example: Using new design system in templates -->
{% load static %}

{% include "components/navbar.html" %}

<main class="container-lg py-section-padding-mobile">
  <section class="btn-group">
    <button class="btn btn-primary btn-lg">Primary Action</button>
    <button class="btn btn-secondary">Secondary</button>
  </section>
</main>

{% include "components/footer.html" %}
```

### CSS Class Conventions
- Utility classes: `.py-section-padding-mobile`
- Component classes: `.btn`, `.card`, `.input`
- State classes: `.is-active`, `.is-disabled`, `.is-error`
- Responsive classes: `.md-grid-2`, `.lg-grid-3`

### JavaScript Enhancement Points
- Form validation with error display
- Dropdown interactions
- Accordion toggling
- Intersection Observer animations
- Smooth scroll behavior

---

## Testing Strategy

### Visual Testing (10-15 tool calls)
- Component showcase verification
- Responsive design testing (mobile, tablet, desktop)
- Dark mode verification
- Cross-browser testing

### Functional Testing (10-15 tool calls)
- Form submissions
- Navigation flows
- Modal interactions
- Mobile responsiveness

### Performance Testing (5-10 tool calls)
- Page load time metrics
- CSS specificity analysis
- Unused CSS detection
- Asset optimization

---

## Deliverables

| Item | Status | File/URL |
|---|---|---|
| Template audit report | Pending | `PHASE2_TEMPLATE_AUDIT.md` |
| Base modern template | Pending | `templates/base-modern.html` |
| Migrated app templates | Pending | `templates/pages/*.html` |
| Enhanced landing page | Pending | `templates/pages/home.html` |
| Component showcase | ✅ | `/components-showcase/` |
| Landing page optimizations | Pending | SEO, performance metrics |

---

## Success Criteria

- ✅ All 15+ templates migrated to new component system
- ✅ Landing page passes professional design review
- ✅ Mobile-responsive on all breakpoints
- ✅ Page load time < 3s (Core Web Vitals)
- ✅ Accessibility WCAG 2.1 AA compliance
- ✅ SEO metadata complete
- ✅ All interactive features tested

---

## Phase 2 Timeline

| Week | Focus |
|---|---|
| Week 1 | Template audit + base template creation |
| Week 2 | App template migration (dashboard, invoice, settings) |
| Week 3 | Static page migration + landing page redesign |

---

## Risks & Mitigation

| Risk | Probability | Mitigation |
|---|---|---|
| Template breakage during migration | High | Parallel testing, git rollback plan |
| Performance regression | Medium | Lighthouse monitoring, CSS optimization |
| Responsive layout issues | Medium | Mobile-first testing, breakpoint validation |
| Browser compatibility | Low | Polyfill strategy, fallback CSS |

---

## Next Phase: PHASE 3

- Backend optimization (caching, ORM, logging)
- Testing infrastructure setup
- CI/CD pipeline configuration
- Performance baseline metrics
