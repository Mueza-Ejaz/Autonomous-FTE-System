"""
Instagram Manager for Gold Tier
Handles Instagram Business Account integration, posting, and engagement tracking.
"""

import asyncio
import json
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging
import base64


class InstagramManager:
    """Manager for Instagram Business Account integration"""

    def __init__(self, config_path: str = "AI_Employee_Vault/Gold_Tier/Social_Suite/Config/instagram_config.json"):
        self.config_path = Path(config_path)
        self.config = self._load_config()

        # Create social media directories
        social_dir = Path("AI_Employee_Vault/Gold_Tier/Social_Suite/")
        (social_dir / "Instagram").mkdir(parents=True, exist_ok=True)
        (social_dir / "Analytics").mkdir(exist_ok=True)

        # Set up logging
        self.logger = self._setup_logging()

        # Instagram API endpoints
        self.graph_api_url = "https://graph.facebook.com/v18.0"
        self.access_token = self.config.get("access_token", "")
        self.instagram_account_id = self.config.get("instagram_account_id", "")

    def _load_config(self) -> Dict[str, Any]:
        """Load Instagram configuration"""
        default_config = {
            "instagram_account_id": "",
            "access_token": "",
            "app_id": "",
            "app_secret": "",
            "post_schedule": {
                "monday": ["08:00", "12:00", "17:00"],
                "tuesday": ["08:00", "12:00", "17:00"],
                "wednesday": ["08:00", "12:00", "17:00"],
                "thursday": ["08:00", "12:00", "17:00"],
                "friday": ["08:00", "12:00", "17:00"]
            },
            "default_hashtags": ["#AI", "#Automation", "#Business", "#Tech"],
            "engagement_monitoring": True,
            "auto_hashtag_generation": True
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
        """Set up Instagram manager logging"""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)

        # Create file handler
        log_file = Path("AI_Employee_Vault/Gold_Tier/Social_Suite/Instagram/instagram_manager.log")
        file_handler = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        return logger

    def _make_api_call(self, endpoint: str, method: str = "GET", data: Dict = None) -> Optional[Dict[str, Any]]:
        """Make a call to the Instagram Graph API via Facebook"""
        if not self.access_token:
            self.logger.error("No access token configured for Instagram API")
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

            if response.status_code in [200, 201]:
                return response.json()
            else:
                self.logger.error(f"Instagram API error {response.status_code}: {response.text}")
                return None

        except Exception as e:
            self.logger.error(f"Error making Instagram API call: {str(e)}")
            return None

    def create_media_container(self, image_url: str, caption: str, is_carousel_item: bool = False) -> Optional[str]:
        """Create a media container for Instagram post"""
        if not self.instagram_account_id:
            self.logger.error("Instagram account ID not configured")
            return None

        # Prepare the media container data
        container_data = {
            "image_url": image_url,
            "caption": caption,
        }

        if is_carousel_item:
            # For carousel items, we don't set the caption here
            container_data = {
                "image_url": image_url,
            }

        # Make API call to create media container
        endpoint = f"{self.instagram_account_id}/media"
        result = self._make_api_call(endpoint, "POST", container_data)

        if result and "id" in result:
            container_id = result["id"]
            self.logger.info(f"Successfully created Instagram media container: {container_id}")
            return container_id
        else:
            self.logger.error("Failed to create Instagram media container")
            return None

    def create_carousel_container(self, media_items: List[Dict[str, str]], caption: str) -> Optional[str]:
        """Create a carousel media container for Instagram"""
        if not self.instagram_account_id:
            self.logger.error("Instagram account ID not configured")
            return None

        # First, create individual media containers for each image
        container_ids = []
        for item in media_items:
            container_id = self.create_media_container(item["image_url"], "", is_carousel_item=True)
            if container_id:
                container_ids.append(container_id)

        if len(container_ids) == 0:
            self.logger.error("Failed to create any media containers for carousel")
            return None

        # Now create the carousel container
        carousel_data = {
            "children": container_ids,
            "caption": caption
        }

        endpoint = f"{self.instagram_account_id}/media"
        result = self._make_api_call(endpoint, "POST", carousel_data)

        if result and "id" in result:
            container_id = result["id"]
            self.logger.info(f"Successfully created Instagram carousel container: {container_id}")
            return container_id
        else:
            self.logger.error("Failed to create Instagram carousel container")
            return None

    def publish_media(self, container_id: str) -> Optional[str]:
        """Publish a media container to Instagram"""
        if not self.instagram_account_id:
            self.logger.error("Instagram account ID not configured")
            return None

        # Prepare the publish data
        publish_data = {
            "creation_id": container_id
        }

        # Make API call to publish media
        endpoint = f"{self.instagram_account_id}/media_publish"
        result = self._make_api_call(endpoint, "POST", publish_data)

        if result and "id" in result:
            post_id = result["id"]
            self.logger.info(f"Successfully published Instagram post: {post_id}")

            # Track the post
            self._track_post(post_id, "instagram", "Published via media container", datetime.now().isoformat())

            return post_id
        else:
            self.logger.error("Failed to publish Instagram post")
            return None

    def post_image(self, image_url: str, caption: str = "") -> Optional[str]:
        """Post an image to Instagram"""
        # Create media container
        container_id = self.create_media_container(image_url, caption)
        if not container_id:
            return None

        # Publish the media
        post_id = self.publish_media(container_id)
        return post_id

    def post_carousel(self, media_items: List[Dict[str, str]], caption: str = "") -> Optional[str]:
        """Post a carousel to Instagram"""
        # Create carousel container
        container_id = self.create_carousel_container(media_items, caption)
        if not container_id:
            return None

        # Publish the carousel
        post_id = self.publish_media(container_id)
        return post_id

    def get_account_info(self) -> Optional[Dict[str, Any]]:
        """Get Instagram account information"""
        if not self.instagram_account_id:
            self.logger.error("Instagram account ID not configured")
            return None

        fields = "account_type,username,website,name,profile_picture_url,follows_count,followers_count,media_count"
        endpoint = f"{self.instagram_account_id}?fields={fields}"

        result = self._make_api_call(endpoint)

        if result:
            self.logger.info(f"Retrieved Instagram account info for: {result.get('username', 'Unknown')}")
            return result
        else:
            self.logger.error("Failed to retrieve Instagram account info")
            return None

    def get_media_info(self, media_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific media post"""
        fields = "id,caption,media_type,media_url,permalink,timestamp,like_count,comments_count"
        endpoint = f"{media_id}?fields={fields}"

        result = self._make_api_call(endpoint)

        if result:
            self.logger.info(f"Retrieved Instagram media info for: {media_id}")
            return result
        else:
            self.logger.error(f"Failed to retrieve Instagram media info for: {media_id}")
            return None

    def get_recent_media(self, limit: int = 10) -> Optional[List[Dict[str, Any]]]:
        """Get recent media from the account"""
        fields = "id,caption,media_type,media_url,permalink,timestamp,like_count,comments_count"
        endpoint = f"{self.instagram_account_id}/media?fields={fields}&limit={limit}"

        result = self._make_api_call(endpoint)

        if result and "data" in result:
            self.logger.info(f"Retrieved {len(result['data'])} recent Instagram media")
            return result["data"]
        else:
            self.logger.error("Failed to retrieve recent Instagram media")
            return None

    def get_account_insights(self, metric: str = "engagement", period: str = "day") -> Optional[Dict[str, Any]]:
        """Get account-level insights"""
        if not self.instagram_account_id:
            self.logger.error("Instagram account ID not configured")
            return None

        endpoint = f"{self.instagram_account_id}/insights"
        params = {
            "metric": metric,
            "period": period
        }

        result = self._make_api_call(endpoint, "GET", params)

        if result:
            self.logger.info(f"Retrieved Instagram insights for metric: {metric}")
            return result
        else:
            self.logger.error(f"Failed to retrieve Instagram insights for metric: {metric}")
            return None

    def _track_post(self, post_id: str, post_type: str, content: str, timestamp: str):
        """Track post in analytics"""
        analytics_file = Path("AI_Employee_Vault/Gold_Tier/Social_Suite/Analytics/instagram_posts.json")

        tracking_data = {
            "post_id": post_id,
            "type": post_type,
            "content_preview": content[:100] + "..." if len(content) > 100 else content,
            "timestamp": timestamp,
            "platform": "instagram"
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
        """Update Instagram configuration"""
        self.config.update(new_config)

        # Save to file
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)

        self.logger.info("Instagram configuration updated")

        # Update instance variables if needed
        self.access_token = self.config.get("access_token", "")
        self.instagram_account_id = self.config.get("instagram_account_id", "")

    def generate_hashtags(self, content: str) -> List[str]:
        """Generate relevant hashtags based on content"""
        if not self.config.get("auto_hashtag_generation", True):
            return self.config.get("default_hashtags", [])

        # Simple keyword-based hashtag generation
        # In a real implementation, this would use more sophisticated NLP
        content_lower = content.lower()
        keywords = ["ai", "automation", "business", "tech", "startup", "innovation", "digital", "marketing"]

        generated_hashtags = []
        for keyword in keywords:
            if keyword in content_lower:
                hashtag = f"#{keyword.title()}"
                if hashtag not in generated_hashtags:
                    generated_hashtags.append(hashtag)

        # Add default hashtags if we don't have enough
        default_hashtags = self.config.get("default_hashtags", [])
        while len(generated_hashtags) < 5 and default_hashtags:
            for hashtag in default_hashtags:
                if hashtag not in generated_hashtags:
                    generated_hashtags.append(hashtag)
                    if len(generated_hashtags) >= 5:
                        break

        return generated_hashtags[:10]  # Maximum 10 hashtags

    def get_analytics_summary(self) -> Dict[str, Any]:
        """Get summary analytics for Instagram"""
        # Get account info
        account_info = self.get_account_info()

        # Get recent media
        recent_media = self.get_recent_media(limit=5) or []

        # Calculate summary
        total_media = len(recent_media)
        total_likes = sum(media.get("like_count", 0) for media in recent_media)
        total_comments = sum(media.get("comments_count", 0) for media in recent_media)

        # Get account insights
        engagement_insights = self.get_account_insights("engagement", "lifetime")

        summary = {
            "username": account_info.get("username", "Unknown") if account_info else "Not Available",
            "followers": account_info.get("followers_count", 0) if account_info else 0,
            "following": account_info.get("follows_count", 0) if account_info else 0,
            "total_posts": account_info.get("media_count", 0) if account_info else 0,
            "recent_media_count": total_media,
            "recent_likes": total_likes,
            "recent_comments": total_comments,
            "engagement_rate": ((total_likes + total_comments) / max(account_info.get("followers_count", 1), 1)) * 100 if account_info else 0,
            "account_type": account_info.get("account_type", "Unknown") if account_info else "Unknown",
            "engagement_insights": engagement_insights,
            "updated_at": datetime.now().isoformat()
        }

        # Save analytics summary
        analytics_file = Path("AI_Employee_Vault/Gold_Tier/Social_Suite/Analytics/instagram_analytics.json")
        with open(analytics_file, 'w') as f:
            json.dump(summary, f, indent=2)

        return summary

    async def run_engagement_monitoring(self, interval: int = 3600):  # Every hour
        """Run continuous engagement monitoring"""
        if not self.config.get("engagement_monitoring", True):
            self.logger.info("Engagement monitoring disabled")
            return

        self.logger.info("Starting Instagram engagement monitoring...")

        while True:
            try:
                # Get recent media and their insights
                recent_media = self.get_recent_media(limit=10)
                if recent_media:
                    for media in recent_media:
                        media_id = media["id"]

                        # Get detailed media info
                        media_info = self.get_media_info(media_id)

                        if media_info:
                            likes = media_info.get("like_count", 0)
                            comments = media_info.get("comments_count", 0)

                            # Calculate engagement
                            engagement = likes + comments

                            if engagement > 10:  # Threshold for high engagement
                                self.logger.info(f"High engagement detected on post {media_id}: {engagement} (likes: {likes}, comments: {comments})")

                # Wait for next check
                await asyncio.sleep(interval)

            except Exception as e:
                self.logger.error(f"Error in Instagram engagement monitoring: {str(e)}")
                await asyncio.sleep(300)  # Wait 5 minutes before retrying


async def test_instagram_manager():
    """Test the Instagram manager"""
    print("Testing Instagram Manager...")

    # Create manager instance
    ig_manager = InstagramManager()

    # Show current configuration status
    print(f"Instagram account ID configured: {'Yes' if ig_manager.config.get('instagram_account_id') else 'No'}")
    print(f"Access token configured: {'Yes' if ig_manager.config.get('access_token') else 'No'}")

    # Show sample post schedule
    print(f"Post schedule: {ig_manager.config.get('post_schedule', {})}")

    # Show default hashtags
    print(f"Default hashtags: {ig_manager.config.get('default_hashtags', [])}")

    # Show auto hashtag generation
    sample_content = "We're excited to announce our new AI-powered automation system!"
    hashtags = ig_manager.generate_hashtags(sample_content)
    print(f"Generated hashtags for sample content: {hashtags}")

    # Get account info (will fail without proper config, but shows the method)
    print("\nAttempting to get account info...")
    account_info = ig_manager.get_account_info()
    if account_info:
        print(f"Account info retrieved: {account_info}")
    else:
        print("Account info not available (likely due to missing configuration)")

    # Show analytics summary structure
    print("\nAnalytics summary structure:")
    analytics_summary = ig_manager.get_analytics_summary()
    print(json.dumps(analytics_summary, indent=2))

    return True


if __name__ == "__main__":
    asyncio.run(test_instagram_manager())