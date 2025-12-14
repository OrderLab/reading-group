#!/usr/bin/env python3
"""
Migration script to convert static HTML semester pages to Jekyll markdown format.
Author: Claude Code

Usage:
    python migrate-semester.py summer25
    python migrate-semester.py --all
"""

import re
import sys
from pathlib import Path
from html.parser import HTMLParser
from typing import List, Dict, Optional


class SemesterHTMLParser(HTMLParser):
    """Parse semester HTML files to extract metadata and sessions."""

    def __init__(self):
        super().__init__()
        self.sessions = []
        self.current_session = {}
        self.in_title_p = False
        self.in_authors_p = False
        self.current_tag = None
        self.td_index = 0
        self.in_tr = False
        self.skip_header = True
        self.semester = None
        self.time = None
        self.coordinator = None

    def handle_starttag(self, tag, attrs):
        self.current_tag = tag
        attrs_dict = dict(attrs)

        if tag == 'tr':
            self.in_tr = True
            self.td_index = 0
            self.current_session = {}
            # Skip header row
            if self.skip_header and 'class' in attrs_dict and 'info' in attrs_dict['class']:
                self.skip_header = False
                self.in_tr = False

        elif tag == 'td' and self.in_tr:
            self.td_index += 1

        elif tag == 'p' and self.in_tr:
            if 'class' in attrs_dict:
                if attrs_dict['class'] == 'title':
                    self.in_title_p = True
                elif attrs_dict['class'] == 'authors':
                    self.in_authors_p = True

        elif tag == 'a' and self.td_index == 5:  # Material column
            if 'href' in attrs_dict:
                self.current_session['link'] = attrs_dict['href']

        elif tag == 'h2' and 'class' in attrs_dict and attrs_dict['class'] == 'semester':
            self.current_tag = 'h2-semester'

        elif tag == 'h3':
            self.current_tag = 'h3-time'

        elif tag == 'h4':
            self.current_tag = 'h4-coordinator'

    def handle_data(self, data):
        data = data.strip()
        if not data:
            return

        if self.current_tag == 'h2-semester':
            self.semester = data
        elif self.current_tag == 'h3-time':
            self.time = data
        elif self.current_tag == 'h4-coordinator':
            # Extract coordinator name from "Coordinator: Name"
            match = re.search(r'Coordinator:\s*(.+)', data)
            if match:
                self.coordinator = match.group(1)

        if not self.in_tr:
            return

        if self.in_title_p:
            self.current_session['title'] = data
        elif self.in_authors_p:
            self.current_session['authors'] = data
        elif self.td_index == 1:  # Date
            self.current_session['date'] = data
        elif self.td_index == 2:  # Presenter
            self.current_session['presenter'] = data
        elif self.td_index == 3:  # Title (fallback for non-<p> titles)
            if 'title' not in self.current_session and data:
                self.current_session['title'] = data
        elif self.td_index == 4:  # Conference
            if data:
                self.current_session['venue'] = data

    def handle_endtag(self, tag):
        if tag == 'tr' and self.in_tr:
            self.in_tr = False
            # Only add sessions with at least a date and presenter
            if 'date' in self.current_session and 'presenter' in self.current_session:
                self.sessions.append(self.current_session)
            self.current_session = {}

        elif tag == 'p':
            self.in_title_p = False
            self.in_authors_p = False


def parse_html_semester(html_path: Path) -> Dict:
    """Parse an HTML semester file and extract all data."""
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    parser = SemesterHTMLParser()
    parser.feed(html_content)

    return {
        'semester': parser.semester,
        'time': parser.time,
        'coordinator': parser.coordinator,
        'sessions': parser.sessions
    }


def generate_yaml_frontmatter(semester_id: str, data: Dict) -> str:
    """Generate YAML front matter for a semester."""

    yaml_lines = [
        "---",
        "layout: semester",
        f"semester_id: {semester_id}",
        f'semester: "{data["semester"]}"',
        f'time: "{data["time"]}"',
        f'coordinator: "{data["coordinator"]}"',
        f"permalink: /{semester_id}/",
        "",
        "sessions:"
    ]

    for session in data['sessions']:
        yaml_lines.append(f'  - date: "{session.get("date", "")}"')
        yaml_lines.append(f'    presenter: "{session.get("presenter", "")}"')
        yaml_lines.append(f'    title: "{session.get("title", "")}"')

        if 'authors' in session and session['authors']:
            yaml_lines.append(f'    authors: "{session["authors"]}"')
        if 'venue' in session and session['venue']:
            yaml_lines.append(f'    venue: "{session["venue"]}"')
        if 'link' in session and session['link']:
            yaml_lines.append(f'    link: "{session["link"]}"')

        yaml_lines.append("")  # Blank line between sessions

    yaml_lines.extend([
        "---",
        "",
        "<!-- This file is automatically processed by Jekyll. The content is defined in the YAML front matter above. -->"
    ])

    return "\n".join(yaml_lines)


def migrate_semester(semester_id: str, base_path: Path):
    """Migrate a single semester from HTML to Jekyll markdown."""

    html_path = base_path / semester_id / "index.html"
    if not html_path.exists():
        print(f"❌ Error: {html_path} not found")
        return False

    print(f"📄 Parsing {semester_id}/index.html...")

    try:
        data = parse_html_semester(html_path)

        if not data['semester']:
            print(f"❌ Error: Could not parse semester metadata from {html_path}")
            return False

        print(f"✅ Found: {data['semester']}")
        print(f"   Time: {data['time']}")
        print(f"   Coordinator: {data['coordinator']}")
        print(f"   Sessions: {len(data['sessions'])}")

        # Generate markdown file
        yaml_content = generate_yaml_frontmatter(semester_id, data)
        md_path = base_path / f"{semester_id}.md"

        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(yaml_content)

        print(f"✅ Created: {md_path.name}")
        return True

    except Exception as e:
        print(f"❌ Error parsing {semester_id}: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python migrate-semester.py <semester_id>")
        print("   or: python migrate-semester.py --all")
        print("")
        print("Examples:")
        print("  python migrate-semester.py summer25")
        print("  python migrate-semester.py --all")
        sys.exit(1)

    base_path = Path(__file__).parent

    # All semesters to migrate (excluding fall25 which is already done)
    all_semesters = [
        'fall17', 'spring18', 'fall18', 'summer18',
        'spring19', 'fall19',
        'spring20', 'fall20',
        'spring21', 'fall21',
        'spring22', 'summer22', 'fall22',
        'fall23',
        'winter24', 'summer24', 'fall24',
        'winter25', 'summer25'
    ]

    if sys.argv[1] == '--all':
        print(f"🚀 Migrating all {len(all_semesters)} semesters...\n")
        success_count = 0

        for semester_id in all_semesters:
            if migrate_semester(semester_id, base_path):
                success_count += 1
            print("")

        print(f"✅ Successfully migrated {success_count}/{len(all_semesters)} semesters")

        if success_count == len(all_semesters):
            print("\n📝 Next steps:")
            print("1. Review the generated .md files")
            print("2. Update _config.yml if needed")
            print("3. Test with: bundle exec jekyll build")
            print("4. Commit and push to GitHub")
    else:
        semester_id = sys.argv[1]
        migrate_semester(semester_id, base_path)


if __name__ == '__main__':
    main()
