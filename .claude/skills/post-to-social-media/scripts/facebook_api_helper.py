#!/usr/bin/env python3
"""
Facebook API Helper for post-to-social-media Skill

Publishes approved posts to Facebook Business Pages via Facebook Graph API.
Supports text posts, image posts, and dry-run mode for testing.

Requirements:
    pip install requests python-dotenv pyyaml

Setup:
    1. Create Facebook App: https://developers.facebook.com/apps/
    2. Add Facebook Login and Pages API products
    3. Generate User Access Token with pages_manage_posts permission
    4. Get Page Access Token and Page ID
    5. Store credentials in .env file

Environment Variables Required:
    FB_PAGE_ACCESS_TOKEN=your_page_access_token
    FB_PAGE_ID=your_page_id
"""

import os
import sys
import argparse
import json
import logging
from pathlib import Path
from typing import Dict, Optional, Tuple
from datetime import datetime

try:
    import requests
    import yaml
    from dotenv import load_dotenv
except ImportError:
    print("ERROR: Required packages not installed.")
    print("Install with: pip install requests python-dotenv pyyaml")
    sys.exit(1)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Facebook Graph API configuration
GRAPH_API_VERSION = "v18.0"
GRAPH_API_BASE = f"https://graph.facebook.com/{GRAPH_API_VERSION}"

class FacebookAPIHelper:
    """Helper class for Facebook Graph API operations."""

    def __init__(self, page_access_token: str, page_id: str):
        """
        Initialize Facebook API Helper.

        Args:
            page_access_token: Facebook Page Access Token
            page_id: Facebook Page ID
        """
        self.page_access_token = page_access_token
        self.page_id = page_id
        self.session = requests.Session()

    def parse_approval_file(self, file_path: Path) -> Dict:
        """
        Parse approval request markdown file.

        Args:
            file_path: Path to approval file

        Returns:
            Dict containing post content and metadata
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Split frontmatter and body
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    frontmatter = yaml.safe_load(parts[1])
                    body = parts[2].strip()
                else:
                    raise ValueError("Invalid frontmatter format")
            else:
                raise ValueError("No frontmatter found in approval file")

            # Extract Facebook post content from body
            fb_content = None
            lines = body.split('\n')
            capture = False
            fb_lines = []

            for line in lines:
                if '### Facebook Post Content' in line:
                    capture = True
                    continue
                elif capture and line.startswith('###'):
                    break
                elif capture and line.startswith('**Metadata:**'):
                    break
                elif capture:
                    fb_lines.append(line)

            if fb_lines:
                fb_content = '\n'.join(fb_lines).strip()

            if not fb_content:
                raise ValueError("No Facebook post content found in approval file")

            # Extract image path if mentioned
            image_path = None
            if 'Image Path:' in body:
                for line in lines:
                    if 'Image Path:' in line:
                        # Extract path after "Image Path:"
                        path_str = line.split('Image Path:', 1)[1].strip()
                        if path_str and path_str.lower() not in ['required', 'optional', 'pending']:
                            image_path = Path(path_str)
                        break

            return {
                'content': fb_content,
                'image_path': image_path,
                'metadata': frontmatter,
                'platform': frontmatter.get('platform', 'facebook')
            }

        except Exception as e:
            logger.error(f"Failed to parse approval file: {e}")
            raise

    def publish_post(self, content: str, image_path: Optional[Path] = None) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Publish post to Facebook Page.

        Args:
            content: Post text content
            image_path: Optional path to image file

        Returns:
            Tuple of (success: bool, post_id: str, post_url: str)
        """
        try:
            endpoint = f"{GRAPH_API_BASE}/{self.page_id}/feed"

            params = {
                'access_token': self.page_access_token,
                'message': content
            }

            # If image provided, upload via photos endpoint instead
            if image_path and image_path.exists():
                logger.info(f"Uploading image: {image_path}")
                return self._publish_photo_post(content, image_path)

            # Text-only post
            response = self.session.post(endpoint, data=params)
            response.raise_for_status()

            result = response.json()
            post_id = result.get('id')

            if post_id:
                # Construct post URL
                post_url = f"https://www.facebook.com/{post_id}"
                logger.info(f"Post published successfully: {post_url}")
                return True, post_id, post_url
            else:
                logger.error("No post ID returned from Facebook API")
                return False, None, None

        except requests.exceptions.RequestException as e:
            logger.error(f"Facebook API request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response: {e.response.text}")
            return False, None, None
        except Exception as e:
            logger.error(f"Unexpected error publishing post: {e}")
            return False, None, None

    def _publish_photo_post(self, content: str, image_path: Path) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Publish photo post to Facebook Page.

        Args:
            content: Post caption
            image_path: Path to image file

        Returns:
            Tuple of (success: bool, post_id: str, post_url: str)
        """
        try:
            endpoint = f"{GRAPH_API_BASE}/{self.page_id}/photos"

            with open(image_path, 'rb') as image_file:
                files = {'source': image_file}
                data = {
                    'access_token': self.page_access_token,
                    'message': content
                }

                response = self.session.post(endpoint, data=data, files=files)
                response.raise_for_status()

            result = response.json()
            photo_id = result.get('id')
            post_id = result.get('post_id')

            if photo_id:
                # Construct post URL
                post_url = f"https://www.facebook.com/{post_id if post_id else photo_id}"
                logger.info(f"Photo post published successfully: {post_url}")
                return True, photo_id, post_url
            else:
                logger.error("No photo ID returned from Facebook API")
                return False, None, None

        except Exception as e:
            logger.error(f"Failed to publish photo post: {e}")
            return False, None, None

    def dry_run(self, content: str, image_path: Optional[Path] = None):
        """
        Simulate posting without actually publishing.

        Args:
            content: Post text content
            image_path: Optional path to image file
        """
        logger.info("=" * 60)
        logger.info("DRY RUN MODE - No actual posting will occur")
        logger.info("=" * 60)
        logger.info(f"\nPage ID: {self.page_id}")
        logger.info(f"\nPost Content:\n{content}")
        logger.info(f"\nCharacter Count: {len(content)}")

        if image_path:
            if image_path.exists():
                size_mb = image_path.stat().st_size / (1024 * 1024)
                logger.info(f"\nImage: {image_path}")
                logger.info(f"Image Size: {size_mb:.2f} MB")
            else:
                logger.warning(f"\nImage not found: {image_path}")
        else:
            logger.info("\nPost Type: Text-only")

        logger.info("\n" + "=" * 60)
        logger.info("Dry run complete. To publish, remove --dry-run flag.")
        logger.info("=" * 60)


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description='Publish approved posts to Facebook Business Page'
    )
    parser.add_argument(
        '--approval-file',
        type=str,
        required=True,
        help='Path to approval request markdown file'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Simulate posting without actually publishing'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    # Load credentials from environment
    page_access_token = os.getenv('FB_PAGE_ACCESS_TOKEN')
    page_id = os.getenv('FB_PAGE_ID')

    if not page_access_token or not page_id:
        logger.error("Missing Facebook credentials in environment variables")
        logger.error("Required: FB_PAGE_ACCESS_TOKEN, FB_PAGE_ID")
        logger.error("Add them to your .env file or export as environment variables")
        sys.exit(1)

    # Parse approval file
    approval_file = Path(args.approval_file)
    if not approval_file.exists():
        logger.error(f"Approval file not found: {approval_file}")
        sys.exit(1)

    logger.info(f"Processing approval file: {approval_file}")

    try:
        fb_helper = FacebookAPIHelper(page_access_token, page_id)
        post_data = fb_helper.parse_approval_file(approval_file)

        content = post_data['content']
        image_path = post_data['image_path']

        logger.info(f"Parsed post content ({len(content)} characters)")
        if image_path:
            logger.info(f"Image specified: {image_path}")

        if args.dry_run:
            # Dry run mode
            fb_helper.dry_run(content, image_path)
        else:
            # Actual posting
            logger.info("Publishing to Facebook...")
            success, post_id, post_url = fb_helper.publish_post(content, image_path)

            if success:
                logger.info(f"✓ Post published successfully!")
                logger.info(f"Post ID: {post_id}")
                logger.info(f"Post URL: {post_url}")

                # Log success to file for Dashboard update
                log_file = Path(__file__).parent.parent.parent.parent / 'Vault' / 'Logs' / 'actions' / f"facebook_post_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                log_file.parent.mkdir(parents=True, exist_ok=True)

                with open(log_file, 'w') as f:
                    json.dump({
                        'timestamp': datetime.now().isoformat(),
                        'platform': 'facebook',
                        'action': 'post_published',
                        'post_id': post_id,
                        'post_url': post_url,
                        'approval_file': str(approval_file),
                        'status': 'success'
                    }, f, indent=2)

                sys.exit(0)
            else:
                logger.error("✗ Failed to publish post")
                sys.exit(1)

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
