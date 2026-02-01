# Social Media Integration Guide for Gold Tier

## Overview
This guide covers the integration of Facebook, Instagram, and Twitter/X platforms with the Gold Tier AI Employee system. The social media suite enables automated content creation, cross-platform posting, engagement tracking, and performance analytics.

## Supported Platforms

### 1. Facebook
- **Pages**: Business page management
- **Features**: Text posts, image posts, video posts, engagement tracking
- **API**: Facebook Graph API v18.0

### 2. Instagram
- **Account Type**: Instagram Business Account
- **Features**: Photo posts, carousel posts, stories, engagement tracking
- **API**: Instagram Basic Display API

### 3. Twitter/X
- **Features**: Tweet posting, thread creation, engagement tracking
- **API**: Twitter API v2

## Prerequisites

### Developer Account Setup
Each platform requires a developer account and app registration:

#### Facebook/Instagram Requirements
- Facebook Developer Account
- Facebook Business Manager
- Instagram Business Account connected to Facebook Page
- App review approval for required permissions

#### Twitter/X Requirements
- Twitter Developer Account
- Twitter App with appropriate permissions
- API keys and tokens

### System Requirements
- Python 3.8+
- Internet connection
- SSL certificate (for webhook callbacks)

## Platform-Specific Setup

### Facebook Setup

#### Step 1: Create Facebook App
1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Create a new app
3. Add "Facebook Pages" product
4. Configure app settings:
   - App Domains: Your domain (if applicable)
   - Site URL: Your callback URL

#### Step 2: Get Required Permissions
For the AI Employee system, request these permissions:
- `pages_manage_posts`: Post to pages
- `pages_read_engagement`: Read page insights
- `pages_manage_engagement`: Manage page engagement

#### Step 3: Obtain Access Tokens
1. Generate Page Access Token:
   - Go to Graph API Explorer
   - Select your app
   - Select "Page Access Token" in dropdown
   - Select required permissions
   - Generate token

2. Store the token securely in the configuration.

#### Step 4: Configure Facebook Manager
Update the configuration file at `AI_Employee_Vault/Gold_Tier/Social_Suite/Config/facebook_config.json`:

```json
{
  "page_id": "your_facebook_page_id",
  "access_token": "your_facebook_page_access_token",
  "app_id": "your_app_id",
  "app_secret": "your_app_secret",
  "post_schedule": {
    "monday": ["09:00", "15:00"],
    "wednesday": ["09:00", "15:00"],
    "friday": ["09:00", "15:00"]
  },
  "default_hashtags": ["#AI", "#Automation", "#Business"],
  "engagement_monitoring": true
}
```

### Instagram Setup

#### Step 1: Connect Instagram to Facebook
1. Go to your Facebook Page
2. Navigate to Settings → Instagram
3. Follow prompts to connect your Instagram Business Account

#### Step 2: Get Instagram Access Token
1. Use Facebook's Access Token Tool
2. Generate token with required permissions
3. Note the Instagram Account ID

#### Step 3: Configure Instagram Manager
Update the configuration file at `AI_Employee_Vault/Gold_Tier/Social_Suite/Config/instagram_config.json`:

```json
{
  "instagram_account_id": "your_instagram_account_id",
  "access_token": "your_instagram_access_token",
  "app_id": "your_app_id",
  "app_secret": "your_app_secret",
  "post_schedule": {
    "monday": ["08:00", "12:00", "17:00"],
    "tuesday": ["08:00", "12:00", "17:00"],
    "wednesday": ["08:00", "12:00", "17:00"],
    "thursday": ["08:00", "12:00", "17:00"],
    "friday": ["08:00", "12:00", "17:00"]
  },
  "default_hashtags": ["#AI", "#Automation", "#Business", "#Tech"],
  "engagement_monitoring": true,
  "auto_hashtag_generation": true
}
```

### Twitter/X Setup

#### Step 1: Create Twitter Developer Account
1. Apply for Twitter Developer Account at [developer.twitter.com](https://developer.twitter.com/)
2. Create a new app
3. Apply for elevated access for posting capabilities

#### Step 2: Generate API Keys
1. Go to your app's "Keys and Tokens" section
2. Generate:
   - API Key and Secret
   - Access Token and Secret
   - Bearer Token

#### Step 3: Configure Twitter Manager
Update the configuration file at `AI_Employee_Vault/Gold_Tier/Social_Suite/Config/twitter_config.json`:

```json
{
  "api_key": "your_twitter_api_key",
  "api_secret": "your_twitter_api_secret",
  "access_token": "your_twitter_access_token",
  "access_token_secret": "your_twitter_access_token_secret",
  "bearer_token": "your_twitter_bearer_token",
  "twitter_username": "your_twitter_username",
  "post_schedule": {
    "monday": ["07:00", "12:00", "17:00"],
    "tuesday": ["07:00", "12:00", "17:00"],
    "wednesday": ["07:00", "12:00", "17:00"],
    "thursday": ["07:00", "12:00", "17:00"],
    "friday": ["07:00", "12:00", "17:00"],
    "saturday": ["10:00", "15:00"],
    "sunday": ["10:00", "15:00"]
  },
  "default_hashtags": ["#AI", "#Automation", "#Tech", "#Business"],
  "engagement_monitoring": true,
  "auto_hashtag_generation": true,
  "max_tweet_length": 280
}
```

## Content Strategy Integration

### Platform-Specific Content Optimization

#### Facebook Content Guidelines
- **Optimal Length**: 40-80 words
- **Hashtags**: 1-2 hashtags maximum
- **Focus**: Community engagement, conversation starters
- **Best Times**: Tuesday-Thursday 1-4 PM, Saturday 12-1 PM

#### Instagram Content Guidelines
- **Optimal Length**: 125-150 characters for feed posts
- **Hashtags**: 5-10 relevant hashtags
- **Focus**: Visual storytelling, aesthetic consistency
- **Best Times**: Monday/Wednesday 11 AM-1 PM, Friday 10-11 AM

#### Twitter Content Guidelines
- **Optimal Length**: 71-100 characters (sweet spot)
- **Hashtags**: 1-2 hashtags maximum
- **Focus**: Concise, engaging, with questions
- **Best Times**: Weekday mornings and early afternoons

### Cross-Platform Content Strategy
The AI Employee system automatically optimizes content for each platform:

1. **Content Creation**: Single piece of content created
2. **Platform Adaptation**: System adapts content to platform specifications
3. **Scheduling**: Posts distributed according to optimal timing
4. **Tracking**: Performance measured across platforms

## Social Suite Orchestrator

### Configuration
The `social_suite_orchestrator.py` coordinates all platforms:

```json
{
  "cross_platform_posting": true,
  "auto_hashtag_generation": true,
  "engagement_monitoring": true,
  "content_calendar": true,
  "analytics_reporting": true,
  "posting_schedule": {
    "facebook": ["09:00", "15:00"],
    "instagram": ["08:00", "12:00", "17:00"],
    "twitter": ["07:00", "12:00", "17:00"]
  },
  "default_timezone": "UTC",
  "content_approval_required": true
}
```

### Cross-Platform Features
- **Unified Content Calendar**: Single calendar for all platforms
- **Performance Analytics**: Aggregated metrics across platforms
- **Content Scheduling**: Intelligent scheduling based on platform algorithms
- **Engagement Tracking**: Cross-platform engagement measurement

## Content Creation Workflow

### Step 1: Content Discovery
The system identifies content-worthy activities:
- Completed tasks and projects
- Business milestones and achievements
- User requests for specific content
- Trending topics relevant to business

### Step 2: Platform Selection
Based on content type and audience:
- Visual content → Instagram, Facebook
- News/updates → Twitter, Facebook
- Community building → Facebook
- Professional content → LinkedIn (if integrated)

### Step 3: Content Optimization
- Platform-specific formatting
- Optimal hashtag selection
- Timing optimization
- Visual asset preparation

### Step 4: Approval Workflow
All content follows the approval workflow:
1. Content drafted and optimized
2. Approval request created
3. Human review and approval
4. Content published
5. Performance tracking initiated

## Engagement Management

### Monitoring Capabilities
- **Real-time Tracking**: Monitor mentions, comments, and engagement
- **Alert System**: Notify of high-engagement posts or issues
- **Response Drafting**: Suggest responses to comments and messages
- **Trend Analysis**: Identify trending topics and content types

### Automated Responses
The system can automatically:
- Like and engage with relevant content
- Respond to common inquiries
- Schedule follow-up posts
- Identify viral content opportunities

## Analytics and Reporting

### Performance Metrics
- **Reach**: Number of people who saw content
- **Engagement**: Likes, comments, shares, saves
- **Click-through**: Link clicks and traffic generated
- **Conversion**: Actions resulting from social traffic

### Reporting Schedule
- **Daily**: Basic metrics and alerts
- **Weekly**: Comprehensive performance analysis
- **Monthly**: Strategic insights and recommendations
- **Custom**: Ad-hoc reports as needed

### Business Intelligence Integration
Social media metrics feed into the broader business intelligence system:
- CEO briefings include social performance
- ROI calculations include social media impact
- Customer sentiment analysis
- Brand awareness tracking

## Security and Compliance

### Data Protection
- **User Privacy**: Protect personal information
- **Content Rights**: Verify image/video usage rights
- **API Security**: Secure API keys and tokens
- **Audit Logging**: Track all social media actions

### Compliance Measures
- **Platform Terms**: Adhere to each platform's terms of service
- **Advertising Standards**: Follow advertising guidelines
- **Industry Regulations**: Comply with industry-specific rules
- **Geographic Laws**: Consider regional regulations

## Troubleshooting

### Common Issues

#### API Rate Limits
**Symptoms**: Posts fail sporadically, API errors
**Solutions**:
- Implement rate limiting in code
- Monitor API usage
- Add delays between requests
- Use batch operations when possible

#### Authentication Failures
**Symptoms**: Cannot post or access data
**Solutions**:
- Verify access tokens are valid
- Check token expiration
- Regenerate tokens if needed
- Verify app permissions

#### Content Approval Bottlenecks
**Symptoms**: Content queues up without publishing
**Solutions**:
- Review approval workflow
- Adjust approval requirements
- Implement auto-approval for trusted content
- Set up notification system

### Diagnostic Commands
```bash
# Test Facebook connection
python facebook_manager.py

# Test Instagram connection
python instagram_manager.py

# Test Twitter connection
python twitter_manager.py

# Run orchestrator test
python social_suite_orchestrator.py

# Check all configurations
python -c "from social_suite_orchestrator import SocialSuiteOrchestrator; o = SocialSuiteOrchestrator(); print(o.config)"
```

## Maintenance

### Regular Tasks
- **Daily**: Monitor posting schedules and engagement
- **Weekly**: Review analytics and adjust strategy
- **Monthly**: Update API keys and review permissions
- **Quarterly**: Evaluate platform performance and ROI

### Backup Strategy
- Store configuration files securely
- Backup content calendars
- Archive performance data
- Document platform-specific settings

## Integration with Gold Tier Systems

### Business Intelligence
- Social metrics feed into CEO briefings
- Engagement data informs business strategy
- Customer sentiment analysis
- Market trend identification

### Autonomy Engine
- Social media tasks integrated into Ralph Wiggum engine
- Persistent state for multi-step campaigns
- Recovery from interruptions

### Error Recovery
- Failed post recovery
- API error handling
- Platform outage management
- Fallback strategies

## Best Practices

### Content Quality
- Maintain brand consistency across platforms
- Create platform-appropriate content
- Use high-quality visuals
- Engage authentically with audience

### Scheduling
- Post at optimal times for each platform
- Maintain consistent frequency
- Coordinate cross-platform campaigns
- Consider global audience time zones

### Measurement
- Track metrics that matter to business
- Compare performance across platforms
- A/B test content strategies
- Iterate based on data

This integration enables the AI Employee to manage social media presence autonomously while maintaining brand consistency and achieving business objectives.