"""
Social Suite Orchestrator for Gold Tier
Coordinates Facebook, Instagram, and Twitter managers for unified social media management.
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging
from enum import Enum

from facebook_manager import FacebookManager
from instagram_manager import InstagramManager
from twitter_manager import TwitterManager


class SocialPlatform(Enum):
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    TWITTER = "twitter"
    ALL = "all"


class SocialMediaType(Enum):
    POST = "post"
    PHOTO = "photo"
    CAROUSEL = "carousel"
    THREAD = "thread"
    STORY = "story"


class SocialSuiteOrchestrator:
    """Central orchestrator for all social media platforms"""

    def __init__(self, config_path: str = "AI_Employee_Vault/Gold_Tier/Social_Suite/Config/social_suite_config.json"):
        self.config_path = Path(config_path)
        self.config = self._load_config()

        # Create directories
        social_dir = Path("AI_Employee_Vault/Gold_Tier/Social_Suite/")
        (social_dir / "Analytics").mkdir(parents=True, exist_ok=True)
        (social_dir / "Content").mkdir(exist_ok=True)
        (social_dir / "Scheduling").mkdir(exist_ok=True)

        # Initialize platform managers
        self.facebook_manager = FacebookManager()
        self.instagram_manager = InstagramManager()
        self.twitter_manager = TwitterManager()

        # Set up logging
        self.logger = self._setup_logging()

        # Track scheduled posts
        self.scheduled_posts = self._load_scheduled_posts()

    def _load_config(self) -> Dict[str, Any]:
        """Load social suite configuration"""
        default_config = {
            "cross_platform_posting": True,
            "auto_hashtag_generation": True,
            "engagement_monitoring": True,
            "content_calendar": True,
            "analytics_reporting": True,
            "posting_schedule": {
                "facebook": ["09:00", "15:00"],
                "instagram": ["08:00", "12:00", "17:00"],
                "twitter": ["07:00", "12:00", "17:00"]
            },
            "default_timezone": "UTC",
            "content_approval_required": True
        }

        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                config = json.load(f)
                # Merge with defaults to ensure all keys exist
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
        else:
            # Create default config file
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
            return default_config

    def _setup_logging(self) -> logging.Logger:
        """Set up social suite orchestrator logging"""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)

        # Create file handler
        log_file = Path("AI_Employee_Vault/Gold_Tier/Social_Suite/social_suite_orchestrator.log")
        file_handler = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        return logger

    def _load_scheduled_posts(self) -> List[Dict[str, Any]]:
        """Load scheduled posts from storage"""
        scheduled_file = Path("AI_Employee_Vault/Gold_Tier/Social_Suite/Scheduling/scheduled_posts.json")

        if scheduled_file.exists():
            with open(scheduled_file, 'r') as f:
                return json.load(f)
        else:
            return []

    def _save_scheduled_posts(self):
        """Save scheduled posts to storage"""
        scheduled_file = Path("AI_Employee_Vault/Gold_Tier/Social_Suite/Scheduling/scheduled_posts.json")
        scheduled_file.parent.mkdir(parents=True, exist_ok=True)

        with open(scheduled_file, 'w') as f:
            json.dump(self.scheduled_posts, f, indent=2)

    def post_cross_platform(self, content: str, platforms: List[SocialPlatform] = None,
                          media_urls: List[str] = None, scheduled_time: str = None) -> Dict[str, str]:
        """Post content across multiple platforms"""
        if platforms is None:
            platforms = [SocialPlatform.FACEBOOK, SocialPlatform.INSTAGRAM, SocialPlatform.TWITTER]

        results = {}

        # Generate hashtags if enabled
        if self.config.get("auto_hashtag_generation", True):
            # For now, we'll use a simple approach - in reality, each platform might need different hashtags
            hashtags = self._generate_cross_platform_hashtags(content)
            content_with_hashtags = f"{content}\n\n{hashtags}"

        for platform in platforms:
            if platform == SocialPlatform.FACEBOOK:
                if scheduled_time:
                    result = self.facebook_manager.schedule_post(content_with_hashtags, scheduled_time)
                else:
                    result = self.facebook_manager.post_to_page(content_with_hashtags)
                results["facebook"] = result
                self.logger.info(f"Facebook post result: {result}")

            elif platform == SocialPlatform.INSTAGRAM:
                if media_urls:
                    # For Instagram, we need to post an image
                    result = self.instagram_manager.post_image(
                        media_urls[0] if media_urls else "",
                        content_with_hashtags
                    )
                    results["instagram"] = result
                    self.logger.info(f"Instagram post result: {result}")

            elif platform == SocialPlatform.TWITTER:
                # Validate content for Twitter's length limit
                validation = self.twitter_manager.validate_tweet_content(content_with_hashtags)
                if not validation["is_valid"]:
                    self.logger.warning(f"Twitter content invalid: {validation['issues']}")
                    # Truncate content if necessary
                    content_with_hashtags = content_with_hashtags[:250] + "..."

                if scheduled_time:
                    # Twitter doesn't support native scheduling in basic API
                    # We'll need to schedule it ourselves
                    result = self.schedule_post(SocialPlatform.TWITTER, content_with_hashtags, scheduled_time)
                else:
                    result = self.twitter_manager.post_tweet(content_with_hashtags)
                results["twitter"] = result
                self.logger.info(f"Twitter post result: {result}")

        return results

    def _generate_cross_platform_hashtags(self, content: str) -> str:
        """Generate appropriate hashtags for cross-platform posting"""
        # This is a simplified version - in reality, each platform has different hashtag best practices
        # Facebook: 0-2 hashtags
        # Instagram: 5-10 hashtags
        # Twitter: 1-2 hashtags

        # For cross-platform, we'll aim for 2-3 general hashtags that work across platforms
        content_lower = content.lower()
        keywords = ["ai", "automation", "tech", "business", "innovation", "digital", "future", "startup"]

        hashtags = []
        for keyword in keywords:
            if keyword in content_lower and len(hashtags) < 3:
                hashtag = f"#{keyword.title()}"
                if hashtag not in hashtags:
                    hashtags.append(hashtag)

        return " ".join(hashtags) if hashtags else ""

    def schedule_post(self, platform: SocialPlatform, content: str, scheduled_time: str,
                     media_urls: List[str] = None) -> str:
        """Schedule a post for later publication"""
        post_id = f"scheduled_{int(datetime.now().timestamp())}_{hash(content) % 10000}"

        scheduled_post = {
            "id": post_id,
            "platform": platform.value,
            "content": content,
            "scheduled_time": scheduled_time,
            "media_urls": media_urls or [],
            "status": "scheduled",
            "created_at": datetime.now().isoformat()
        }

        self.scheduled_posts.append(scheduled_post)
        self._save_scheduled_posts()

        self.logger.info(f"Scheduled post {post_id} for {platform.value} at {scheduled_time}")
        return post_id

    def execute_scheduled_posts(self):
        """Execute posts that are scheduled for the current time"""
        now = datetime.now()
        executed_count = 0

        for post in self.scheduled_posts:
            if post["status"] == "scheduled":
                scheduled_time = datetime.fromisoformat(post["scheduled_time"])

                # Execute if the scheduled time has passed (within last 5 minutes to handle timing issues)
                if now >= scheduled_time and (now - scheduled_time).total_seconds() <= 300:
                    platform = SocialPlatform(post["platform"])

                    if platform == SocialPlatform.FACEBOOK:
                        result = self.facebook_manager.post_to_page(post["content"])
                    elif platform == SocialPlatform.INSTAGRAM:
                        if post["media_urls"]:
                            result = self.instagram_manager.post_image(
                                post["media_urls"][0], post["content"]
                            )
                        else:
                            result = None
                            self.logger.warning(f"No media URL provided for scheduled Instagram post {post['id']}")
                    elif platform == SocialPlatform.TWITTER:
                        result = self.twitter_manager.post_tweet(post["content"])
                    else:
                        result = None
                        self.logger.warning(f"Unknown platform for scheduled post {post['id']}")

                    if result:
                        post["status"] = "executed"
                        post["executed_at"] = datetime.now().isoformat()
                        post["execution_result"] = result
                        executed_count += 1
                        self.logger.info(f"Executed scheduled post {post['id']} on {platform.value}")
                    else:
                        post["status"] = "failed"
                        post["failed_at"] = datetime.now().isoformat()
                        self.logger.error(f"Failed to execute scheduled post {post['id']} on {platform.value}")

        # Save updated schedule
        self._save_scheduled_posts()

        return executed_count

    def get_cross_platform_analytics(self) -> Dict[str, Any]:
        """Get analytics aggregated across all platforms"""
        facebook_analytics = self.facebook_manager.get_analytics_summary()
        instagram_analytics = self.instagram_manager.get_analytics_summary()
        twitter_analytics = self.twitter_manager.get_analytics_summary()

        # Aggregate metrics
        total_followers = (
            facebook_analytics.get("followers", 0) +
            instagram_analytics.get("followers", 0) +
            twitter_analytics.get("followers", 0)
        )

        total_recent_posts = (
            facebook_analytics.get("recent_posts_count", 0) +
            instagram_analytics.get("recent_media_count", 0) +
            twitter_analytics.get("recent_tweets_count", 0)
        )

        total_recent_engagement = (
            facebook_analytics.get("recent_likes", 0) +
            facebook_analytics.get("recent_comments", 0) +
            instagram_analytics.get("recent_likes", 0) +
            instagram_analytics.get("recent_comments", 0) +
            twitter_analytics.get("recent_likes", 0) +
            twitter_analytics.get("recent_retweets", 0) +
            twitter_analytics.get("recent_replies", 0)
        )

        # Calculate overall engagement rate
        total_reach = max(total_followers, 1)
        overall_engagement_rate = (total_recent_engagement / total_reach) * 100

        cross_platform_analytics = {
            "overview": {
                "total_followers": total_followers,
                "total_recent_posts": total_recent_posts,
                "total_recent_engagement": total_recent_engagement,
                "overall_engagement_rate": round(overall_engagement_rate, 2),
                "platforms_tracked": 3
            },
            "platform_breakdown": {
                "facebook": facebook_analytics,
                "instagram": instagram_analytics,
                "twitter": twitter_analytics
            },
            "comparison": {
                "top_performing_platform": self._determine_top_performing_platform(
                    facebook_analytics, instagram_analytics, twitter_analytics
                ),
                "engagement_by_platform": {
                    "facebook": facebook_analytics.get("recent_likes", 0) + facebook_analytics.get("recent_comments", 0),
                    "instagram": instagram_analytics.get("recent_likes", 0) + instagram_analytics.get("recent_comments", 0),
                    "twitter": twitter_analytics.get("recent_likes", 0) + twitter_analytics.get("recent_retweets", 0)
                }
            },
            "updated_at": datetime.now().isoformat()
        }

        # Save to analytics file
        analytics_file = Path("AI_Employee_Vault/Gold_Tier/Social_Suite/Analytics/cross_platform_analytics.json")
        with open(analytics_file, 'w') as f:
            json.dump(cross_platform_analytics, f, indent=2)

        return cross_platform_analytics

    def _determine_top_performing_platform(self, fb_analytics: Dict, ig_analytics: Dict, tw_analytics: Dict) -> str:
        """Determine which platform is performing best based on engagement"""
        fb_engagement = fb_analytics.get("recent_likes", 0) + fb_analytics.get("recent_comments", 0)
        ig_engagement = ig_analytics.get("recent_likes", 0) + ig_analytics.get("recent_comments", 0)
        tw_engagement = tw_analytics.get("recent_likes", 0) + tw_analytics.get("recent_retweets", 0)

        max_engagement = max(fb_engagement, ig_engagement, tw_engagement)

        if max_engagement == fb_engagement:
            return "facebook"
        elif max_engagement == ig_engagement:
            return "instagram"
        else:
            return "twitter"

    def create_content_calendar(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Create a content calendar for the specified date range"""
        from datetime import datetime, timedelta

        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")

        calendar = []
        current_date = start

        while current_date <= end:
            date_str = current_date.strftime("%Y-%m-%d")

            # Get scheduled posts for this date
            day_posts = [
                post for post in self.scheduled_posts
                if post["scheduled_time"].startswith(date_str) and post["status"] == "scheduled"
            ]

            calendar.append({
                "date": date_str,
                "day_of_week": current_date.strftime("%A"),
                "posts": day_posts,
                "post_count": len(day_posts)
            })

            current_date += timedelta(days=1)

        # Save calendar
        calendar_file = Path("AI_Employee_Vault/Gold_Tier/Social_Suite/Content/content_calendar.json")
        with open(calendar_file, 'w') as f:
            json.dump(calendar, f, indent=2)

        self.logger.info(f"Created content calendar for {start_date} to {end_date}")
        return calendar

    def optimize_post_timing(self, platform: SocialPlatform) -> List[str]:
        """Suggest optimal posting times based on platform analytics"""
        if platform == SocialPlatform.FACEBOOK:
            # Facebook: Typically best times are Tuesday-Thursday 1-4 PM
            return ["13:00", "14:00", "15:00", "16:00"]
        elif platform == SocialPlatform.INSTAGRAM:
            # Instagram: Typically best times are Wednesday-Friday 11 AM-1 PM
            return ["11:00", "12:00", "13:00"]
        elif platform == SocialPlatform.TWITTER:
            # Twitter: Typically best times are Tuesday-Thursday 8-10 AM and 7-9 PM
            return ["08:00", "09:00", "19:00", "20:00", "21:00"]
        else:
            return ["09:00", "12:00", "17:00"]  # Default times

    def get_recommendation_for_content(self, content_type: str, goal: str = "engagement") -> Dict[str, Any]:
        """Provide recommendations for content based on type and goal"""
        recommendations = {
            "content_type": content_type,
            "goal": goal,
            "best_platforms": [],
            "format_suggestions": [],
            "timing_suggestions": [],
            "hashtag_suggestions": [],
            "additional_tips": []
        }

        if content_type == "educational":
            recommendations["best_platforms"] = ["twitter", "linkedin"]  # Assuming LinkedIn integration
            recommendations["format_suggestions"] = ["thread", "article", "infographic"]
            recommendations["timing_suggestions"] = ["08:00", "12:00", "17:00"]
            recommendations["hashtag_suggestions"] = ["#Education", "#Learn", "#Knowledge", "#Tips"]
            recommendations["additional_tips"] = ["Use clear, informative language", "Include sources when possible"]

        elif content_type == "promotional":
            recommendations["best_platforms"] = ["instagram", "facebook"]
            recommendations["format_suggestions"] = ["image", "video", "carousel"]
            recommendations["timing_suggestions"] = ["09:00", "15:00"]
            recommendations["hashtag_suggestions"] = ["#Ad", "#Promotion", "#Offer", "#Deal"]
            recommendations["additional_tips"] = ["Include eye-catching visuals", "Keep text concise"]

        elif content_type == "engagement":
            recommendations["best_platforms"] = ["twitter", "instagram"]
            recommendations["format_suggestions"] = ["poll", "question", "interactive"]
            recommendations["timing_suggestions"] = ["12:00", "18:00"]
            recommendations["hashtag_suggestions"] = ["#Engage", "#Discuss", "#Share", "#Opinion"]
            recommendations["additional_tips"] = ["Ask questions", "Encourage comments"]

        return recommendations

    def update_config(self, new_config: Dict[str, Any]):
        """Update social suite configuration"""
        self.config.update(new_config)

        # Save to file
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)

        self.logger.info("Social suite configuration updated")

    async def run_scheduled_posting(self, interval: int = 60):  # Check every minute
        """Run continuous scheduled posting monitor"""
        self.logger.info("Starting scheduled posting monitor...")

        while True:
            try:
                executed_count = self.execute_scheduled_posts()
                if executed_count > 0:
                    self.logger.info(f"Executed {executed_count} scheduled posts")

                # Wait for next check
                await asyncio.sleep(interval)

            except Exception as e:
                self.logger.error(f"Error in scheduled posting: {str(e)}")
                await asyncio.sleep(300)  # Wait 5 minutes before retrying

    async def run_analytics_reporting(self, interval: int = 3600):  # Run every hour
        """Run continuous analytics reporting"""
        if not self.config.get("analytics_reporting", True):
            self.logger.info("Analytics reporting disabled")
            return

        self.logger.info("Starting analytics reporting...")

        while True:
            try:
                # Get cross-platform analytics
                analytics = self.get_cross_platform_analytics()

                self.logger.info(f"Analytics updated. Total followers across platforms: {analytics['overview']['total_followers']}")

                # Wait for next report
                await asyncio.sleep(interval)

            except Exception as e:
                self.logger.error(f"Error in analytics reporting: {str(e)}")
                await asyncio.sleep(300)  # Wait 5 minutes before retrying


async def test_social_suite_orchestrator():
    """Test the social suite orchestrator"""
    print("Testing Social Suite Orchestrator...")

    orchestrator = SocialSuiteOrchestrator()

    # Show configuration
    print(f"Cross-platform posting enabled: {orchestrator.config.get('cross_platform_posting')}")
    print(f"Auto-hashtag generation enabled: {orchestrator.config.get('auto_hashtag_generation')}")
    print(f"Engagement monitoring enabled: {orchestrator.config.get('engagement_monitoring')}")

    # Show scheduled posts
    print(f"Scheduled posts count: {len(orchestrator.scheduled_posts)}")

    # Test cross-platform posting (without actually posting due to missing credentials)
    content = "Excited to share our latest innovation in AI-powered automation!"
    platforms = [SocialPlatform.FACEBOOK, SocialPlatform.INSTAGRAM, SocialPlatform.TWITTER]

    print(f"\nTesting cross-platform hashtag generation...")
    hashtags = orchestrator._generate_cross_platform_hashtags(content)
    print(f"Generated hashtags: {hashtags}")

    # Test content calendar creation
    print(f"\nTesting content calendar creation...")
    calendar = orchestrator.create_content_calendar("2026-02-01", "2026-02-07")
    print(f"Created calendar for 7 days with {len(calendar)} entries")

    # Test platform recommendations
    print(f"\nTesting platform recommendations...")
    edu_recs = orchestrator.get_recommendation_for_content("educational", "engagement")
    print(f"Educational content recommendations: {edu_recs['best_platforms']}")

    prom_recs = orchestrator.get_recommendation_for_content("promotional", "reach")
    print(f"Promotional content recommendations: {prom_recs['best_platforms']}")

    # Test optimal timing
    print(f"\nTesting optimal timing suggestions...")
    fb_times = orchestrator.optimize_post_timing(SocialPlatform.FACEBOOK)
    ig_times = orchestrator.optimize_post_timing(SocialPlatform.INSTAGRAM)
    tw_times = orchestrator.optimize_post_timing(SocialPlatform.TWITTER)

    print(f"Facebook optimal times: {fb_times}")
    print(f"Instagram optimal times: {ig_times}")
    print(f"Twitter optimal times: {tw_times}")

    # Test cross-platform analytics aggregation
    print(f"\nTesting cross-platform analytics...")
    try:
        analytics = orchestrator.get_cross_platform_analytics()
        print(f"Analytics overview: {analytics['overview']}")
    except Exception as e:
        print(f"Analytics test failed (expected due to missing credentials): {str(e)}")

    return True


if __name__ == "__main__":
    asyncio.run(test_social_suite_orchestrator())