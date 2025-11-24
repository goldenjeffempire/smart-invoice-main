# Smart Invoice v5.0 Rebuild - Risk Register

**Last Updated:** November 24, 2025  
**Project Phase:** Phase 0 → Phase 1 Transition  
**Review Frequency:** Weekly during active phases, monthly during maintenance

---

## Risk Assessment Matrix

| Risk Level | Impact | Probability | Response Priority |
|------------|--------|-------------|-------------------|
| 🔴 Critical | High impact on delivery/quality | Likely to occur | Immediate mitigation required |
| 🟡 Moderate | Medium impact | Possible | Monitor and prepare mitigation |
| 🟢 Low | Minor impact | Unlikely | Accept or minimal mitigation |

---

## Critical Risks (🔴)

### R001: Frontend Rebuild Disrupts User Experience
**Category:** User Impact  
**Impact:** High - Users may encounter broken features during incremental migration  
**Probability:** High - 53 templates being rebuilt over 4 weeks  
**Owner:** Frontend Lead

**Mitigation Strategy:**
1. **Feature Flags:** Implement Django middleware to toggle between old/new templates per user
2. **Incremental Rollout:** Migrate non-critical pages first (About, FAQ) before core flows
3. **Regression Testing:** Automated E2E tests for each migrated template
4. **Rollback Plan:** Keep old templates in `templates/legacy/` for immediate fallback
5. **User Communication:** Beta testing with small user group before full rollout

**Contingency:**
- If P0 bugs detected → immediate rollback to legacy templates
- Emergency hotfix workflow established
- 24-hour monitoring during each major page migration

---

### R002: Build Tooling Migration (npm → Vite) Breaks Asset Pipeline
**Category:** Technical Infrastructure  
**Impact:** High - Development halted if builds fail  
**Probability:** Medium - Vite is well-documented but migration has unknowns  
**Owner:** DevOps Lead

**Current State:**
```json
// Existing: npm scripts
"build:css": "tailwindcss -i ./static/css/tailwind.input.css -o ./static/css/tailwind.output.css --minify",
"minify:js": "terser static/js/app.js -o static/js/app.min.js",
"minify:css": "cssnano static/css/main.css static/css/main.min.css"
```

**Migration Risks:**
- Django staticfiles integration with Vite
- HMR (Hot Module Replacement) compatibility with Django dev server
- Production build output paths mismatch
- Asset manifest generation for WhiteNoise

**Mitigation Strategy:**
1. **Parallel Development:** Keep npm scripts working during Vite POC
2. **Staged Migration:** 
   - Week 1: Vite dev server + HMR only
   - Week 2: Production builds
   - Week 3: Full migration + deprecate npm scripts
3. **Compatibility Testing:** Test with Whitenoise, collectstatic, Render deployment
4. **Documentation:** Step-by-step migration guide

**Contingency:**
- If Vite integration fails → revert to enhanced npm scripts with esbuild
- Fallback option: Parcel bundler as alternative to Vite

---

### R003: PDF Generation (WeasyPrint) Breaks After Frontend Rebuild
**Category:** Core Feature Dependency  
**Impact:** High - Invoice PDF export is critical feature  
**Probability:** Medium - Template changes may affect PDF rendering  
**Owner:** Backend Lead

**Dependencies:**
- WeasyPrint 66.0 (Python library)
- Cairo graphics library (system dependency)
- Pango font rendering
- Invoice templates HTML/CSS structure

**Specific Risks:**
- New Tailwind classes incompatible with WeasyPrint's CSS engine
- JavaScript-based animations break PDF static rendering
- Custom fonts not loaded in PDF context
- Print-specific CSS (@media print) not tested

**Mitigation Strategy:**
1. **Separate PDF Templates:** Create dedicated `templates/invoices/invoice_pdf.html` (not shared with web views)
2. **PDF-Specific CSS:** Use minimal, WeasyPrint-tested CSS (`static/css/pdf.css`)
3. **Automated Testing:** Unit tests for PDF generation with each template change
4. **Visual Regression:** PDF screenshot comparison tests
5. **Early Validation:** Test PDF rendering in Phase 1 with sample layouts

**Contingency:**
- If WeasyPrint fails → investigate wkhtmltopdf as fallback
- Emergency option: Browser-based PDF via Puppeteer (adds Node dependency)

---

### R004: SendGrid Rate Limits During Email Redesign
**Category:** Third-Party Service  
**Impact:** Medium-High - Email delivery delays affect user experience  
**Probability:** Low-Medium - Rate limits depend on sending volume  
**Owner:** Backend Lead

**Current Implementation:**
```python
# invoices/sendgrid_service.py
class SendGridEmailService:
    # No retry logic
    # No queue system
    # Synchronous sending
```

**Known Limits:**
- SendGrid free tier: 100 emails/day
- SendGrid paid tier: Varies by plan
- No current tracking of email quota usage

**Mitigation Strategy:**
1. **Email Queue:** Implement Celery task queue for async email sending
2. **Retry Logic:** Exponential backoff for rate limit errors (429 status)
3. **Monitoring:** Track daily send volume, alert at 80% quota
4. **Batch Operations:** Consolidate multiple emails where possible
5. **Graceful Degradation:** Save email content to database if SendGrid fails

**Contingency:**
- If rate limits hit → queue emails for delayed send
- Alternative: AWS SES or Mailgun as backup provider

---

## Moderate Risks (🟡)

### R005: CSS Conflicts During Transition Period
**Category:** Technical Quality  
**Impact:** Medium - Visual bugs, layout shifts  
**Probability:** High - 3 CSS files being consolidated  
**Owner:** Frontend Lead

**Mitigation:**
- CSS namespacing: `.legacy-` prefix for old styles
- Gradual migration: One page at a time
- Visual regression tests: Percy or Chromatic

---

### R006: Database Schema Drift (Accidental Migrations)
**Category:** Data Integrity  
**Impact:** High (if occurs) - Data loss, production issues  
**Probability:** Low - No planned schema changes  
**Owner:** Backend Lead

**Mitigation:**
- Code review: All migrations reviewed by 2+ engineers
- Migration staging: Test on copy of production data first
- Backup: Daily database backups enabled
- Freeze: No schema changes during frontend rebuild phases

---

### R007: Celery Task Queue Configuration Uncertainty
**Category:** Infrastructure  
**Impact:** Medium - Background tasks (recurring invoices) may fail  
**Probability:** Medium - Current usage unknown  
**Owner:** DevOps Lead

**Current State:**
```python
# invoices/celery_tasks.py exists but usage unclear
# No Redis/RabbitMQ configured
# No Celery beat schedule
```

**Mitigation:**
1. **Audit:** Document all async tasks (Phase 1)
2. **Redis Setup:** Add Redis for Celery broker (Phase 4)
3. **Testing:** Unit tests for all Celery tasks
4. **Monitoring:** Flower for Celery task monitoring

---

### R008: Replit Environment Constraints
**Category:** Development Environment  
**Impact:** Medium - Performance, debugging limitations  
**Probability:** Medium - Replit has resource constraints  
**Owner:** DevOps Lead

**Known Constraints:**
- Limited RAM for parallel builds
- No native Redis (need external service)
- Port 5000 required for web preview
- Replit-specific networking for proxies

**Mitigation:**
- Test locally before Replit deployment
- Use external Redis (Render add-on or Upstash)
- Document Replit-specific configurations

---

### R009: Test Coverage Gaps
**Category:** Quality Assurance  
**Impact:** Medium - Bugs slip to production  
**Probability:** High - Current coverage incomplete  
**Owner:** QA Lead

**Current State:**
- `invoices/tests.py`: Basic model tests
- `invoices/tests_comprehensive.py`: Exists but limited
- No E2E tests
- No integration tests

**Mitigation:**
1. **Coverage Target:** >85% by Phase 7
2. **Test Types:**
   - Unit: pytest for models, forms, services
   - Integration: API endpoint tests
   - E2E: Playwright for critical flows
3. **CI Integration:** GitHub Actions runs tests on every PR

---

## Low Risks (🟢)

### R010: Asset Cache Invalidation Issues
**Category:** Performance  
**Impact:** Low - Users see stale assets temporarily  
**Probability:** Low - WhiteNoise handles versioning  
**Mitigation:** Content-based hashing in filenames (automatic with WhiteNoise)

---

### R011: SEO Rankings Drop During Redesign
**Category:** Business Impact  
**Impact:** Low-Medium - Traffic decreases temporarily  
**Probability:** Low - No URL structure changes planned  
**Mitigation:**
- Maintain URL structure
- Preserve meta tags
- 301 redirects if URLs change
- Google Search Console monitoring

---

### R012: Deployment Downtime
**Category:** Operations  
**Impact:** Low - Brief service interruption  
**Probability:** Low - Render supports zero-downtime deploys  
**Mitigation:**
- Blue-green deployment on Render
- Health checks before routing traffic
- Rollback procedure documented

---

## Monitoring & Review Process

### Weekly Risk Review (During Active Phases)
- **Attendees:** Project Lead, Frontend Lead, Backend Lead, DevOps Lead
- **Agenda:**
  1. Review critical risks (🔴) - any new triggers?
  2. Update probability/impact based on weekly progress
  3. Test contingency plans
  4. Add new risks identified during development

### Monthly Risk Review (Maintenance)
- **Post-Launch:** Continue monitoring top 5 risks
- **Metrics:** Track incidents related to each risk
- **Lessons Learned:** Document what mitigations worked

---

## Risk Response Templates

### Risk Triggered: What to Do

**If R001 (Frontend Disruption) Occurs:**
1. Immediately notify Project Lead
2. Rollback to legacy templates (`templates/legacy/`)
3. Post incident report to Slack/email
4. Schedule hotfix within 4 hours
5. Conduct post-mortem within 24 hours

**If R002 (Build Tool Failure) Occurs:**
1. Switch to npm fallback scripts
2. Create GitHub issue with error logs
3. Continue development with old build system
4. Schedule Vite debug session within 48 hours

**If R003 (PDF Breaks) Occurs:**
1. Test with previous template version
2. If urgent: Revert templates for PDF generation only
3. Add regression test to prevent recurrence
4. Consider separating PDF/web templates permanently

---

## Risk Ownership & Contact

| Risk ID | Owner Role | Escalation Path |
|---------|-----------|-----------------|
| R001-R003 | Frontend Lead → Project Lead → Stakeholder |
| R004, R006-R007 | Backend Lead → Project Lead → Stakeholder |
| R002, R008, R012 | DevOps Lead → Project Lead → Stakeholder |
| R005, R009 | QA Lead → Project Lead |

---

**Risk Register Status:** ✅ Complete  
**Next Review:** Start of Phase 1 (Design System)  
**Document Owner:** Project Lead
