# Planning Best Practices

Guidelines for creating effective, actionable plans.

**Last Updated:** 2026-01-11

---

## When to Create a Plan

### Yes, create a plan:
- ✅ Task has 3+ distinct steps
- ✅ Task involves multiple skills/actions
- ✅ Task has dependencies or sequencing
- ✅ Task requires approval at any stage
- ✅ Task is unfamiliar or complex
- ✅ User explicitly requests a plan

### No, don't create a plan (just do it):
- ❌ Single-step simple tasks
- ❌ Routine operations (already documented)
- ❌ Tasks with clear obvious approach
- ❌ Emergency/urgent tasks needing immediate action

---

## Appropriate Step Count

- **Too few (1-2 steps)**: Probably doesn't need a plan
- **Good (3-7 steps)**: Ideal, manageable plan
- **Too many (10+ steps)**: Break into phases or sub-plans

### If you have 10+ steps, consider:
- Grouping related steps into phases
- Creating a high-level plan + detailed sub-plans
- Combining atomic steps into logical chunks

---

## Writing Effective Steps

### Good Step Examples:

✅ **Clear and actionable:**
```markdown
- [ ] Draft proposal document including pricing ($2,500), timeline (3 weeks), and deliverables
      Est: 1 hour | Depends on: Research complete | Resources: pricing-template.md
```

✅ **Specific with context:**
```markdown
- [ ] Request approval to send email with attachment to Client A
      Est: 2m | Depends on: Draft complete | Approval: YES
      [REQUIRES APPROVAL] - Email to client with pricing information
```

### Bad Step Examples:

❌ **Too vague:**
```markdown
- [ ] Work on proposal
```

❌ **Missing details:**
```markdown
- [ ] Send email
```
(Missing: to whom? What content? Approval needed?)

❌ **No estimate:**
```markdown
- [ ] Research competitor websites and create wireframes and develop code
```
(Too broad, should be 3 separate steps)

---

## Action Verbs to Use

**For Learning/Research:**
- Research, Review, Analyze, Investigate, Study, Examine

**For Creation:**
- Draft, Write, Create, Generate, Build, Design, Develop

**For Communication:**
- Send, Publish, Share, Post, Email, Notify, Inform

**For Quality:**
- Verify, Validate, Test, Check, Confirm, Review

**For Modification:**
- Update, Modify, Refactor, Improve, Enhance, Optimize

**For Execution:**
- Deploy, Execute, Run, Launch, Implement, Install

---

## Writing Objectives

### Strong Objectives:
✅ "Send proposal to Client A with $2,500 quote by Friday"
✅ "Research AI automation trends and create 5-page report with recommendations"
✅ "Deploy website redesign to production with mobile optimization"

### Weak Objectives:
❌ "Handle client proposal"
❌ "Do research"
❌ "Work on website"

**Characteristics of good objectives:**
- Specific (what exactly)
- Measurable (how you'll know it's done)
- Time-bound (when, if applicable)
- Clear deliverable (what artifact exists at the end)

---

## Time Estimates

### Realistic Estimates:
- ✅ "Est: 30m" (specific and reasonable)
- ✅ "Est: 2h" (clear duration)
- ✅ "Est: 5m" (quick task)

### Poor Estimates:
- ❌ "Est: varies" (not helpful)
- ❌ "Est: TBD" (defeats purpose)
- ❌ "Est: as long as it takes" (not useful)

**Estimation Guidelines:**
- Be realistic, not optimistic
- Include buffer for unexpected issues
- Round to reasonable increments (5m, 15m, 30m, 1h, 2h)
- Don't estimate beyond 8h for a single step (break it down)

---

## Success Criteria

### Good Success Criteria:
✅ **Specific and measurable:**
```markdown
- [ ] Email sent successfully (confirmation received)
- [ ] No typos or errors in final document
- [ ] Client acknowledges receipt within 24 hours
- [ ] Vault/Dashboard.md updated with completion log
```

✅ **Quality-focused:**
```markdown
- [ ] Website passes mobile responsiveness test
- [ ] All links work (no 404 errors)
- [ ] Page load time < 3 seconds
```

### Weak Success Criteria:
❌ "Task done well"
❌ "Everything looks good"
❌ "Finished successfully"

**Characteristics of good criteria:**
- Observable (can verify it happened)
- Binary (yes/no, not subjective)
- Comprehensive (covers all aspects of success)

---

## Dependencies Best Practices

### Clear Dependency Notation:

✅ **Sequential:**
```markdown
## Dependencies

**Sequential:**
- Step 2 requires Step 1 completion
- Step 5 requires Step 4 completion
- Must execute in order: 1 → 2 → 3 → 4 → 5
```

✅ **Parallel:**
```markdown
**Parallel Opportunities:**
- Steps 3 and 4 can run simultaneously (independent)
- Steps 6 and 7 can be done in any order
```

✅ **External:**
```markdown
**External Dependencies:**
- API access needed for Step 3 (requires admin approval from Platform X)
- Client feedback required before Step 5
- File delivery from vendor needed before Step 4
```

### Avoid Circular Dependencies:
❌ Step 2 depends on Step 3, Step 3 depends on Step 2
✅ Draw dependency graph if complex

---

## Common Mistakes to Avoid

### 1. Forgetting Approval Steps
❌ Plan includes "Send email to client" without approval flag
✅ "Request approval to send email to client [REQUIRES APPROVAL]"

### 2. Skipping Success Criteria
❌ Plan ends with final step, no criteria
✅ Plan includes measurable success criteria section

### 3. Too Many Steps
❌ 15 detailed steps for a simple task
✅ Break into phases or combine related steps

### 4. No Time Estimates
❌ Steps listed with no estimates
✅ Every step has realistic time estimate

### 5. Vague Steps
❌ "Work on project", "Handle task"
✅ "Draft proposal with pricing and timeline", "Send invoice to Client A"

### 6. Missing Context
❌ No background section, unclear why task matters
✅ Background explains business goal alignment

### 7. Ignoring Dependencies
❌ All steps marked as "Depends on: none"
✅ Clear dependencies mapped out

---

## Plan Status Best Practices

### pending_approval
- Use when plan needs human review before starting
- Plan created but not yet validated
- Waiting for user to approve approach

### in_progress
- At least one step started or completed
- Active work happening
- This is the primary "working" state

### blocked
- Work stopped due to dependency or issue
- Document blocking issue clearly
- Include expected resolution

### completed
- All steps finished
- All success criteria met
- Ready to move to `Vault/Done`

---

## Dashboard Logging

Always log plan creation to Vault/Dashboard.md:

```markdown
### [Timestamp] - Plan Created

**Plan:** [Task name]
- File: Vault/Plans/PLAN_[name]_[date].md
- Priority: [priority level]
- Total Steps: [number]
- Requires Approval: [yes/no, which steps]
- Estimated Duration: [time]
- Status: Ready for execution
```

---

## Integration with Other Skills

### How Plans Work in the System:

```
1. create-plan generates Plan.md
2. process-tasks reads plan and executes steps
3. handle-approval manages steps requiring approval
4. Specific skills (process-emails, post-to-linkedin) execute actions
5. Vault/Dashboard.md logs all activity
6. Completed plans move to Vault/Done
```

### Plan Execution Workflow:

```
Task arrives
  → create-plan analyzes
  → Generates Plan.md in Vault/Plans
  → process-tasks reads plan
  → Executes Step 1
  → Step 2 needs approval
  → handle-approval creates approval request
  → Human approves
  → process-tasks continues
  → All steps complete
  → Plan moved to Vault/Done
```

---

## Quick Reference

### Plan Template Checklist:
- [ ] YAML frontmatter with required fields
- [ ] Clear one-sentence objective
- [ ] Background/context section
- [ ] 3-7 actionable steps with estimates
- [ ] Dependencies clearly identified
- [ ] Approval requirements flagged
- [ ] Measurable success criteria
- [ ] Execution log section (empty initially)

### File Naming:
- Format: `PLAN_[description]_[date].md`
- Example: `PLAN_ClientA_Proposal_2026-01-11.md`
- Keep filename < 80 characters
- Use underscores, not spaces

### Folder Location:
- Always save to `Vault/Plans` folder
- Completed plans move to `Vault/Done`
- Active plans stay in `Vault/Plans`

---

*Following these practices ensures plans are clear, actionable, and successfully executable.*

*Last Updated: 2026-01-11*
*Version: 1.1 (Updated for Vault structure)*