"""
Facebook Manager for Gold Tier
Handles Facebook Page integration, posting, and engagement tracking.
"""

import asyncio
import json
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging


class FacebookManager:
    """Manager for Facebook Page integration"""

    def __init__(self, config_path: str = "AI_Employee_Vault/Gold_Tier/Social_Suite/Config/facebook_config.json"):
        self.config_path = Path(config_path)
        self.config = self._load_config()

        # Create social media directories
        social_dir = Path("AI_Employee_Vault/Gold_Tier/Social_Suite/")
        (social_dir / "Facebook").mkdir(parents=True, exist_ok=True)
        (social_dir / "Analytics").mkdir(exist_ok=True)

        # Set up logging
        self.logger = self._setup_logging()

        # Facebook API endpoints
        self.graph_api_url = "https://graph.facebook.com/v18.0"
        self.access_token = self.config.get("access_token", "")

    def _load_config(self) -> Dict[str, Any]:
        """Load Facebook configuration"""
        default_config = {
            "page_id": "",
            "access_token": "",
            "app_id": "",
            "app_secret": "",
            "post_schedule": {
                "monday": ["09:00", "15:00"],
                "wednesday": ["09:00", "15:00"],
                "friday": ["09:00", "15:00"]
            },
            "default_hashtags": [],
            "engagement_monitoring": True
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
        """Set up Facebook manager logging"""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)

        # Create file handler
        log_file = Path("AI_Employee_Vault/Gold_Tier/Social_Suite/Facebook/facebook_manager.log")
        file_handler = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        return logger

    def _make_api_call(self, endpoint: str, method: str = "GET", data: Dict = None) -> Optional[Dict[str, Any]]:
        """Make a call to the Facebook Graph API"""
        if not self.access_token:
            self.logger.error("No access token configured for Facebook API")
            return None

        url = f"{self.graph_api_url}/{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, params=data)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json=data)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            if response.status_code == 200:
                return response.json()
            else:
                self.logger.error(f"Facebook API error {response.status_code}: {response.text}")
                return None

        except Exception as e:
            self.logger.error(f"Error making Facebook API call: {str(e)}")
            return None

    def post_to_page(self, message: str, link: str = None, image_urls: List[str] = None) -> Optional[str]:
        """Post content to Facebook page"""
        if not self.config.get("page_id"):
            self.logger.error("Page ID not configured")
            return None

        # Prepare post data
        post_data = {
            "message": message
        }

        if link:
            post_data["link"] = link

        # Make API call to create post
        result = self._make_api_call(f"{self.config['page_id']}/feed", "POST", post_data)

        if result and "id" in result:
            post_id = result["id"]
            self.logger.info(f"Successfully posted to Facebook: {post_id}")

            # Track the post
            self._track_post(post_id, "facebook", message, datetime.now().isoformat())

            return post_id
        else:
            self.logger.error("Failed to post to Facebook")
            return None

    def post_photo_to_page(self, image_url: str, caption: str = "") -> Optional[str]:
        """Post a photo to Facebook page"""
        if not self.config.get("page_id"):
            self.logger.error("Page ID not configured")
            return None

        # Upload photo first
        upload_data = {
            "url": image_url,
            "published": False  # Don't publish yet, we'll attach caption
        }

        result = self._make_api_call(f"{self.config['page_id']}/photos", "POST", upload_data)

        if result and "id" in result:
            photo_id = result["id"]

            # Now create a post with the photo and caption
            post_data = {
                "attached_media": [{"media_fbid": photo_id}],
                "message": caption
            }

            post_result = self._make_api_call(f"{self.config['page_id']}/feed", "POST", post_data)

            if post_result and "id" in post_result:
                post_id = post_result["id"]
                self.logger.info(f"Successfully posted photo to Facebook: {post_id}")

                # Track the post
                self._track_post(post_id, "facebook_photo", caption, datetime.now().isoformat())

                return post_id
            else:
                self.logger.error("Failed to create Facebook post with photo")
                return None
        else:
            self.logger.error("Failed to upload photo to Facebook")
            return None

    def get_page_info(self) -> Optional[Dict[str, Any]]:
        """Get Facebook page information"""
        if not self.config.get("page_id"):
            self.logger.error("Page ID not configured")
            return None

        fields = "name,fan_count,talking_about_count,category"
        result = self._make_api_call(f"{self.config['page_id']}?fields={fields}")

        if result:
            self.logger.info(f"Retrieved Facebook page info for: {result.get('name', 'Unknown')}")
            return result
        else:
            self.logger.error("Failed to retrieve Facebook page info")
            return None

    def get_post_insights(self, post_id: str) -> Optional[Dict[str, Any]]:
        """Get insights for a specific post"""
        fields = "engagement,impressions,reactions.summary(true),comments.summary(true),shares"
        result = self._make_api_call(f"{post_id}/insights?metric={fields}")

        if result:
            self.logger.info(f"Retrieved insights for Facebook post: {post_id}")
            return result
        else:
            self.logger.error(f"Failed to retrieve insights for Facebook post: {post_id}")
            return None

    def get_page_posts(self, limit: int = 10) -> Optional[List[Dict[str, Any]]]:
        """Get recent posts from the page"""
        fields = "id,message,created_time,likes.summary(true),comments.summary(true),shares"
        result = self._make_api_call(f"{self.config['page_id']}/posts?fields={fields}&limit={limit}")

        if result and "data" in result:
            self.logger.info(f"Retrieved {len(result['data'])} recent Facebook posts")
            return result["data"]
        else:
            self.logger.error("Failed to retrieve Facebook page posts")
            return None

    def schedule_post(self, message: str, scheduled_time: str, link: str = None) -> Optional[str]:
        """Schedule a post for later publication"""
        if not self.config.get("page_id"):
            self.logger.error("Page ID not configured")
            return None

        post_data = {
            "message": message,
            "published": False,  # Don't publish immediately
            "scheduled_publish_time": scheduled_time  # ISO 8601 format
        }

        if link:
            post_data["link"] = link

        result = self._make_api_call(f"{self.config['page_id']}/feed", "POST", post_data)

        if result and "id" in result:
            post_id = result["id"]
            self.logger.info(f"Successfully scheduled Facebook post: {post_id} for {scheduled_time}")
            return post_id
        else:
            self.logger.error("Failed to schedule Facebook post")
            return None

    def _track_post(self, post_id: str, post_type: str, content: str, timestamp: str):
        """Track post in analytics"""
        analytics_file = Path("AI_Employee_Vault/Gold_Tier/Social_Suite/Analytics/facebook_posts.json")

        tracking_data = {
            "post_id": post_id,
            "type": post_type,
            "content_preview": content[:100] + "..." if len(content) > 100 else content,
            "timestamp": timestamp,
            "platform": "facebook"
        }

        # Load existing data or create new
        if analytics_file.exists():
            with open(analytics_file, 'r') as f:
                data = json.load(f)
        else:
            data = {"posts": []}

        # Add new tracking data
        data["posts"].append(tracking_data)

        # Save back to file
        with open(analytics_file, 'w') as f:
            json.dump(data, f, indent=2)

    def update_config(self, new_config: Dict[str, Any]):
        """Update Facebook configuration"""
        self.config.update(new_config)

        # Save to file
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)

        self.logger.info("Facebook configuration updated")

        # Update instance variables if needed
        self.access_token = self.config.get("access_token", "")

    def get_analytics_summary(self) -> Dict[str, Any]:
        """Get summary analytics for Facebook"""
        # Get page info
        page_info = self.get_page_info()

        # Get recent posts
        recent_posts = self.get_page_posts(limit=5) or []

        # Calculate summary
        total_posts = len(recent_posts)
        total_likes = sum(post.get("likes", {}).get("summary", {}).get("total_count", 0) for post in recent_posts)
        total_comments = sum(post.get("comments", {}).get("summary", {}).get("total_count", 0) for post in recent_posts)

        summary = {
            "page_name": page_info.get("name", "Unknown") if page_info else "Not Available",
            "followers": page_info.get("fan_count", 0) if page_info else 0,
            "talking_about": page_info.get("talking_about_count", 0) if page_info else 0,
            "recent_posts_count": total_posts,
            "recent_likes": total_likes,
            "recent_comments": total_comments,
            "engagement_rate": ((total_likes + total_comments) / max(page_info.get("fan_count", 1), 1)) * 100 if page_info else 0,
            "updated_at": datetime.now().isoformat()
        }

        # Save analytics summary
        analytics_file = Path("AI_Employee_Vault/Gold_Tier/Social_Suite/Analytics/facebook_analytics.json")
        with open(analytics_file, 'w') as f:
            json.dump(summary, f, indent=2)

        return summary

    async def run_engagement_monitoring(self, interval: int = 3600):  # Every hour
        """Run continuous engagement monitoring"""
        if not self.config.get("engagement_monitoring", True):
            self.logger.info("Engagement monitoring disabled")
            return

        self.logger.info("Starting Facebook engagement monitoring...")

        while True:
            try:
                # Get recent posts and their insights
                recent_posts = self.get_page_posts(limit=10)
                if recent_posts:
                    for post in recent_posts:
                        post_id = post["id"]
                        insights = self.get_post_insights(post_id)

                        if insights:
                            # Process insights and look for engagement
                            reactions = insights.get("data", [{}])[0].get("values", [{}])[0].get("value", {}).get("reactions", 0)

                            if reactions > 10:  # Threshold for high engagement
                                self.logger.info(f"High engagement detected on post {post_id}: {reactions} reactions")

                # Wait for next check
                await asyncio.sleep(interval)

            except Exception as e:
                self.logger.error(f"Error in Facebook engagement monitoring: {str(e)}")
                await asyncio.sleep(300)  # Wait 5 minutes before retrying


async def test_facebook_manager():
    """Test the Facebook manager"""
    print("Testing Facebook Manager...")

    # Create manager instance
    fb_manager = FacebookManager()

    # Show current configuration status
    print(f"Page ID configured: {'Yes' if fb_manager.config.get('page_id') else 'No'}")
    print(f"Access token configured: {'Yes' if fb_manager.config.get('access_token') else 'No'}")

    # Show sample post schedule
    print(f"Post schedule: {fb_manager.config.get('post_schedule', {})}")

    # Show default hashtags
    print(f"Default hashtags: {fb_manager.config.get('default_hashtags', [])}")

    # Get page info (will fail without proper config, but shows the method)
    print("\nAttempting to get page info...")
    page_info = fb_manager.get_page_info()
    if page_info:
        print(f"Page info retrieved: {page_info}")
    else:
        print("Page info not available (likely due to missing configuration)")

    # Show analytics summary structure
    print("\nAnalytics summary structure:")
    analytics_summary = fb_manager.get_analytics_summary()
    print(json.dumps(analytics_summary, indent=2))

    return True


if __name__ == "__main__":
    asyncio.run(test_facebook_manager())