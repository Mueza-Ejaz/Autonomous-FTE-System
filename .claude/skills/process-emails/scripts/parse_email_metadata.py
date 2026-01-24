#!/usr/bin/env python3
"""
Email Metadata Parser

Extracts structured metadata from EMAIL_*.md files created by Gmail Watcher.
Parses YAML frontmatter and email content for categorization and processing.

Usage:
    python parse_email_metadata.py <email_file.md>
    python parse_email_metadata.py <email_file.md> --json

Author: Autonomous FTE System
Date: 2026-01-11
"""

import sys
import yaml
import json
import re
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime


class EmailMetadataParser:
    """Parser for EMAIL_*.md files with YAML frontmatter."""

    def __init__(self, file_path: str):
        """
        Initialize parser with email file path.

        Args:
            file_path: Path to EMAIL_*.md file
        """
        self.file_path = Path(file_path)
        self.metadata: Dict[str, Any] = {}
        self.body: str = ""
        self.suggested_actions: List[str] = []
        self.additional_metadata: Dict[str, Any] = {}

    def parse(self) -> Dict[str, Any]:
        """
        Parse email file and extract all metadata.

        Returns:
            Dictionary containing parsed metadata and content

        Raises:
            FileNotFoundError: If email file doesn't exist
            ValueError: If file format is invalid
        """
        if not self.file_path.exists():
            raise FileNotFoundError(f"Email file not found: {self.file_path}")

        content = self.file_path.read_text(encoding='utf-8')

        # Extract YAML frontmatter
        self._parse_frontmatter(content)

        # Extract email body
        self._parse_body(content)

        # Extract suggested actions
        self._parse_suggested_actions(content)

        # Extract additional metadata section
        self._parse_additional_metadata(content)

        # Analyze content for urgency indicators
        self._analyze_urgency()

        # Return complete parsed data
        return self._build_result()

    def _parse_frontmatter(self, content: str) -> None:
        """Extract YAML frontmatter from email file."""
        # Match YAML frontmatter pattern
        frontmatter_pattern = r'^---\s*\n(.*?)\n---\s*\n'
        match = re.search(frontmatter_pattern, content, re.DOTALL)

        if not match:
            raise ValueError("No YAML frontmatter found in email file")

        yaml_content = match.group(1)

        try:
            self.metadata = yaml.safe_load(yaml_content)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML frontmatter: {e}")

        # Validate required fields
        required_fields = ['type', 'from', 'subject']
        for field in required_fields:
            if field not in self.metadata:
                raise ValueError(f"Missing required field in frontmatter: {field}")

    def _parse_body(self, content: str) -> None:
        """Extract email body content."""
        # Find "Email Content" section
        body_pattern = r'## Email Content\s*\n(.*?)(?=\n## |$)'
        match = re.search(body_pattern, content, re.DOTALL)

        if match:
            self.body = match.group(1).strip()
        else:
            # Fallback: everything after frontmatter until next section
            after_frontmatter = re.split(r'^---\s*$', content, flags=re.MULTILINE)[2:]
            if after_frontmatter:
                self.body = '\n'.join(after_frontmatter).strip()

    def _parse_suggested_actions(self, content: str) -> None:
        """Extract suggested actions from email file."""
        actions_pattern = r'## Suggested Actions\s*\n(.*?)(?=\n## |$)'
        match = re.search(actions_pattern, content, re.DOTALL)

        if match:
            actions_text = match.group(1)
            # Extract checkbox items
            checkbox_pattern = r'- \[ \] (.+)'
            self.suggested_actions = re.findall(checkbox_pattern, actions_text)

    def _parse_additional_metadata(self, content: str) -> None:
        """Extract additional metadata section if present."""
        metadata_pattern = r'## Metadata\s*\n(.*?)(?=\n## |$)'
        match = re.search(metadata_pattern, content, re.DOTALL)

        if match:
            metadata_text = match.group(1)
            # Parse key-value pairs
            kv_pattern = r'- \*\*(.+?)\*\*:\s*(.+)'
            pairs = re.findall(kv_pattern, metadata_text)
            self.additional_metadata = {key: value for key, value in pairs}

    def _analyze_urgency(self) -> None:
        """Analyze content for urgency indicators."""
        urgent_keywords = [
            'urgent', 'asap', 'immediate', 'emergency', 'critical',
            'time-sensitive', 'deadline today', 'expires today',
            'action required', 'final notice', 'overdue'
        ]

        # Check subject and body
        text_to_check = f"{self.metadata.get('subject', '')} {self.body}".lower()

        found_keywords = [kw for kw in urgent_keywords if kw in text_to_check]

        # Add urgency analysis to metadata
        self.metadata['urgency_keywords_found'] = found_keywords
        self.metadata['urgency_score'] = len(found_keywords)

    def _build_result(self) -> Dict[str, Any]:
        """Build complete result dictionary."""
        return {
            'file_path': str(self.file_path),
            'file_name': self.file_path.name,
            'parsed_at': datetime.now().isoformat(),

            # Core metadata from frontmatter
            'type': self.metadata.get('type'),
            'from': self.metadata.get('from'),
            'from_name': self.metadata.get('from_name', ''),
            'subject': self.metadata.get('subject'),
            'received': self.metadata.get('received'),
            'priority': self.metadata.get('priority', 'normal'),
            'message_id': self.metadata.get('message_id', ''),
            'status': self.metadata.get('status', 'pending'),

            # Content
            'body': self.body,
            'body_length': len(self.body),
            'body_word_count': len(self.body.split()),

            # Suggested actions
            'suggested_actions': self.suggested_actions,
            'suggested_action_count': len(self.suggested_actions),

            # Additional metadata
            'additional_metadata': self.additional_metadata,

            # Urgency analysis
            'urgency_keywords': self.metadata.get('urgency_keywords_found', []),
            'urgency_score': self.metadata.get('urgency_score', 0),
            'has_urgency_indicators': self.metadata.get('urgency_score', 0) > 0,

            # Parsing metadata
            'raw_metadata': self.metadata,
        }

    def get_sender_email(self) -> str:
        """Extract just the email address from 'from' field."""
        from_field = self.metadata.get('from', '')
        # Handle "Name <email@example.com>" format
        email_match = re.search(r'<(.+?)>', from_field)
        if email_match:
            return email_match.group(1)
        # Handle plain email
        if '@' in from_field:
            return from_field
        return ''

    def get_sender_domain(self) -> str:
        """Extract sender's email domain."""
        email = self.get_sender_email()
        if '@' in email:
            return email.split('@')[1]
        return ''

    def is_automated_sender(self) -> bool:
        """Check if sender appears to be automated."""
        email = self.get_sender_email().lower()
        automated_patterns = [
            'noreply@', 'no-reply@', 'donotreply@', 'do-not-reply@',
            'automated@', 'notifications@', 'newsletter@', 'marketing@'
        ]
        return any(pattern in email for pattern in automated_patterns)

    def extract_keywords(self, custom_keywords: Optional[List[str]] = None) -> List[str]:
        """
        Extract specific keywords from email content.

        Args:
            custom_keywords: Optional list of keywords to search for

        Returns:
            List of found keywords
        """
        if custom_keywords is None:
            custom_keywords = [
                'invoice', 'payment', 'meeting', 'urgent', 'deadline',
                'project', 'question', 'help', 'issue', 'problem'
            ]

        text = f"{self.metadata.get('subject', '')} {self.body}".lower()
        found = [kw for kw in custom_keywords if kw in text]
        return found


def print_formatted_output(data: Dict[str, Any], use_json: bool = False) -> None:
    """
    Print parsed data in human-readable or JSON format.

    Args:
        data: Parsed email data
        use_json: If True, output JSON; otherwise human-readable
    """
    if use_json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print("=" * 60)
        print("EMAIL METADATA PARSER RESULTS")
        print("=" * 60)
        print(f"\nFile: {data['file_name']}")
        print(f"Parsed at: {data['parsed_at']}")
        print("\n--- EMAIL DETAILS ---")
        print(f"From: {data['from_name']} <{data['from']}>")
        print(f"Subject: {data['subject']}")
        print(f"Received: {data['received']}")
        print(f"Priority: {data['priority']}")
        print(f"Status: {data['status']}")

        print("\n--- CONTENT ANALYSIS ---")
        print(f"Body length: {data['body_length']} characters")
        print(f"Word count: {data['body_word_count']} words")
        print(f"Suggested actions: {data['suggested_action_count']}")

        print("\n--- URGENCY ANALYSIS ---")
        print(f"Urgency score: {data['urgency_score']}")
        print(f"Has urgency indicators: {data['has_urgency_indicators']}")
        if data['urgency_keywords']:
            print(f"Urgency keywords found: {', '.join(data['urgency_keywords'])}")

        if data['suggested_actions']:
            print("\n--- SUGGESTED ACTIONS ---")
            for action in data['suggested_actions']:
                print(f"  - {action}")

        print("\n--- EMAIL BODY (Preview) ---")
        preview = data['body'][:300]
        if len(data['body']) > 300:
            preview += "..."
        print(preview)
        print("\n" + "=" * 60)


def main():
    """Main entry point for command-line usage."""
    if len(sys.argv) < 2:
        print("Usage: python parse_email_metadata.py <email_file.md> [--json]")
        print("\nExample:")
        print("  python parse_email_metadata.py EMAIL_12345.md")
        print("  python parse_email_metadata.py EMAIL_12345.md --json")
        sys.exit(1)

    file_path = sys.argv[1]
    use_json = '--json' in sys.argv

    try:
        parser = EmailMetadataParser(file_path)
        result = parser.parse()

        # Add additional helper methods results
        result['sender_email'] = parser.get_sender_email()
        result['sender_domain'] = parser.get_sender_domain()
        result['is_automated'] = parser.is_automated_sender()
        result['extracted_keywords'] = parser.extract_keywords()

        print_formatted_output(result, use_json)

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error parsing email file: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
