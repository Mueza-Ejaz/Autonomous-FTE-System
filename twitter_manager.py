"""
Twitter Manager for Gold Tier
Handles Twitter/X integration, posting, and engagement tracking.
"""

import asyncio
import json
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging
import tweepy


class TwitterManager:
    """Manager for Twitter/X integration"""

    def __init__(self, config_path: str = "AI_Employee_Vault/Gold_Tier/Social_Suite/Config/twitter_config.json"):
        self.config_path = Path(config_path)
        self.config = self._load_config()

        # Create social media directories
        social_dir = Path("AI_Employee_Vault/Gold_Tier/Social_Suite/")
        (social_dir / "Twitter").mkdir(parents=True, exist_ok=True)
        (social_dir / "Analytics").mkdir(exist_ok=True)

        # Set up logging
        self.logger = self._setup_logging()

        # Twitter API setup
        self.api_client = self._setup_api_client()

    def _load_config(self) -> Dict[str, Any]:
        """Load Twitter configuration"""
        default_config = {
            "api_key": "",
            "api_secret": "",
            "access_token": "",
            "access_token_secret": "",
            "bearer_token": "",
            "twitter_username": "",
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
            "engagement_monitoring": True,
            "auto_hashtag_generation": True,
            "max_tweet_length": 280
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
        """Set up Twitter manager logging"""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)

        # Create file handler
        log_file = Path("AI_Employee_Vault/Gold_Tier/Social_Suite/Twitter/twitter_manager.log")
        file_handler = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        return logger

    def _setup_api_client(self):
        """Set up Twitter API client"""
        try:
            # Use tweepy for Twitter API v2
            client = tweepy.Client(
                bearer_token=self.config.get("bearer_token", ""),
                consumer_key=self.config.get("api_key", ""),
                consumer_secret=self.config.get("api_secret", ""),
                access_token=self.config.get("access_token", ""),
                access_token_secret=self.config.get("access_token_secret", ""),
                wait_on_rate_limit=True
            )
            return client
        except Exception as e:
            self.logger.error(f"Error setting up Twitter API client: {str(e)}")
            return None

    def post_tweet(self, text: str, media_urls: List[str] = None) -> Optional[str]:
        """Post a tweet to Twitter"""
        if not self.api_client:
            self.logger.error("Twitter API client not configured")
            return None

        try:
            # Handle media uploads if provided
            media_ids = []
            if media_urls:
                # Note: Actual media upload would require tweepy's media upload methods
                # This is a simplified version - in reality, you'd need to upload media first
                self.logger.warning("Media uploading not fully implemented in this version")

            # Post the tweet
            response = self.api_client.create_tweet(text=text)

            if response.data and 'id' in response.data:
                tweet_id = response.data['id']
                self.logger.info(f"Successfully posted tweet: {tweet_id}")

                # Track the post
                self._track_post(tweet_id, "twitter", text, datetime.now().isoformat())

                return str(tweet_id)
            else:
                self.logger.error("Failed to post tweet - no ID in response")
                return None

        except Exception as e:
            self.logger.error(f"Error posting tweet: {str(e)}")
            return None

    def post_thread(self, tweets: List[str]) -> Optional[List[str]]:
        """Post a thread of tweets"""
        if not self.api_client:
            self.logger.error("Twitter API client not configured")
            return None

        try:
            tweet_ids = []
            prev_tweet_id = None

            for i, tweet_text in enumerate(tweets):
                try:
                    if i == 0:
                        # First tweet doesn't need to reply to anything
                        response = self.api_client.create_tweet(text=tweet_text)
                    else:
                        # Subsequent tweets reply to the previous one
                        response = self.api_client.create_tweet(
                            text=tweet_text,
                            in_reply_to_tweet_id=prev_tweet_id
                        )

                    if response.data and 'id' in response.data:
                        tweet_id = response.data['id']
                        tweet_ids.append(str(tweet_id))

                        # Track each tweet in the thread
                        self._track_post(tweet_id, "twitter_thread", tweet_text, datetime.now().isoformat())

                        prev_tweet_id = tweet_id
                        self.logger.info(f"Posted thread tweet {i+1}/{len(tweets)}: {tweet_id}")
                    else:
                        self.logger.error(f"Failed to post thread tweet {i+1}")
                        break

                except Exception as e:
                    self.logger.error(f"Error posting thread tweet {i+1}: {str(e)}")
                    break

            if len(tweet_ids) == len(tweets):
                self.logger.info(f"Successfully posted thread of {len(tweet_ids)} tweets")
                return tweet_ids
            else:
                self.logger.warning(f"Partially posted thread: {len(tweet_ids)}/{len(tweets)} tweets")
                return tweet_ids

        except Exception as e:
            self.logger.error(f"Error posting thread: {str(e)}")
            return None

    def get_user_info(self) -> Optional[Dict[str, Any]]:
        """Get Twitter user information"""
        if not self.api_client:
            self.logger.error("Twitter API client not configured")
            return None

        try:
            # Get user by username from config
            username = self.config.get("twitter_username", "")
            if not username:
                self.logger.error("Twitter username not configured")
                return None

            response = self.api_client.get_user(username=username,
                                             user_fields=["public_metrics", "created_at", "description"])

            if response.data:
                user_data = response.data.data
                self.logger.info(f"Retrieved Twitter user info for: @{user_data['username']}")
                return user_data
            else:
                self.logger.error("Failed to retrieve Twitter user info")
                return None

        except Exception as e:
            self.logger.error(f"Error getting user info: {str(e)}")
            return None

    def get_tweet_info(self, tweet_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific tweet"""
        if not self.api_client:
            self.logger.error("Twitter API client not configured")
            return None

        try:
            response = self.api_client.get_tweet(
                id=tweet_id,
                tweet_fields=["public_metrics", "created_at", "author_id", "context_annotations"]
            )

            if response.data:
                tweet_data = response.data.data
                self.logger.info(f"Retrieved Twitter tweet info for: {tweet_id}")
                return tweet_data
            else:
                self.logger.error(f"Failed to retrieve Twitter tweet info for: {tweet_id}")
                return None

        except Exception as e:
            self.logger.error(f"Error getting tweet info: {str(e)}")
            return None

    def get_recent_tweets(self, limit: int = 10) -> Optional[List[Dict[str, Any]]]:
        """Get recent tweets from the user"""
        if not self.api_client:
            self.logger.error("Twitter API client not configured")
            return None

        try:
            username = self.config.get("twitter_username", "")
            if not username:
                self.logger.error("Twitter username not configured")
                return None

            # Get user ID first
            user_response = self.api_client.get_user(username=username)
            if not user_response.data or 'id' not in user_response.data:
                self.logger.error("Could not get user ID")
                return None

            user_id = user_response.data.data['id']

            # Get user's tweets
            response = self.api_client.get_users_tweets(
                id=user_id,
                max_results=min(limit, 100),  # Twitter API max is 100
                tweet_fields=["public_metrics", "created_at", "context_annotations"]
            )

            if response.data:
                tweets = response.data.data if hasattr(response.data, 'data') else []
                self.logger.info(f"Retrieved {len(tweets)} recent tweets from @{username}")
                return tweets
            else:
                self.logger.error("Failed to retrieve recent tweets")
                return None

        except Exception as e:
            self.logger.error(f"Error getting recent tweets: {str(e)}")
            return None

    def search_tweets(self, query: str, limit: int = 10) -> Optional[List[Dict[str, Any]]]:
        """Search for tweets matching a query"""
        if not self.api_client:
            self.logger.error("Twitter API client not configured")
            return None

        try:
            response = self.api_client.search_recent_tweets(
                query=query,
                max_results=min(limit, 100),
                tweet_fields=["public_metrics", "created_at", "author_id"]
            )

            if response.data:
                tweets = response.data.data if hasattr(response.data, 'data') else []
                self.logger.info(f"Found {len(tweets)} tweets matching query: {query}")
                return tweets
            else:
                self.logger.error(f"Failed to search tweets for query: {query}")
                return None

        except Exception as e:
            self.logger.error(f"Error searching tweets: {str(e)}")
            return None

    def like_tweet(self, tweet_id: str) -> bool:
        """Like a tweet"""
        if not self.api_client:
            self.logger.error("Twitter API client not configured")
            return False

        try:
            response = self.api_client.like(tweet_id)
            if response.data and 'liked' in response.data:
                self.logger.info(f"Successfully liked tweet: {tweet_id}")
                return True
            else:
                self.logger.error(f"Failed to like tweet: {tweet_id}")
                return False
        except Exception as e:
            self.logger.error(f"Error liking tweet {tweet_id}: {str(e)}")
            return False

    def retweet(self, tweet_id: str) -> bool:
        """Retweet a tweet"""
        if not self.api_client:
            self.logger.error("Twitter API client not configured")
            return False

        try:
            response = self.api_client.retweet(tweet_id)
            if response.data and 'retweeted' in response.data:
                self.logger.info(f"Successfully retweeted: {tweet_id}")
                return True
            else:
                self.logger.error(f"Failed to retweet: {tweet_id}")
                return False
        except Exception as e:
            self.logger.error(f"Error retweeting {tweet_id}: {str(e)}")
            return False

    def follow_user(self, username: str) -> bool:
        """Follow a user"""
        if not self.api_client:
            self.logger.error("Twitter API client not configured")
            return False

        try:
            # First get user ID
            user_response = self.api_client.get_user(username=username)
            if not user_response.data or 'id' not in user_response.data:
                self.logger.error(f"Could not find user: {username}")
                return False

            user_id = user_response.data.data['id']

            # Follow the user
            response = self.api_client.follow_user(user_id)
            if response.data and 'following' in response.data:
                self.logger.info(f"Successfully followed user: {username}")
                return True
            else:
                self.logger.error(f"Failed to follow user: {username}")
                return False
        except Exception as e:
            self.logger.error(f"Error following user {username}: {str(e)}")
            return False

    def _track_post(self, post_id: str, post_type: str, content: str, timestamp: str):
        """Track post in analytics"""
        analytics_file = Path("AI_Employee_Vault/Gold_Tier/Social_Suite/Analytics/twitter_posts.json")

        tracking_data = {
            "post_id": post_id,
            "type": post_type,
            "content_preview": content[:100] + "..." if len(content) > 100 else content,
            "timestamp": timestamp,
            "platform": "twitter"
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
        """Update Twitter configuration"""
        self.config.update(new_config)

        # Save to file
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)

        self.logger.info("Twitter configuration updated")

        # Update API client with new credentials
        self.api_client = self._setup_api_client()

    def validate_tweet_content(self, text: str) -> Dict[str, Any]:
        """Validate tweet content for Twitter requirements"""
        issues = []

        # Check length
        if len(text) > self.config.get("max_tweet_length", 280):
            issues.append(f"Tweet is too long: {len(text)} characters (max: 280)")

        # Check for URLs (they take 23 characters regardless of actual length)
        import re
        urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
        url_placeholder_length = len(urls) * 23
        text_without_urls = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        effective_length = len(text_without_urls) + url_placeholder_length

        if effective_length > 280:
            issues.append(f"Tweet with URL shortening would be too long: {effective_length} effective characters")

        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
            "length": len(text),
            "effective_length": effective_length,
            "max_length": 280
        }

    def generate_hashtags(self, content: str) -> List[str]:
        """Generate relevant hashtags based on content"""
        if not self.config.get("auto_hashtag_generation", True):
            return self.config.get("default_hashtags", [])

        # Simple keyword-based hashtag generation
        content_lower = content.lower()
        keywords = ["ai", "automation", "tech", "business", "startup", "innovation", "digital", "marketing", "future"]

        generated_hashtags = []
        for keyword in keywords:
            if keyword in content_lower:
                hashtag = f"#{keyword.title()}"
                if hashtag not in generated_hashtags:
                    generated_hashtags.append(hashtag)

        # Add default hashtags if we don't have enough
        default_hashtags = self.config.get("default_hashtags", [])
        while len(generated_hashtags) < 2 and default_hashtags:  # Twitter recommends 1-2 hashtags
            for hashtag in default_hashtags:
                if hashtag not in generated_hashtags:
                    generated_hashtags.append(hashtag)
                    if len(generated_hashtags) >= 2:
                        break

        return generated_hashtags[:2]  # Maximum 2 hashtags for Twitter

    def get_analytics_summary(self) -> Dict[str, Any]:
        """Get summary analytics for Twitter"""
        # Get user info
        user_info = self.get_user_info()

        # Get recent tweets
        recent_tweets = self.get_recent_tweets(limit=5) or []

        # Calculate summary
        total_tweets = len(recent_tweets)
        total_likes = sum(tweet.get("public_metrics", {}).get("like_count", 0) for tweet in recent_tweets)
        total_retweets = sum(tweet.get("public_metrics", {}).get("retweet_count", 0) for tweet in recent_tweets)
        total_replies = sum(tweet.get("public_metrics", {}).get("reply_count", 0) for tweet in recent_tweets)
        total_quotes = sum(tweet.get("public_metrics", {}).get("quote_count", 0) for tweet in recent_tweets)

        summary = {
            "username": user_info.get("username", "Unknown") if user_info else "Not Available",
            "display_name": user_info.get("name", "Unknown") if user_info else "Not Available",
            "followers": user_info.get("public_metrics", {}).get("followers_count", 0) if user_info else 0,
            "following": user_info.get("public_metrics", {}).get("following_count", 0) if user_info else 0,
            "tweets_count": user_info.get("public_metrics", {}).get("tweet_count", 0) if user_info else 0,
            "recent_tweets_count": total_tweets,
            "recent_likes": total_likes,
            "recent_retweets": total_retweets,
            "recent_replies": total_replies,
            "recent_quotes": total_quotes,
            "engagement_rate": ((total_likes + total_retweets + total_replies) / max(user_info.get("public_metrics", {}).get("followers_count", 1), 1)) * 100 if user_info else 0,
            "account_created": user_info.get("created_at", "Unknown") if user_info else "Unknown",
            "updated_at": datetime.now().isoformat()
        }

        # Save analytics summary
        analytics_file = Path("AI_Employee_Vault/Gold_Tier/Social_Suite/Analytics/twitter_analytics.json")
        with open(analytics_file, 'w') as f:
            json.dump(summary, f, indent=2)

        return summary

    async def run_engagement_monitoring(self, interval: int = 1800):  # Every 30 minutes
        """Run continuous engagement monitoring"""
        if not self.config.get("engagement_monitoring", True):
            self.logger.info("Engagement monitoring disabled")
            return

        self.logger.info("Starting Twitter engagement monitoring...")

        while True:
            try:
                # Get recent tweets and their metrics
                recent_tweets = self.get_recent_tweets(limit=10)
                if recent_tweets:
                    for tweet in recent_tweets:
                        tweet_id = tweet["id"]
                        tweet_metrics = tweet.get("public_metrics", {})

                        likes = tweet_metrics.get("like_count", 0)
                        retweets = tweet_metrics.get("retweet_count", 0)
                        replies = tweet_metrics.get("reply_count", 0)
                        quotes = tweet_metrics.get("quote_count", 0)

                        # Calculate engagement
                        engagement = likes + retweets + replies + quotes

                        if engagement > 5:  # Threshold for high engagement
                            self.logger.info(f"High engagement detected on tweet {tweet_id}: {engagement} (likes: {likes}, RTs: {retweets}, replies: {replies})")

                        # Check for new replies/mentions (would require additional API calls)
                        # This is a simplified version

                # Wait for next check
                await asyncio.sleep(interval)

            except Exception as e:
                self.logger.error(f"Error in Twitter engagement monitoring: {str(e)}")
                await asyncio.sleep(300)  # Wait 5 minutes before retrying


async def test_twitter_manager():
    """Test the Twitter manager"""
    print("Testing Twitter Manager...")

    # Create manager instance
    tw_manager = TwitterManager()

    # Show current configuration status
    print(f"API key configured: {'Yes' if tw_manager.config.get('api_key') else 'No'}")
    print(f"Bearer token configured: {'Yes' if tw_manager.config.get('bearer_token') else 'No'}")
    print(f"Twitter username configured: {'Yes' if tw_manager.config.get('twitter_username') else 'No'}")

    # Show sample post schedule
    print(f"Post schedule: {tw_manager.config.get('post_schedule', {})}")

    # Show default hashtags
    print(f"Default hashtags: {tw_manager.config.get('default_hashtags', [])}")

    # Show auto hashtag generation
    sample_content = "Just implemented a new AI automation system that's boosting our productivity by 300%!"
    hashtags = tw_manager.generate_hashtags(sample_content)
    print(f"Generated hashtags for sample content: {hashtags}")

    # Validate sample tweet
    sample_tweet = "Excited to share our latest innovation in AI-powered automation! This system learns and adapts to optimize workflows automatically. #AI #Automation #Innovation"
    validation = tw_manager.validate_tweet_content(sample_tweet)
    print(f"Tweet validation: {validation}")

    # Get user info (will fail without proper config, but shows the method)
    print("\nAttempting to get user info...")
    user_info = tw_manager.get_user_info()
    if user_info:
        print(f"User info retrieved: {user_info}")
    else:
        print("User info not available (likely due to missing configuration)")

    # Show analytics summary structure
    print("\nAnalytics summary structure:")
    analytics_summary = tw_manager.get_analytics_summary()
    print(json.dumps(analytics_summary, indent=2))

    return True


if __name__ == "__main__":
    asyncio.run(test_twitter_manager())