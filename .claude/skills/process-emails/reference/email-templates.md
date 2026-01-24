# Email Response Templates

**Purpose:** Professional email templates for common business scenarios.

**Usage:** Select appropriate template based on email category and request type, then personalize with specific details.

---

## Table of Contents

1. [Client Inquiry Response](#client-inquiry-response)
2. [Invoice Request Response](#invoice-request-response)
3. [Meeting Scheduling Response](#meeting-scheduling-response)
4. [Project Status Update](#project-status-update)
5. [Support Request Response](#support-request-response)
6. [Generic Professional Response](#generic-professional-response)
7. [Urgent Matter Escalation](#urgent-matter-escalation)
8. [Follow-up Email](#follow-up-email)
9. [Thank You Email](#thank-you-email)
10. [Decline/Rejection Email](#declinerejection-email)

---

## Template Guidelines

**All Templates Should:**
- Include professional greeting and closing
- Address sender by name (use from_name from email metadata)
- Reference specific details from original email
- Maintain tone consistent with `Vault/Company_Handbook.md`
- Be concise and actionable
- Include clear next steps
- Sign with appropriate signature

**Personalization Variables:**
- `{sender_name}` - Name of email sender
- `{your_name}` - Your name from `Vault/Company_Handbook.md`
- `{company_name}` - Your company name
- `{specific_detail}` - Detail from original email
- `{date}` - Relevant date
- `{amount}` - Relevant amount (invoices, quotes)

---

## 1. Client Inquiry Response

**Use When:** Client asks about services, pricing, availability

**Template:**

```
Subject: Re: {original_subject}

Hi {sender_name},

Thank you for reaching out regarding {specific_detail}.

I'd be happy to help you with {request_summary}. Based on your requirements, here's what I can offer:

{service_details}

{pricing_information - if applicable}

The typical timeline for this would be {timeframe}, and we can start as soon as {availability}.

Would you like to schedule a call to discuss this in more detail? I'm available {availability_options}.

Looking forward to working with you!

Best regards,
{your_name}
{company_name}
{contact_information}
```

**Notes:**
- Keep response warm and professional
- Provide specific details, not vague promises
- Include clear call-to-action (schedule call, reply with preferences)
- Reference `Vault/Business_Goals.md` for pricing guidance

---

## 2. Invoice Request Response

**Use When:** Client requests invoice for completed work

**Template:**

```
Subject: Invoice #{invoice_number} - {project_name}

Hi {sender_name},

Thank you for your email. I've prepared your invoice for {project_name}.

**Invoice Details:**
- Invoice Number: #{invoice_number}
- Amount: ${amount}
- Due Date: {due_date}
- Payment Methods: {payment_methods}

The invoice is attached to this email. Please let me know if you have any questions or need any adjustments.

Payment can be made via:
{payment_instructions}

Thank you for your business!

Best regards,
{your_name}
{company_name}
```

**Notes:**
- Always attach actual invoice (flag for manual attachment in approval)
- Include clear payment instructions
- Professional but friendly tone
- Reference account receivable policies from `Vault/Business_Goals.md`

---

## 3. Meeting Scheduling Response

**Use When:** Client requests meeting or call

**Template:**

```
Subject: Re: Meeting Request - {topic}

Hi {sender_name},

I'd be happy to meet to discuss {meeting_topic}.

I'm available at the following times:
- {option_1}
- {option_2}
- {option_3}

Please let me know which time works best for you, or suggest an alternative if none of these suit your schedule.

Meeting Details:
- Duration: {estimated_duration}
- Format: {video_call / phone / in-person}
- Agenda: {brief_agenda}

I'll send a calendar invite once you confirm the time.

Looking forward to our conversation!

Best regards,
{your_name}
```

**Notes:**
- Provide 3 specific time options
- Mention timezone if relevant
- Include meeting format (Zoom, phone, etc.)
- Brief agenda shows preparation
- Consider integration with calendar MCP (future)

---

## 4. Project Status Update

**Use When:** Client asks for progress update on ongoing project

**Template:**

```
Subject: Project Update - {project_name}

Hi {sender_name},

Thank you for checking in on {project_name}.

**Current Status:**
We've completed {completed_milestones} and are currently working on {current_phase}.

**Progress Summary:**
✓ {completed_item_1}
✓ {completed_item_2}
→ {in_progress_item} (Current)
- {upcoming_item_1}
- {upcoming_item_2}

**Timeline:**
We're {on_track / slightly_behind / ahead_of_schedule} with an expected completion date of {completion_date}.

{any_blockers_or_issues}

I'll keep you updated on progress. Please let me know if you have any questions or concerns.

Best regards,
{your_name}
```

**Notes:**
- Be transparent about status (use `Vault/Dashboard.md` and `Vault/Done` folder for accurate info)
- Use visual indicators (✓ for done, → for current, - for pending)
- Proactively mention any delays or issues
- Provide realistic completion dates

---

## 5. Support Request Response

**Use When:** Client reports issue or requests technical support

**Template:**

```
Subject: Re: {issue_description}

Hi {sender_name},

Thank you for bringing this to my attention. I understand you're experiencing {issue_summary}.

I've looked into this and {initial_assessment}.

**Immediate Action:**
{quick_fix_if_available}

**Next Steps:**
1. {step_1}
2. {step_2}
3. {step_3}

I'll {action_commitment} and follow up with you by {follow_up_timeframe}.

In the meantime, if you have any additional information about the issue, please feel free to share.

Best regards,
{your_name}
```

**Notes:**
- Acknowledge the issue promptly
- Show empathy and understanding
- Provide immediate fix if possible
- Clear next steps and timeline
- Set expectations for follow-up

---

## 6. Generic Professional Response

**Use When:** Email doesn't fit other categories, or multiple topics

**Template:**

```
Subject: Re: {original_subject}

Hi {sender_name},

Thank you for your email regarding {topic}.

{address_main_points}

{provide_information_or_answer}

{next_steps_or_action_items}

Please let me know if you need any additional information or clarification.

Best regards,
{your_name}
{company_name}
{contact_information}
```

**Notes:**
- Flexible template for various situations
- Address all points from original email
- Maintain professional but approachable tone
- Clear structure: acknowledge → respond → next steps

---

## 7. Urgent Matter Escalation

**Use When:** Email requires immediate attention or beyond AI capability

**Template:**

```
Subject: Re: {original_subject} [URGENT]

Hi {sender_name},

Thank you for your urgent email regarding {urgent_matter}.

I've received your message and understand the time-sensitive nature of {issue}.

I'm reviewing this immediately and will {committed_action} within {timeframe}.

{if_escalation_needed}
I'm also flagging this for immediate review to ensure we address your needs as quickly as possible.

You can expect a detailed response by {specific_deadline}.

If you need immediate assistance, please feel free to call {phone_number}.

Best regards,
{your_name}
```

**Notes:**
- Use [URGENT] tag in subject
- Acknowledge urgency explicitly
- Provide specific response timeframe
- Offer alternative contact method for emergencies
- Always create high-priority approval for these

---

## 8. Follow-up Email

**Use When:** Following up on previous email with no response

**Template:**

```
Subject: Following up: {original_subject}

Hi {sender_name},

I wanted to follow up on my previous email from {date} regarding {topic}.

{brief_recap_of_previous_email}

I understand you may be busy, but I wanted to make sure this didn't get lost in your inbox.

{restate_question_or_action_needed}

Please let me know if you need any additional information, or if there's a better time to discuss this.

Looking forward to hearing from you.

Best regards,
{your_name}
```

**Notes:**
- Wait appropriate time before follow-up (typically 3-5 business days)
- Reference previous email with date
- Brief recap of key points
- Friendly, not pushy tone
- Acknowledge they may be busy

---

## 9. Thank You Email

**Use When:** Expressing gratitude for business, referral, payment, etc.

**Template:**

```
Subject: Thank you - {reason}

Hi {sender_name},

I wanted to take a moment to thank you for {specific_reason}.

{personalized_appreciation}

It's clients like you that make this work so rewarding, and I truly appreciate {specific_aspect}.

{future_commitment}

If there's anything else I can help you with, please don't hesitate to reach out.

Warm regards,
{your_name}
```

**Notes:**
- Genuine and specific appreciation
- Reference specific actions or qualities
- Keep brief and sincere
- Mention future collaboration

---

## 10. Decline/Rejection Email

**Use When:** Need to politely decline request or reject proposal

**Template:**

```
Subject: Re: {request_subject}

Hi {sender_name},

Thank you for reaching out regarding {request}.

After careful consideration, I won't be able to {request_action} at this time due to {brief_reason}.

{alternative_suggestion_if_possible}

I appreciate your understanding, and I hope we can work together on future opportunities.

Best regards,
{your_name}
```

**Notes:**
- Be polite and respectful
- Brief explanation without over-justifying
- Offer alternative if appropriate
- Leave door open for future
- Don't burn bridges

---

## Template Selection Logic

**Decision Tree:**

1. **Email Category** (from categorization.md):
   - Client Communications → Client Inquiry / Project Status / Support
   - Sales/Leads → Client Inquiry / Meeting Scheduling
   - Administrative → Generic Professional / Invoice Request
   - Support → Support Request / Urgent Escalation

2. **Request Type** (from email content):
   - Question about services → Client Inquiry
   - Request for invoice → Invoice Request
   - Want to meet → Meeting Scheduling
   - Project progress → Project Status Update
   - Problem/issue → Support Request
   - Time-sensitive → Urgent Escalation
   - No previous response → Follow-up
   - Appreciation → Thank You
   - Can't accommodate → Decline

3. **Priority Level**:
   - Urgent → Use Urgent Escalation template
   - Normal → Standard template for category
   - Low → Generic Professional (if response needed)

---

## Customization Guidelines

**For Each Template:**

1. **Replace all {variables}** with actual content
2. **Personalize greeting** with sender's name
3. **Reference specific details** from original email
4. **Match tone** to `Vault/Company_Handbook.md` guidelines
5. **Check for typos** and formatting
6. **Verify signature** includes correct contact info
7. **Add context** from `Vault/Business_Goals.md` if relevant

**Quality Checklist:**
- [ ] Addresses sender by name
- [ ] References specific content from original email
- [ ] Professional and friendly tone
- [ ] Clear next steps or action items
- [ ] No typos or grammar errors
- [ ] Proper signature with contact info
- [ ] Subject line is descriptive
- [ ] Length is appropriate (not too long)

---

## Integration with Company Voice

**Refer to `Vault/Company_Handbook.md` for:**
- Preferred greeting style (Hi vs. Dear vs. Hello)
- Signature format
- Tone preferences (formal vs. casual)
- Industry-specific terminology
- Brand voice guidelines

**Example Company Voice Variations:**

**Formal Style:**
```
Dear Mr. Smith,

I hope this message finds you well.

[body]

Sincerely,
{your_name}
```

**Friendly Professional:**
```
Hi John,

Thanks for reaching out!

[body]

Best,
{your_name}
```

**Current Default:** Friendly Professional (adjust based on Company_Handbook)

---

## Advanced Template Features (Future)

- Multi-language templates
- Industry-specific variations
- A/B tested high-conversion templates
- Seasonal/holiday variations
- Automated attachment mentions
- Calendar link integration
- Payment link integration

---

**Template Library Stats:**
- Total Templates: 10
- Categories Covered: Client, Sales, Admin, Support
- Average Length: 150-250 words
- Personalization Variables: 15+

**Last Updated:** 2026-01-11
**Status:** Ready for use
**Maintenance:** Review quarterly, update based on response effectiveness