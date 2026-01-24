#!/usr/bin/env python3
"""
Instagram API Helper for post-to-social-media Skill

Publishes approved posts to Instagram Business Accounts via Facebook Graph API.
Supports single image posts, carousel posts, and dry-run mode for testing.

Requirements:
    pip install requests python-dotenv pyyaml

Setup:
    1. Convert Instagram account to Business Account
    2. Link Instagram Business to Facebook Page
    3. Create Facebook App: https://developers.facebook.com/apps/
    4. Add Instagram Graph API product
    5. Generate User Access Token with instagram_basic, instagram_content_publish permissions
    6. Get Instagram Business Account ID
    7. Store credentials in .env file

Environment Variables Required:
    IG_ACCESS_TOKEN=your_instagram_access_token
    IG_BUSINESS_ACCOUNT_ID=your_instagram_business_account_id
"""

import os
import sys
import argparse
import json
import logging
import time
from pathlib import Path
from typing import Dict, Optional, Tuple, List
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

# Instagram Graph API configuration
GRAPH_API_VERSION = "v18.0"
GRAPH_API_BASE = f"https://graph.facebook.com/{GRAPH_API_VERSION}"

class InstagramAPIHelper:
    """Helper class for Instagram Graph API operations."""

    def __init__(self, access_token: str, business_account_id: str):
        """
        Initialize Instagram API Helper.

        Args:
            access_token: Instagram Access Token
            business_account_id: Instagram Business Account ID
        """
        self.access_token = access_token
        self.business_account_id = business_account_id
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

            # Extract Instagram post content from body
            ig_content = None
            lines = body.split('\n')
            capture = False
            ig_lines = []

            for line in lines:
                if '### Instagram Post Content' in line:
                    capture = True
                    continue
                elif capture and line.startswith('###'):
                    break
                elif capture and line.startswith('**Metadata:**'):
                    break
                elif capture:
                    ig_lines.append(line)

            if ig_lines:
                ig_content = '\n'.join(ig_lines).strip()

            if not ig_content:
                raise ValueError("No Instagram post content found in approval file")

            # Extract image path if mentioned
            image_paths = []
            if 'Image Path:' in body:
                for line in lines:
                    if 'Image Path:' in line:
                        # Extract path after "Image Path:"
                        path_str = line.split('Image Path:', 1)[1].strip()
                        if path_str and path_str.lower() not in ['required', 'optional', 'pending']:
                            # Check if multiple paths (comma-separated for carousel)
                            if ',' in path_str:
                                paths = [Path(p.strip()) for p in path_str.split(',')]
                                image_paths.extend(paths)
                            else:
                                image_paths.append(Path(path_str))
                        break

            return {
                'content': ig_content,
                'image_paths': image_paths,
                'metadata': frontmatter,
                'platform': frontmatter.get('platform', 'instagram')
            }

        except Exception as e:
            logger.error(f"Failed to parse approval file: {e}")
            raise

    def create_media_container(self, image_url: str, caption: Optional[str] = None, is_carousel_item: bool = False) -> Optional[str]:
        """
        Create media container for single image.

        Args:
            image_url: Publicly accessible image URL
            caption: Post caption (only for single posts, not carousel items)
            is_carousel_item: True if this is part of a carousel

        Returns:
            Container ID or None if failed
        """
        try:
            endpoint = f"{GRAPH_API_BASE}/{self.business_account_id}/media"

            params = {
                'access_token': self.access_token,
                'image_url': image_url
            }

            if caption and not is_carousel_item:
                params['caption'] = caption

            if is_carousel_item:
                params['is_carousel_item'] = 'true'

            response = self.session.post(endpoint, data=params)
            response.raise_for_status()

            result = response.json()
            container_id = result.get('id')

            if container_id:
                logger.info(f"Media container created: {container_id}")
                return container_id
            else:
                logger.error("No container ID returned")
                return None

        except Exception as e:
            logger.error(f"Failed to create media container: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response: {e.response.text}")
            return None

    def create_carousel_container(self, child_container_ids: List[str], caption: str) -> Optional[str]:
        """
        Create carousel container from child containers.

        Args:
            child_container_ids: List of media container IDs
            caption: Carousel caption

        Returns:
            Carousel container ID or None if failed
        """
        try:
            endpoint = f"{GRAPH_API_BASE}/{self.business_account_id}/media"

            params = {
                'access_token': self.access_token,
                'media_type': 'CAROUSEL',
                'caption': caption,
                'children': ','.join(child_container_ids)
            }

            response = self.session.post(endpoint, data=params)
            response.raise_for_status()

            result = response.json()
            container_id = result.get('id')

            if container_id:
                logger.info(f"Carousel container created: {container_id}")
                return container_id
            else:
                logger.error("No carousel container ID returned")
                return None

        except Exception as e:
            logger.error(f"Failed to create carousel container: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response: {e.response.text}")
            return None

    def publish_container(self, container_id: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Publish media container to Instagram.

        Args:
            container_id: Media container ID to publish

        Returns:
            Tuple of (success: bool, media_id: str, permalink: str)
        """
        try:
            endpoint = f"{GRAPH_API_BASE}/{self.business_account_id}/media_publish"

            params = {
                'access_token': self.access_token,
                'creation_id': container_id
            }

            response = self.session.post(endpoint, data=params)
            response.raise_for_status()

            result = response.json()
            media_id = result.get('id')

            if media_id:
                # Get permalink
                permalink = self._get_media_permalink(media_id)
                logger.info(f"Post published successfully: {permalink}")
                return True, media_id, permalink
            else:
                logger.error("No media ID returned")
                return False, None, None

        except Exception as e:
            logger.error(f"Failed to publish container: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response: {e.response.text}")
            return False, None, None

    def _get_media_permalink(self, media_id: str) -> Optional[str]:
        """
        Get permalink for published media.

        Args:
            media_id: Published media ID

        Returns:
            Permalink URL or None
        """
        try:
            endpoint = f"{GRAPH_API_BASE}/{media_id}"

            params = {
                'access_token': self.access_token,
                'fields': 'permalink'
            }

            response = self.session.get(endpoint, params=params)
            response.raise_for_status()

            result = response.json()
            return result.get('permalink')

        except Exception as e:
            logger.warning(f"Could not retrieve permalink: {e}")
            return None

    def publish_single_post(self, image_url: str, caption: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Publish single image post to Instagram.

        Args:
            image_url: Publicly accessible image URL
            caption: Post caption

        Returns:
            Tuple of (success: bool, media_id: str, permalink: str)
        """
        logger.info("Creating single image post...")

        # Step 1: Create media container
        container_id = self.create_media_container(image_url, caption)
        if not container_id:
            return False, None, None

        # Step 2: Wait briefly for processing
        time.sleep(2)

        # Step 3: Publish container
        return self.publish_container(container_id)

    def publish_carousel_post(self, image_urls: List[str], caption: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Publish carousel post to Instagram.

        Args:
            image_urls: List of publicly accessible image URLs (2-10)
            caption: Carousel caption

        Returns:
            Tuple of (success: bool, media_id: str, permalink: str)
        """
        if len(image_urls) < 2 or len(image_urls) > 10:
            logger.error("Carousel requires 2-10 images")
            return False, None, None

        logger.info(f"Creating carousel post with {len(image_urls)} images...")

        # Step 1: Create child containers
        child_container_ids = []
        for i, image_url in enumerate(image_urls):
            logger.info(f"Creating container {i+1}/{len(image_urls)}...")
            container_id = self.create_media_container(image_url, is_carousel_item=True)
            if not container_id:
                logger.error(f"Failed to create container for image {i+1}")
                return False, None, None
            child_container_ids.append(container_id)
            time.sleep(1)  # Brief delay between containers

        # Step 2: Create carousel container
        carousel_container_id = self.create_carousel_container(child_container_ids, caption)
        if not carousel_container_id:
            return False, None, None

        # Step 3: Wait for processing
        time.sleep(3)

        # Step 4: Publish carousel
        return self.publish_container(carousel_container_id)

    def dry_run(self, caption: str, image_paths: List[Path]):
        """
        Simulate posting without actually publishing.

        Args:
            caption: Post caption
            image_paths: List of image paths
        """
        logger.info("=" * 60)
        logger.info("DRY RUN MODE - No actual posting will occur")
        logger.info("=" * 60)
        logger.info(f"\nBusiness Account ID: {self.business_account_id}")

        if len(image_paths) > 1:
            logger.info(f"\nPost Type: Carousel ({len(image_paths)} images)")
        elif len(image_paths) == 1:
            logger.info("\nPost Type: Single Image")
        else:
            logger.error("\nERROR: No images provided (Instagram requires images)")

        logger.info(f"\nCaption:\n{caption}")
        logger.info(f"\nCaption Length: {len(caption)} characters (limit: 2,200)")

        for i, img_path in enumerate(image_paths, 1):
            if img_path.exists():
                size_mb = img_path.stat().st_size / (1024 * 1024)
                logger.info(f"\nImage {i}: {img_path}")
                logger.info(f"Size: {size_mb:.2f} MB")
            else:
                logger.warning(f"\nImage {i} not found: {img_path}")

        logger.info("\n" + "=" * 60)
        logger.info("Dry run complete. To publish, remove --dry-run flag.")
        logger.info("=" * 60)


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description='Publish approved posts to Instagram Business Account'
    )
    parser.add_argument(
        '--approval-file',
        type=str,
        required=True,
        help='Path to approval request markdown file'
    )
    parser.add_argument(
        '--image-url',
        type=str,
        help='Publicly accessible image URL (alternative to approval file image paths)'
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
    access_token = os.getenv('IG_ACCESS_TOKEN')
    business_account_id = os.getenv('IG_BUSINESS_ACCOUNT_ID')

    if not access_token or not business_account_id:
        logger.error("Missing Instagram credentials in environment variables")
        logger.error("Required: IG_ACCESS_TOKEN, IG_BUSINESS_ACCOUNT_ID")
        logger.error("Add them to your .env file or export as environment variables")
        sys.exit(1)

    # Parse approval file
    approval_file = Path(args.approval_file)
    if not approval_file.exists():
        logger.error(f"Approval file not found: {approval_file}")
        sys.exit(1)

    logger.info(f"Processing approval file: {approval_file}")

    try:
        ig_helper = InstagramAPIHelper(access_token, business_account_id)
        post_data = ig_helper.parse_approval_file(approval_file)

        caption = post_data['content']
        image_paths = post_data['image_paths']

        logger.info(f"Parsed caption ({len(caption)} characters)")
        logger.info(f"Images found: {len(image_paths)}")

        if not image_paths:
            logger.error("No images found. Instagram requires at least one image.")
            logger.error("Ensure approval file specifies image path(s).")
            sys.exit(1)

        if args.dry_run:
            # Dry run mode
            ig_helper.dry_run(caption, image_paths)
        else:
            # Actual posting
            logger.info("IMPORTANT: Instagram API requires images to be publicly accessible URLs.")
            logger.info("Local file paths must be uploaded to a web server first.")
            logger.info("You need to implement image hosting (e.g., upload to your website, AWS S3, etc.)")
            logger.error("This script currently requires manual image URL input.")
            logger.error("Use --image-url parameter with publicly accessible image URL.")

            # Note: In production, you would:
            # 1. Upload images from image_paths to a web-accessible location
            # 2. Get the public URLs
            # 3. Use those URLs to create Instagram posts
            #
            # For now, we'll show an example if user provides --image-url

            if args.image_url:
                logger.info(f"Using provided image URL: {args.image_url}")
                success, media_id, permalink = ig_helper.publish_single_post(args.image_url, caption)

                if success:
                    logger.info(f"✓ Post published successfully!")
                    logger.info(f"Media ID: {media_id}")
                    logger.info(f"Permalink: {permalink}")

                    # Log success
                    log_file = Path(__file__).parent.parent.parent.parent / 'Vault' / 'Logs' / 'actions' / f"instagram_post_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    log_file.parent.mkdir(parents=True, exist_ok=True)

                    with open(log_file, 'w') as f:
                        json.dump({
                            'timestamp': datetime.now().isoformat(),
                            'platform': 'instagram',
                            'action': 'post_published',
                            'media_id': media_id,
                            'permalink': permalink,
                            'approval_file': str(approval_file),
                            'status': 'success'
                        }, f, indent=2)

                    sys.exit(0)
                else:
                    logger.error("✗ Failed to publish post")
                    sys.exit(1)
            else:
                logger.error("Missing --image-url parameter for actual posting.")
                logger.error("Run with --dry-run to test approval file parsing.")
                sys.exit(1)

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
