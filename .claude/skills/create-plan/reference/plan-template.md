# Plan Template

This is the standard template for all Plan.md files created by the **create-plan** skill.

**Purpose:** Provides consistent structure for task planning across the AI Employee system.

---

## Template

Copy this template when creating new plans in `Vault/Plans` folder:

```markdown
---
created: [YYYY-MM-DDTHH:MM:SSZ]
status: pending_approval | in_progress | completed | blocked
priority: low | normal | high | urgent
task_source: Vault/Needs_Action/[source-file].md
estimated_duration: [e.g., "30 minutes", "3 hours", "2 days"]
assigned_to: claude_code
---

## Objective

[One clear sentence describing what needs to be accomplished. Be specific and measurable.]

**Example:** Send project proposal to Client A with pricing ($2,500) and 3-week timeline by Friday

---

## Background

[Context: Why this task matters, who requested it, what it's part of, relevant history]

**Include:**
- Who initiated this task
- Business goal it supports (reference Vault/Business_Goals.md if applicable)
- Any constraints (budget, timeline, resources)
- Related previous work or context

**Example:**
Client A requested a proposal for website redesign after seeing our LinkedIn post about
recent project. This aligns with Q1 revenue goal of $10,000/month. Client budget is
flexible but prefers completion within 3 weeks. We've worked with this client before
on smaller projects with positive feedback.

---

## Steps

[Break down into 3-7 actionable steps. Each step should be atomic and clearly described.]

- [ ] **Step 1:** [Clear action description using action verb]
      - **Est:** [time estimate: 5m, 30m, 2h, etc.]
      - **Depends on:** [none | previous step number | external dependency]
      - **Approval:** [yes | no]
      - **Details:** [Additional context, considerations, or notes]
      - **Resources:** [Files, tools, information, templates needed]
      - [REQUIRES APPROVAL] [Use this tag if approval needed]

- [ ] **Step 2:** [Next action]
      - **Est:** [time]
      - **Depends on:** Step 1
      - **Approval:** no
      - **Details:** [What this step involves]

- [ ] **Step 3:** [Continue pattern for all steps]
      - **Est:** [time]
      - **Depends on:** Step 2
      - **Approval:** yes
      - [REQUIRES APPROVAL] Reason why approval is needed

[... continue for remaining steps ...]

- [ ] **Step N:** [Final step - often involves logging, cleanup, or notification]

---

## Dependencies

**Sequential Dependencies:**
[List steps that must happen in order]
- Step 2 requires Step 1 completion
- Step 5 requires Step 4 completion
- Steps must be executed in order: 1 → 2 → 3 → 4 → 5

**Parallel Opportunities:**
[List steps that can be done simultaneously]
- Steps 3 and 4 can run in parallel (independent of each other)

**External Dependencies:**
[List dependencies on things outside our control]
- API access needed for Step 3 (requires admin approval from Platform X)
- Client feedback needed before proceeding to Step 5
- File must be delivered by external vendor before Step 4

**Blocking Issues:**
[If any exist at plan creation time]
- Currently blocked: Waiting for [something]
- Resolution needed: [action required to unblock]

---

## Approval Requirements

**Steps requiring human approval:** [List step numbers: 3, 5, 7]

**Detailed Approval Breakdown:**

**Step [N]:** [Why approval is needed]
- **Action:** [What will be done]
- **Risk:** [What could go wrong if done incorrectly]
- **Approval Type:** [email | payment | social | file | other]

**Example:**
**Step 3:** Send proposal email to Client A
- **Action:** Email with pricing information and timeline commitment
- **Risk:** Pricing or timeline might be incorrect, affects client relationship
- **Approval Type:** email (new client pricing)

[Repeat for each step requiring approval]

---

## Success Criteria

[Define specific, measurable outcomes that indicate task completion]

Task is considered complete when ALL of these criteria are met:

- [ ] [Criterion 1: Specific deliverable exists]
- [ ] [Criterion 2: Quality standard met]
- [ ] [Criterion 3: Stakeholders notified]
- [ ] [Criterion 4: No errors or issues remain]
- [ ] [Criterion 5: Documentation updated]

**Examples:**
- [ ] Email sent successfully (confirmation received)
- [ ] No typos or errors in final document
- [ ] Client acknowledges receipt
- [ ] Vault/Dashboard.md updated with completion
- [ ] All files moved to Vault/Done folder

---

## Risks & Contingencies

[Optional but recommended for complex tasks]

**Potential Risks:**
- **Risk 1:** [What could go wrong]
  - **Mitigation:** [How to prevent or minimize]
  - **Contingency:** [What to do if it happens]

**Example:**
- **Risk 1:** Client doesn't respond to proposal
  - **Mitigation:** Include clear call-to-action and response deadline
  - **Contingency:** Follow up after 3 business days, escalate to phone call if needed

---

## Resources

[List all files, tools, templates, information needed]

**Files:**
- Vault/Templates/proposal-template.md
- Vault/Pricing/standard-rates.md
- Vault/Client_History/ClientA_previous_work.md

**Tools:**
- Email MCP server (for sending)
- handle-approval skill (for approval workflow)

**Information Needed:**
- Client's exact requirements (documented in task source)
- Current project availability/capacity
- Latest pricing structure

**Templates:**
- [Link to relevant template files in vault]

---

## Execution Log

[This section is updated as work progresses]

**Status Updates:**

- **[YYYY-MM-DD HH:MM]** Plan created, ready to start Step 1
- **[YYYY-MM-DD HH:MM]** Step 1 completed - [brief result/outcome]
- **[YYYY-MM-DD HH:MM]** Step 2 in progress - [current status]
- **[YYYY-MM-DD HH:MM]** Step 3 blocked - [reason and resolution plan]
- **[YYYY-MM-DD HH:MM]** Step 3 unblocked - [how issue was resolved]
- **[YYYY-MM-DD HH:MM]** Step 4 completed - [result]
- **[YYYY-MM-DD HH:MM]** Step 5 approval requested - [approval file location]
- **[YYYY-MM-DD HH:MM]** Step 5 approved - [proceeding with execution]
- **[YYYY-MM-DD HH:MM]** All steps completed successfully
- **[YYYY-MM-DD HH:MM]** Plan archived to Vault/Done

**Issues Encountered:**
- [List any problems that came up and how they were resolved]

**Deviations from Plan:**
- [Note any changes made to original plan and why]

---

## Notes

[Any additional context, lessons learned, or follow-up items]

**Follow-up Actions:**
- [Tasks that need to happen after this plan completes]

**Lessons Learned:**
- [What went well, what could be improved for next time]

**References:**
- Related plans: Vault/Plans/PLAN_[related-task].md
- Documentation: [Links to relevant docs]

---

*Plan generated by create-plan skill*
*Last updated: [YYYY-MM-DD HH:MM:SS]*
*Current status: [status from frontmatter]*
```

---

## Field Descriptions

### Frontmatter Fields

| Field | Values | Description |
|-------|--------|-------------|
| **created** | ISO 8601 timestamp | When plan was created |
| **status** | pending_approval, in_progress, completed, blocked | Current plan status |
| **priority** | low, normal, high, urgent | Task urgency level |
| **task_source** | File path | Original task that triggered this plan |
| **estimated_duration** | Human-readable time | How long task will take total |
| **assigned_to** | claude_code (or human name) | Who's responsible for execution |

### Step Format

Each step should follow this structure:

```markdown
- [ ] **Step N:** [Action verb] + [clear description]
      - **Est:** [Realistic time estimate]
      - **Depends on:** [What must complete first]
      - **Approval:** [yes/no - is human approval needed?]
      - **Details:** [More context if needed]
      - **Resources:** [What's needed to complete this step]
      - [REQUIRES APPROVAL] [Include if approval: yes]
```

**Action Verbs to Use:**
- Research, Review, Analyze, Investigate (for learning)
- Draft, Write, Create, Generate (for content)
- Send, Publish, Share, Post (for communication)
- Verify, Validate, Test, Check (for quality)
- Update, Modify, Refactor, Improve (for changes)
- Deploy, Execute, Run, Launch (for actions)

---

## Status Values

### pending_approval
- Plan is created but waiting for human to review and approve the approach
- No steps have started yet
- Use when plan needs validation before execution

### in_progress
- Plan is approved and actively being worked on
- One or more steps are complete or currently being executed
- This is the "active work" state

### blocked
- Plan execution is stopped due to external dependency or issue
- Clearly document blocking issue in Execution Log
- Include expected resolution

### completed
- All steps finished successfully
- All success criteria met
- Plan should be moved to Vault/Done folder

---

## Minimal Plan Template (Quick Tasks)

For simpler tasks that still benefit from structure:

```markdown
---
created: [timestamp]
status: in_progress
priority: normal
---

## Objective
[What needs to be done]

## Steps
- [ ] Step 1: [action]
- [ ] Step 2: [action]
- [ ] Step 3: [action]

## Success Criteria
- [ ] [Measurable outcome]

---
## Execution Log
[Updates as work progresses]
```

---

## Examples by Task Type

### Email Response Plan

```markdown
---
created: 2026-01-11T16:00:00Z
status: in_progress
priority: normal
task_source: Vault/Needs_Action/EMAIL_ClientInquiry.md
estimated_duration: 20 minutes
---

## Objective
Respond to Client B's inquiry about availability and pricing for consulting services

## Steps

- [ ] **Step 1:** Review client's inquiry email and understand requirements
      Est: 3m | Depends on: none | Approval: no

- [ ] **Step 2:** Check Vault/Business_Goals.md for current availability and pricing
      Est: 2m | Depends on: Step 1 | Approval: no

- [ ] **Step 3:** Draft response email with availability and pricing quote
      Est: 10m | Depends on: Step 2 | Approval: no

- [ ] **Step 4:** Request approval to send email
      Est: 1m | Depends on: Step 3 | Approval: yes
      [REQUIRES APPROVAL] Email to client with pricing information

- [ ] **Step 5:** Send email once approved
      Est: 1m | Depends on: Step 4 approved | Approval: handled

## Success Criteria
- [ ] Email sent with accurate pricing
- [ ] Response time < 24 hours from inquiry
- [ ] Vault/Dashboard.md updated
```

### Research & Report Plan

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

## Best Practices

### Writing Objectives
- ✅ "Send proposal to Client A with $2,500 quote by Friday"
- ❌ "Handle client proposal"

### Writing Steps
- ✅ "Draft email with project scope, pricing, and timeline"
- ❌ "Work on email"

### Time Estimates
- ✅ "Est: 30m" (realistic)
- ❌ "Est: varies" (not helpful)

### Success Criteria
- ✅ "Email sent, client confirmed receipt, no typos in document"
- ❌ "Task done well"

---

*This template ensures consistent, complete task planning across all AI Employee operations.*

*Last Updated: 2026-01-11*
*Version: 1.1 (Updated for Vault structure)*