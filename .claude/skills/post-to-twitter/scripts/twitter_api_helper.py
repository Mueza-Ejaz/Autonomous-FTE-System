#!/usr/bin/env python3
"""
Twitter API Helper Script
========================

Publishes tweets and threads to Twitter/X using Twitter API v2.

Features:
- Single tweet publishing
- Multi-tweet thread publishing
- Dry-run mode (preview without posting)
- Approval file parsing
- Character count validation
- Rate limit handling
- Error logging

Dependencies:
    pip install tweepy python-dotenv

Environment Variables (.env):
    TWITTER_API_KEY=your_api_key
    TWITTER_API_SECRET=your_api_secret
    TWITTER_ACCESS_TOKEN=your_access_token
    TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret
    TWITTER_BEARER_TOKEN=your_bearer_token  # Optional, for v2 endpoints

Usage:
    # Publish from approval file
    python twitter_api_helper.py --approval-file "path/to/APPROVAL_TWITTER_xxx.md"

    # Dry run (preview without posting)
    python twitter_api_helper.py --dry-run --approval-file "path/to/file.md"

    # Post single tweet directly
    python twitter_api_helper.py --tweet "Your tweet content here"

    # Test authentication
    python twitter_api_helper.py --test-auth

Author: Claude Sonnet 4.5
Created: 2026-01-11
Version: 1.0
"""

import os
import sys
import argparse
import json
import time
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

try:
    import tweepy
    from dotenv import load_dotenv
except ImportError as e:
    print(f"Error: Missing required package: {e}")
    print("\nInstall with: pip install tweepy python-dotenv")
    sys.exit(1)


class TwitterAPIHelper:
    """Helper class for Twitter API v2 operations."""

    def __init__(self, dry_run: bool = False):
        """
        Initialize Twitter API client.

        Args:
            dry_run: If True, preview actions without posting to Twitter
        """
        self.dry_run = dry_run
        self.client = None
        self.api = None  # v1.1 API for some operations

        # Load environment variables
        load_dotenv()

        if not dry_run:
            self._authenticate()

    def _authenticate(self):
        """Authenticate with Twitter API v2 and v1.1."""
        try:
            # Get credentials from environment
            api_key = os.getenv('TWITTER_API_KEY')
            api_secret = os.getenv('TWITTER_API_SECRET')
            access_token = os.getenv('TWITTER_ACCESS_TOKEN')
            access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
            bearer_token = os.getenv('TWITTER_BEARER_TOKEN')

            if not all([api_key, api_secret, access_token, access_token_secret]):
                raise ValueError("Missing required Twitter API credentials in .env file")

            # Twitter API v2 client (for tweets)
            self.client = tweepy.Client(
                bearer_token=bearer_token,
                consumer_key=api_key,
                consumer_secret=api_secret,
                access_token=access_token,
                access_token_secret=access_token_secret
            )

            # Twitter API v1.1 (for some operations)
            auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_token_secret)
            self.api = tweepy.API(auth)

            # Test authentication
            me = self.client.get_me()
            print(f"✓ Authenticated as @{me.data.username}")

        except Exception as e:
            raise Exception(f"Authentication failed: {e}")

    def test_authentication(self) -> bool:
        """
        Test Twitter API authentication.

        Returns:
            True if authentication successful, False otherwise
        """
        try:
            self._authenticate()
            me = self.client.get_me()
            print(f"\n✓ Twitter API Authentication Successful")
            print(f"  Username: @{me.data.username}")
            print(f"  User ID: {me.data.id}")
            print(f"  Name: {me.data.name}")
            return True
        except Exception as e:
            print(f"\n✗ Authentication Failed: {e}")
            return False

    def validate_tweet(self, text: str) -> Tuple[bool, str]:
        """
        Validate tweet content.

        Args:
            text: Tweet text to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        char_count = len(text)

        if char_count == 0:
            return False, "Tweet is empty"

        if char_count > 280:
            return False, f"Tweet exceeds 280 characters ({char_count})"

        return True, ""

    def post_tweet(self, text: str, reply_to_id: Optional[str] = None) -> Optional[Dict]:
        """
        Post a single tweet.

        Args:
            text: Tweet content
            reply_to_id: Optional tweet ID to reply to (for threads)

        Returns:
            Tweet data dict if successful, None otherwise
        """
        # Validate
        is_valid, error = self.validate_tweet(text)
        if not is_valid:
            raise ValueError(f"Invalid tweet: {error}")

        if self.dry_run:
            print(f"\n[DRY RUN] Would post tweet:")
            print(f"  Text: {text}")
            print(f"  Characters: {len(text)}/280")
            if reply_to_id:
                print(f"  Reply to: {reply_to_id}")
            return {
                'id': 'DRY_RUN_ID',
                'text': text,
                'dry_run': True
            }

        try:
            # Post tweet
            kwargs = {'text': text}
            if reply_to_id:
                kwargs['in_reply_to_tweet_id'] = reply_to_id

            response = self.client.create_tweet(**kwargs)

            tweet_id = response.data['id']
            tweet_url = f"https://twitter.com/i/web/status/{tweet_id}"

            print(f"\n✓ Tweet posted successfully")
            print(f"  Tweet ID: {tweet_id}")
            print(f"  URL: {tweet_url}")
            print(f"  Characters: {len(text)}/280")

            return {
                'id': tweet_id,
                'url': tweet_url,
                'text': text,
                'characters': len(text)
            }

        except tweepy.TweepyException as e:
            raise Exception(f"Failed to post tweet: {e}")

    def post_thread(self, tweets: List[str], delay_seconds: int = 5) -> List[Dict]:
        """
        Post a multi-tweet thread.

        Args:
            tweets: List of tweet texts (in order)
            delay_seconds: Delay between tweets (seconds)

        Returns:
            List of tweet data dicts
        """
        if not tweets:
            raise ValueError("Thread is empty")

        # Validate all tweets
        for i, tweet in enumerate(tweets, 1):
            is_valid, error = self.validate_tweet(tweet)
            if not is_valid:
                raise ValueError(f"Tweet {i}/{len(tweets)} invalid: {error}")

        print(f"\n{'[DRY RUN] ' if self.dry_run else ''}Posting thread ({len(tweets)} tweets)...")

        results = []
        reply_to_id = None

        for i, tweet_text in enumerate(tweets, 1):
            print(f"\n  Tweet {i}/{len(tweets)}:")

            # Post tweet
            tweet_data = self.post_tweet(tweet_text, reply_to_id=reply_to_id)
            results.append(tweet_data)

            # Set reply_to_id for next tweet (threading)
            reply_to_id = tweet_data['id']

            # Delay between tweets (except after last tweet)
            if i < len(tweets) and not self.dry_run:
                print(f"    Waiting {delay_seconds} seconds...")
                time.sleep(delay_seconds)

        print(f"\n✓ Thread posted successfully ({len(results)} tweets)")
        if not self.dry_run and results:
            print(f"  First tweet URL: {results[0]['url']}")

        return results

    def parse_approval_file(self, file_path: str) -> Dict:
        """
        Parse Twitter approval request file.

        Args:
            file_path: Path to approval file

        Returns:
            Dict with parsed data (content_type, tweets, metadata)
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Approval file not found: {file_path}")

        content = file_path.read_text(encoding='utf-8')

        # Extract frontmatter
        frontmatter_match = re.search(r'^---\s*\n(.*?)\n---', content, re.DOTALL | re.MULTILINE)
        if not frontmatter_match:
            raise ValueError("Invalid approval file format (missing frontmatter)")

        frontmatter = {}
        for line in frontmatter_match.group(1).split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                frontmatter[key.strip()] = value.strip()

        # Validate frontmatter
        if frontmatter.get('platform') != 'twitter':
            raise ValueError("Not a Twitter approval file")

        content_type = frontmatter.get('content_type', 'tweet')  # 'tweet' or 'thread'

        # Extract tweets
        tweets = []

        # Look for tweet content sections
        tweet_pattern = r'\*\*Tweet (\d+)(?:\s*\(.*?\))?:\*\*\s*\n([^\n]+(?:\n(?!\*\*)[^\n]+)*)'
        tweet_matches = re.finditer(tweet_pattern, content, re.MULTILINE)

        for match in tweet_matches:
            tweet_num = int(match.group(1))
            tweet_text = match.group(2).strip()

            # Remove character count if present
            tweet_text = re.sub(r'\s*Character count:.*$', '', tweet_text, flags=re.MULTILINE)

            tweets.append(tweet_text)

        if not tweets:
            # Fallback: try to extract from ## Twitter Content section
            content_section = re.search(r'## Twitter Content\s*\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
            if content_section:
                # Simple extraction: any line that looks like a tweet
                lines = content_section.group(1).strip().split('\n')
                current_tweet = []
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('#') and not line.startswith('*'):
                        current_tweet.append(line)
                    elif current_tweet:
                        tweets.append(' '.join(current_tweet))
                        current_tweet = []

                if current_tweet:
                    tweets.append(' '.join(current_tweet))

        if not tweets:
            raise ValueError("No tweet content found in approval file")

        return {
            'content_type': content_type,
            'tweets': tweets,
            'metadata': frontmatter,
            'file_path': str(file_path)
        }

    def post_from_approval_file(self, file_path: str) -> Dict:
        """
        Parse approval file and post tweet(s).

        Args:
            file_path: Path to approval file

        Returns:
            Dict with results
        """
        print(f"\n{'=' * 60}")
        print(f"Twitter API Helper")
        print(f"{'=' * 60}")
        print(f"Mode: {'DRY RUN (Preview Only)' if self.dry_run else 'LIVE POSTING'}")
        print(f"File: {file_path}")

        # Parse file
        print(f"\nParsing approval file...")
        parsed = self.parse_approval_file(file_path)

        content_type = parsed['content_type']
        tweets = parsed['tweets']

        print(f"  Content Type: {content_type}")
        print(f"  Tweet Count: {len(tweets)}")

        # Post
        if content_type == 'thread' or len(tweets) > 1:
            results = self.post_thread(tweets)
        else:
            result = self.post_tweet(tweets[0])
            results = [result] if result else []

        return {
            'success': True,
            'content_type': content_type,
            'tweet_count': len(results),
            'results': results,
            'dry_run': self.dry_run
        }


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Twitter API Helper - Post tweets and threads',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Post from approval file
  python twitter_api_helper.py --approval-file "Vault/Approved/APPROVAL_TWITTER_xxx.md"

  # Dry run (preview without posting)
  python twitter_api_helper.py --dry-run --approval-file "path/to/file.md"

  # Post single tweet directly
  python twitter_api_helper.py --tweet "Your tweet content here"

  # Test authentication
  python twitter_api_helper.py --test-auth
        """
    )

    parser.add_argument(
        '--approval-file',
        type=str,
        help='Path to approval request file'
    )

    parser.add_argument(
        '--tweet',
        type=str,
        help='Single tweet text to post directly'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview actions without posting to Twitter'
    )

    parser.add_argument(
        '--test-auth',
        action='store_true',
        help='Test Twitter API authentication'
    )

    parser.add_argument(
        '--thread-delay',
        type=int,
        default=5,
        help='Delay between thread tweets (seconds, default: 5)'
    )

    args = parser.parse_args()

    # Validate arguments
    if not any([args.approval_file, args.tweet, args.test_auth]):
        parser.print_help()
        print("\nError: Must specify --approval-file, --tweet, or --test-auth")
        sys.exit(1)

    try:
        helper = TwitterAPIHelper(dry_run=args.dry_run)

        if args.test_auth:
            # Test authentication
            success = helper.test_authentication()
            sys.exit(0 if success else 1)

        elif args.tweet:
            # Post single tweet directly
            result = helper.post_tweet(args.tweet)
            print(f"\n✓ Success")
            sys.exit(0)

        elif args.approval_file:
            # Post from approval file
            result = helper.post_from_approval_file(args.approval_file)

            if result['success']:
                print(f"\n{'=' * 60}")
                print(f"✓ {'DRY RUN COMPLETE' if args.dry_run else 'POSTING COMPLETE'}")
                print(f"{'=' * 60}")
                print(f"  Content Type: {result['content_type']}")
                print(f"  Tweets Posted: {result['tweet_count']}")

                if not args.dry_run:
                    print(f"\nNext Steps:")
                    print(f"  1. Move approval file from /Approved to /Done")
                    print(f"  2. Update Dashboard.md with success log")
                    print(f"  3. Create engagement tracking file")

                sys.exit(0)
            else:
                print(f"\n✗ Posting failed")
                sys.exit(1)

    except FileNotFoundError as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)

    except ValueError as e:
        print(f"\n✗ Validation Error: {e}")
        sys.exit(1)

    except Exception as e:
        print(f"\n✗ Unexpected Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
