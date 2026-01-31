#!/usr/bin/env python3
"""Test the CEO Briefing Generator"""

import sys
sys.path.insert(0, '.')

from ceo_briefing_generator import CEOBriefingGenerator

def test_generator():
    print("Testing CEO Briefing Generator...")

    generator = CEOBriefingGenerator()
    print("Generator created successfully")

    try:
        briefing_file = generator.generate_weekly_briefing()
        print(f"Weekly briefing generated: {briefing_file}")
    except Exception as e:
        print(f"Error generating briefing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_generator()