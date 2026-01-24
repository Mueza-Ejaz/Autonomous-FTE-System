#!/usr/bin/env python3
"""
Image Optimizer for post-to-social-media Skill

Optimizes images for Facebook and Instagram by resizing, compressing, and
adjusting quality for optimal platform performance.

Requirements:
    pip install Pillow

Supported Formats:
    Input: JPG, JPEG, PNG, WEBP
    Output: JPG (optimized), PNG (if transparency needed)

Platform Specifications:
    Facebook:
        - Recommended: 1200x630px (link posts), 1200x1200px (photo posts)
        - Max size: 2048x2048px
        - Target file size: < 1 MB

    Instagram:
        - Feed Square: 1080x1080px
        - Feed Portrait: 1080x1350px (4:5 ratio)
        - Feed Landscape: 1080x566px (1.91:1 ratio)
        - Max size: 1080px width
        - Target file size: < 1 MB
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from typing import Tuple, Optional

try:
    from PIL import Image, ImageEnhance, ImageOps
except ImportError:
    print("ERROR: Pillow not installed.")
    print("Install with: pip install Pillow")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Platform specifications
PLATFORM_SPECS = {
    'facebook': {
        'photo': (1200, 1200),  # Square photo post
        'link': (1200, 630),    # Link preview
        'max_size': 2048,
        'quality': 85,
        'target_file_size_mb': 1.0
    },
    'instagram': {
        'square': (1080, 1080),     # 1:1 ratio
        'portrait': (1080, 1350),   # 4:5 ratio
        'landscape': (1080, 566),   # 1.91:1 ratio
        'max_size': 1080,
        'quality': 85,
        'target_file_size_mb': 1.0
    }
}

class ImageOptimizer:
    """Image optimization class for social media platforms."""

    def __init__(self, platform: str, format_type: str = 'auto'):
        """
        Initialize Image Optimizer.

        Args:
            platform: 'facebook' or 'instagram'
            format_type: For instagram: 'square', 'portrait', 'landscape', 'auto'
                        For facebook: 'photo', 'link', 'auto'
        """
        self.platform = platform.lower()
        self.format_type = format_type.lower()

        if self.platform not in PLATFORM_SPECS:
            raise ValueError(f"Platform must be 'facebook' or 'instagram', got '{platform}'")

    def detect_best_format(self, width: int, height: int) -> str:
        """
        Detect best format based on image aspect ratio.

        Args:
            width: Image width
            height: Image height

        Returns:
            Best format type for platform
        """
        aspect_ratio = width / height

        if self.platform == 'instagram':
            if 0.95 <= aspect_ratio <= 1.05:
                return 'square'
            elif aspect_ratio < 0.95:
                return 'portrait'
            else:
                return 'landscape'
        else:  # facebook
            if aspect_ratio > 1.5:
                return 'link'
            else:
                return 'photo'

    def calculate_dimensions(self, original_width: int, original_height: int) -> Tuple[int, int, str]:
        """
        Calculate optimal dimensions for platform.

        Args:
            original_width: Original image width
            original_height: Original image height

        Returns:
            Tuple of (target_width, target_height, crop_method)
        """
        # Determine format if auto
        if self.format_type == 'auto':
            format_type = self.detect_best_format(original_width, original_height)
            logger.info(f"Auto-detected format: {format_type}")
        else:
            format_type = self.format_type

        # Get target dimensions
        specs = PLATFORM_SPECS[self.platform]
        target_width, target_height = specs.get(format_type, specs.get('photo', (1200, 1200)))

        # Calculate aspect ratios
        original_ratio = original_width / original_height
        target_ratio = target_width / target_height

        if abs(original_ratio - target_ratio) < 0.05:
            # Aspect ratios are close enough, just resize
            crop_method = 'resize'
        else:
            # Need to crop to match aspect ratio
            crop_method = 'crop_and_resize'

        return target_width, target_height, crop_method

    def optimize_image(self, input_path: Path, output_path: Optional[Path] = None,
                      quality: Optional[int] = None) -> Path:
        """
        Optimize image for platform.

        Args:
            input_path: Path to input image
            output_path: Path to save optimized image (optional)
            quality: JPEG quality (1-100, optional)

        Returns:
            Path to optimized image
        """
        if not input_path.exists():
            raise FileNotFoundError(f"Input image not found: {input_path}")

        # Load image
        logger.info(f"Loading image: {input_path}")
        image = Image.open(input_path)

        # Convert RGBA to RGB if necessary (for JPEG)
        if image.mode in ('RGBA', 'LA', 'P'):
            logger.info(f"Converting {image.mode} to RGB")
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1] if image.mode in ('RGBA', 'LA') else None)
            image = background

        original_width, original_height = image.size
        original_size_mb = input_path.stat().st_size / (1024 * 1024)

        logger.info(f"Original dimensions: {original_width}x{original_height}")
        logger.info(f"Original file size: {original_size_mb:.2f} MB")

        # Calculate target dimensions
        target_width, target_height, crop_method = self.calculate_dimensions(
            original_width, original_height
        )

        logger.info(f"Target dimensions: {target_width}x{target_height}")
        logger.info(f"Processing method: {crop_method}")

        # Apply auto-orientation based on EXIF data
        image = ImageOps.exif_transpose(image)

        # Process image
        if crop_method == 'crop_and_resize':
            # Crop to target aspect ratio, then resize
            image = self._crop_to_aspect_ratio(image, target_width, target_height)
            image = image.resize((target_width, target_height), Image.Resampling.LANCZOS)
        else:
            # Just resize
            image = image.resize((target_width, target_height), Image.Resampling.LANCZOS)

        # Enhance sharpness slightly after resize
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.1)

        # Determine output path
        if output_path is None:
            output_dir = input_path.parent / f"{self.platform}_optimized"
            output_dir.mkdir(exist_ok=True)
            output_filename = f"{input_path.stem}_optimized.jpg"
            output_path = output_dir / output_filename

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Determine quality
        if quality is None:
            quality = PLATFORM_SPECS[self.platform]['quality']

        # Save optimized image
        logger.info(f"Saving optimized image: {output_path}")
        image.save(output_path, 'JPEG', quality=quality, optimize=True)

        # Check file size and re-optimize if needed
        output_size_mb = output_path.stat().st_size / (1024 * 1024)
        target_size_mb = PLATFORM_SPECS[self.platform]['target_file_size_mb']

        logger.info(f"Optimized file size: {output_size_mb:.2f} MB")

        if output_size_mb > target_size_mb:
            logger.warning(f"File size exceeds target ({target_size_mb} MB), reducing quality...")
            reduced_quality = max(quality - 10, 70)
            image.save(output_path, 'JPEG', quality=reduced_quality, optimize=True)
            final_size_mb = output_path.stat().st_size / (1024 * 1024)
            logger.info(f"Reduced to quality {reduced_quality}, new size: {final_size_mb:.2f} MB")

        logger.info(f"✓ Optimization complete: {output_path}")
        return output_path

    def _crop_to_aspect_ratio(self, image: Image.Image, target_width: int, target_height: int) -> Image.Image:
        """
        Crop image to match target aspect ratio (center crop).

        Args:
            image: PIL Image object
            target_width: Target width
            target_height: Target height

        Returns:
            Cropped PIL Image
        """
        original_width, original_height = image.size
        target_ratio = target_width / target_height
        original_ratio = original_width / original_height

        if original_ratio > target_ratio:
            # Image is wider than target, crop width
            new_width = int(original_height * target_ratio)
            left = (original_width - new_width) // 2
            top = 0
            right = left + new_width
            bottom = original_height
        else:
            # Image is taller than target, crop height
            new_height = int(original_width / target_ratio)
            left = 0
            top = (original_height - new_height) // 2
            right = original_width
            bottom = top + new_height

        logger.info(f"Cropping to aspect ratio (center crop)")
        return image.crop((left, top, right, bottom))

    def batch_optimize(self, input_dir: Path, output_dir: Optional[Path] = None,
                      pattern: str = "*.[jJ][pP][gG]") -> list:
        """
        Batch optimize all images in directory.

        Args:
            input_dir: Directory containing images
            output_dir: Directory to save optimized images (optional)
            pattern: Glob pattern for finding images

        Returns:
            List of optimized image paths
        """
        if not input_dir.is_dir():
            raise NotADirectoryError(f"Input directory not found: {input_dir}")

        # Find all matching images
        image_files = list(input_dir.glob(pattern))
        image_files.extend(list(input_dir.glob(pattern.replace('[jJ][pP][gG]', '[pP][nN][gG]'))))

        if not image_files:
            logger.warning(f"No images found matching pattern: {pattern}")
            return []

        logger.info(f"Found {len(image_files)} images to optimize")

        optimized_paths = []
        for image_file in image_files:
            try:
                if output_dir:
                    output_path = output_dir / f"{image_file.stem}_optimized.jpg"
                else:
                    output_path = None

                optimized_path = self.optimize_image(image_file, output_path)
                optimized_paths.append(optimized_path)

            except Exception as e:
                logger.error(f"Failed to optimize {image_file}: {e}")
                continue

        logger.info(f"✓ Batch optimization complete: {len(optimized_paths)}/{len(image_files)} successful")
        return optimized_paths


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description='Optimize images for Facebook or Instagram'
    )
    parser.add_argument(
        '--input',
        type=str,
        required=True,
        help='Path to input image or directory'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Path to output image or directory (optional)'
    )
    parser.add_argument(
        '--platform',
        type=str,
        required=True,
        choices=['facebook', 'instagram', 'fb', 'ig'],
        help='Target platform (facebook/fb or instagram/ig)'
    )
    parser.add_argument(
        '--format',
        type=str,
        default='auto',
        choices=['auto', 'square', 'portrait', 'landscape', 'photo', 'link'],
        help='Image format (auto-detected if not specified)'
    )
    parser.add_argument(
        '--quality',
        type=int,
        default=None,
        help='JPEG quality (1-100, default: 85)'
    )
    parser.add_argument(
        '--batch',
        action='store_true',
        help='Batch process all images in directory'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    # Normalize platform name
    platform = 'facebook' if args.platform in ['facebook', 'fb'] else 'instagram'

    # Initialize optimizer
    optimizer = ImageOptimizer(platform, args.format)

    input_path = Path(args.input)
    output_path = Path(args.output) if args.output else None

    try:
        if args.batch:
            # Batch mode
            if not input_path.is_dir():
                logger.error("--batch requires a directory as input")
                sys.exit(1)

            optimized_paths = optimizer.batch_optimize(input_path, output_path)
            logger.info(f"Optimized {len(optimized_paths)} images")

            # Print paths
            for path in optimized_paths:
                print(path)

        else:
            # Single image mode
            if not input_path.is_file():
                logger.error(f"Input file not found: {input_path}")
                sys.exit(1)

            optimized_path = optimizer.optimize_image(input_path, output_path, args.quality)
            print(optimized_path)

        sys.exit(0)

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
