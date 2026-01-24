# Plan Examples

Practical examples of Plan.md files for different task types.

**Last Updated:** 2026-01-11

---

## Example 1: Simple Email Response Plan

```markdown
---
created: 2026-01-11T16:00:00Z
status: in_progress
priority: normal
task_source: Vault/Needs_Action/EMAIL_ClientA_Invoice_Request.md
estimated_duration: 30 minutes
---

## Objective
Send invoice email to Client A for January services

## Steps

- [ ] **Step 1:** Locate invoice file in Vault/Invoices folder
      Est: 2m | Depends on: none | Approval: no

- [ ] **Step 2:** Verify invoice details (amount, date, services)
      Est: 5m | Depends on: Step 1 | Approval: no

- [ ] **Step 3:** Draft email with professional invoice message
      Est: 10m | Depends on: Step 2 | Approval: no

- [ ] **Step 4:** Request approval to send email with attachment
      Est: 2m | Depends on: Step 3 | Approval: YES
      [REQUIRES APPROVAL] - Email to client with attachment

- [ ] **Step 5:** Send email once approved
      Est: 1m | Depends on: Step 4 approved | Approval: handled in Step 4

- [ ] **Step 6:** Log sent email to Vault/Dashboard.md
      Est: 2m | Depends on: Step 5 | Approval: no

## Success Criteria
- [ ] Email sent successfully
- [ ] Client acknowledges receipt
- [ ] Vault/Dashboard.md updated
```

---

## Example 2: Complex Project Plan

```markdown
---
created: 2026-01-11T16:00:00Z
status: pending_approval
priority: high
task_source: Vault/Needs_Action/PROJECT_WebsiteRedesign.md
estimated_duration: 2-3 weeks
---

## Objective
Complete website redesign project for Client B with new branding and improved UX

## Background
Client B requested modernization of their website. They provided new brand guidelines
and want to improve mobile experience. Budget: $5,000, Timeline: 3 weeks.

## Steps

- [ ] **Step 1:** Review client brief and brand guidelines
      Est: 1h | Depends on: none | Approval: no

- [ ] **Step 2:** Research competitor websites and UX best practices
      Est: 2h | Depends on: Step 1 | Approval: no

- [ ] **Step 3:** Create wireframes for homepage and key pages
      Est: 4h | Depends on: Step 2 | Approval: no

- [ ] **Step 4:** Request approval to share wireframes with client
      Est: 5m | Depends on: Step 3 | Approval: YES
      [REQUIRES APPROVAL] - External client communication

- [ ] **Step 5:** Incorporate client feedback into design
      Est: 3h | Depends on: Step 4 approved + feedback received | Approval: no

- [ ] **Step 6:** Develop responsive front-end code
      Est: 16h | Depends on: Step 5 | Approval: no

- [ ] **Step 7:** Request approval to deploy to staging server
      Est: 5m | Depends on: Step 6 | Approval: YES
      [REQUIRES APPROVAL] - Server deployment

## Dependencies
- Step 5 blocked until client provides feedback (external dependency)
- Steps 6 and 7 are sequential (cannot deploy before development complete)

## Success Criteria
- [ ] Website deployed and functioning on all devices
- [ ] Client approval received on final design
- [ ] Payment received ($5,000)
- [ ] Project documented in portfolio

## Notes
- Client typically responds within 24-48 hours
- May need to schedule video call for feedback session
- Budget includes 2 rounds of revisions
```

---

## Example 3: Research & Report Plan

```markdown
---
created: 2026-01-11T16:00:00Z
status: in_progress
priority: low
task_source: Vault/Needs_Action/RESEARCH_MarketTrends.md
estimated_duration: 3 hours
---

## Objective
Research current AI automation trends and create summary report for business strategy

## Steps

- [ ] **Step 1:** Search for recent articles on AI automation trends (2026)
      Est: 45m | Depends on: none | Approval: no
      Resources: Web search, industry publications

- [ ] **Step 2:** Identify top 5 trends relevant to our services
      Est: 30m | Depends on: Step 1 | Approval: no

- [ ] **Step 3:** Analyze how trends align with Vault/Business_Goals.md
      Est: 30m | Depends on: Step 2 | Approval: no

- [ ] **Step 4:** Draft report with findings and recommendations
      Est: 1h | Depends on: Step 3 | Approval: no

- [ ] **Step 5:** Save report to Vault/Reports folder and update Dashboard
      Est: 5m | Depends on: Step 4 | Approval: no

## Success Criteria
- [ ] Report contains 5 specific trends with sources
- [ ] Recommendations aligned with current business goals
- [ ] Report saved and logged
```

---

## Example 4: Multi-Phase Project

```markdown
---
created: 2026-01-11T16:00:00Z
status: in_progress
priority: high
task_source: Vault/Needs_Action/PROJECT_MarketingCampaign.md
estimated_duration: 2 weeks
---

## Objective
Launch Q1 marketing campaign across email and LinkedIn to generate 10 qualified leads

## Background
Q1 goal is $10,000 revenue. Need to increase visibility and generate inbound leads.
Campaign will showcase recent successful projects and AI automation expertise.

## Phase 1: Planning & Content Creation (Week 1)

- [ ] **Step 1:** Define campaign messaging and target audience
      Est: 2h | Depends on: none | Approval: no

- [ ] **Step 2:** Create 4 LinkedIn post drafts
      Est: 3h | Depends on: Step 1 | Approval: no

- [ ] **Step 3:** Create 2 email campaign drafts
      Est: 2h | Depends on: Step 1 | Approval: no

- [ ] **Step 4:** Request approval for all content
      Est: 10m | Depends on: Steps 2-3 | Approval: YES
      [REQUIRES APPROVAL] - All marketing content

## Phase 2: Execution (Week 2)

- [ ] **Step 5:** Schedule LinkedIn posts (2 per week)
      Est: 30m | Depends on: Step 4 approved | Approval: handled

- [ ] **Step 6:** Send first email campaign
      Est: 15m | Depends on: Step 4 approved | Approval: handled

- [ ] **Step 7:** Monitor engagement and respond to inquiries
      Est: ongoing | Depends on: Steps 5-6 | Approval: no

- [ ] **Step 8:** Send second email campaign (mid-week)
      Est: 15m | Depends on: Step 6 + 3 days | Approval: no

## Dependencies
- Phase 2 cannot start until Phase 1 approved
- Step 8 requires 3-day gap after Step 6

## Success Criteria
- [ ] 4 LinkedIn posts published
- [ ] 2 email campaigns sent
- [ ] 10+ qualified leads generated
- [ ] 2+ meetings scheduled
- [ ] Campaign documented for future reference

## Notes
- Track all leads in CRM or spreadsheet
- Document what works for future campaigns
```

---

## Example 5: Minimal Plan (Quick Task)

For simpler tasks that still benefit from structure:

```markdown
---
created: 2026-01-11T16:00:00Z
status: in_progress
priority: normal
---

## Objective
Update pricing page on website with new 2026 rates

## Steps
- [ ] Review current pricing vs new rates in Vault/Business_Goals.md
- [ ] Update pricing page HTML/markdown
- [ ] Request approval to deploy changes
- [ ] Deploy to production once approved

## Success Criteria
- [ ] Pricing accurate and reflects 2026 rates
- [ ] No broken links or formatting issues

---
## Execution Log
[Updates as work progresses]
```

---

*These examples demonstrate proper plan structure across different task complexities.*

*Last Updated: 2026-01-11*