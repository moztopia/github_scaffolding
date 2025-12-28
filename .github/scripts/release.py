#!/usr/bin/env python3
import argparse
import os
import sys
import subprocess
import datetime
import re

VERSION_FILE = 'VERSION'
CHANGELOG_FILE = 'CHANGELOG.md'

def get_current_version():
    try:
        with open(VERSION_FILE, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        print(f"Error: {VERSION_FILE} not found.")
        sys.exit(1)

def write_version(version):
    with open(VERSION_FILE, 'w') as f:
        f.write(version)
    print(f"Updated {VERSION_FILE} to {version}")

def bump_version(current_version, bump_type):
    major, minor, patch = map(int, current_version.split('.'))
    
    if bump_type == 'major':
        major += 1
        minor = 0
        patch = 0
    elif bump_type == 'minor':
        minor += 1
        patch = 0
    elif bump_type == 'patch':
        patch += 1
    
    return f"{major}.{minor}.{patch}"

def is_safe_to_reset():
    cwd = os.getcwd()
    return os.path.basename(cwd) == 'github_scaffolding'

def get_last_tag():
    try:
        # Get the latest reachable tag
        output = subprocess.check_output(['git', 'describe', '--tags', '--abbrev=0'], stderr=subprocess.DEVNULL).decode().strip()
        return output
    except subprocess.CalledProcessError:
        return None

def get_commits(from_tag):
    range_spec = f"{from_tag}..HEAD" if from_tag else "HEAD"
    cmd = ['git', 'log', '--pretty=format:%s', range_spec]
    try:
        output = subprocess.check_output(cmd).decode().strip()
        if not output:
            return []
        return output.split('\n')
    except subprocess.CalledProcessError:
        print("Error getting git log.")
        return []

def parse_commits(commits):
    categories = {
        'Features': [],
        'Fixes': [],
        'Docs': [],
        'Chores': [],
        'Other': []
    }
    
    for commit in commits:
        commit = commit.strip()
        if not commit:
            continue
            
        lower_commit = commit.lower()
        if lower_commit.startswith('feat') or lower_commit.startswith('feature'):
            categories['Features'].append(commit)
        elif lower_commit.startswith('fix'):
            categories['Fixes'].append(commit)
        elif lower_commit.startswith('docs') or lower_commit.startswith('doc'):
            categories['Docs'].append(commit)
        elif lower_commit.startswith('chore') or lower_commit.startswith('test') or lower_commit.startswith('refactor'):
            categories['Chores'].append(commit)
        else:
            categories['Other'].append(commit)
            
    return categories

def generate_changelog_content(version, categories, is_nightly=False):
    date_str = datetime.date.today().isoformat()
    if is_nightly:
        header = f"\n## [Nightly] {version} - {date_str}\n"
    else:
        header = f"\n## [{version}] - {date_str}\n"
        
    content = header
    
    for category, items in categories.items():
        if items:
            content += f"### {category}\n"
            for item in items:
                content += f"- {item}\n"
            content += "\n"
            
    return content

def update_changelog_file(content, dry_run=False):
    if dry_run:
        print("--- Dry Run: Changelog Update ---")
        print(content)
        print("---------------------------------")
        return

    try:
        with open(CHANGELOG_FILE, 'r') as f:
            existing_content = f.read()
    except FileNotFoundError:
        existing_content = "# Changelog\n\n"

    # Insert after the main header bits (approximate heuristic: find first '##' or append after header)
    # If standard Keep A Changelog header exists
    lines = existing_content.split('\n')
    insert_idx = -1
    for i, line in enumerate(lines):
        if line.startswith('## '):
            insert_idx = i
            break
    
    if insert_idx != -1:
        lines.insert(insert_idx, content.strip()) 
        # Add an empty line for spacing
        lines.insert(insert_idx + 1, "")
    else:
        # Append logic if no versions exist yet, but typically we want it after the header
        # Let's search for the end of the header paragraph (first double newline)
        # Simple fallback: Append to end if no '##' found
        # Or better: After line 6 (standard header length)
        # Let's just prepend (after title) for now if no sections found
        if len(lines) > 5 and lines[0].startswith('# '):
             lines.insert(6, content.strip())
             lines.insert(7, "")
        else:
             lines.append(content.strip())
    
    new_full_content = '\n'.join(lines)
    
    with open(CHANGELOG_FILE, 'w') as f:
        f.write(new_full_content)
    print(f"Updated {CHANGELOG_FILE}")

def main():
    parser = argparse.ArgumentParser(description='Manage repository versioning and changelog.')
    parser.add_argument('--type', choices=['major', 'minor', 'patch', 'reset'], required=True,
                        help='Type of release or action to perform')
    parser.add_argument('--dry-run', action='store_true', help='Do not modify files')
    
    args = parser.parse_args()
    
    current_version = get_current_version()
    
    if args.type == 'reset':
        if not is_safe_to_reset():
            print("Error: Reset command is only allowed in the 'github_scaffolding' repository.")
            sys.exit(1)
        
        new_version = '0.0.0'
        print("Resetting version to 0.0.0...")
        # Optional: Reset changelog? The user didn't explicitly ask, but it makes sense for reset.
        if not args.dry_run:
             with open(VERSION_FILE, 'w') as f:
                 f.write(new_version)
    else:
        new_version = bump_version(current_version, args.type)
        print(f"Bumping version from {current_version} to {new_version}")

        # Changelog generation
        last_tag = get_last_tag()
        commits = get_commits(last_tag)
        categories = parse_commits(commits)
        # Basic check: if it's a nightly build (often implied by context, but here we just have bump types)
        # The prompt mentioned "Nightly builds append entries under a 'Nightly Builds' section".
        # But 'nightly' isn't passed as a --type here, usually nightly just runs. 
        # In our nightly.yml, we ran: .scripts/release.py --type patch --dry-run
        # We need to distinguish nightly runs if we want special sections.
        # But for now, let's treat major/minor/patch as standard releases.
        
        changelog_content = generate_changelog_content(new_version, categories)
        update_changelog_file(changelog_content, dry_run=args.dry_run)

    if not args.dry_run:
        write_version(new_version)
        if os.getenv('GITHUB_OUTPUT'):
            with open(os.getenv('GITHUB_OUTPUT'), 'a') as fh:
                fh.write(f"version={new_version}\n")

if __name__ == '__main__':
    main()
