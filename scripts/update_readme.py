#!/usr/bin/env python3
"""
Fetch latest GitHub repositories and update README.
"""

import os
import re
import requests
from datetime import datetime

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME", "Ayyankhan101")
README_PATH = "README.md"

def fetch_repositories():
    """Fetch latest public repositories from GitHub API."""
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    url = f"https://api.github.com/users/{GITHUB_USERNAME}/repos"
    params = {
        "sort": "updated",
        "direction": "desc",
        "per_page": 10,
        "type": "owner"
    }
    
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    
    repos = response.json()
    
    # Filter out the profile README repo itself
    repos = [r for r in repos if r["name"] != f"{GITHUB_USERNAME}.github.io"]
    
    return repos[:6]  # Return top 6 repos

def format_repo_info(repo):
    """Format repository info for README."""
    name = repo["name"]
    description = repo["description"] or "No description available"
    html_url = repo["html_url"]
    language = repo["language"] or "Unknown"
    stars = repo["stargazers_count"]
    updated_at = datetime.strptime(repo["updated_at"], "%Y-%m-%dT%H:%M:%SZ")
    updated_str = updated_at.strftime("%b %d, %Y")
    
    return {
        "name": name,
        "description": description,
        "url": html_url,
        "language": language,
        "stars": stars,
        "updated": updated_str
    }

def generate_readme_section(repos):
    """Generate Markdown section for latest repositories."""
    lines = [
        "",
        "### 📌 Latest Repositories",
        "",
        "| Repository | Description | Language | ⭐ | Updated |",
        "|------------|-------------|----------|----|---------|"
    ]
    
    for repo in repos:
        desc = repo["description"][:50] + "..." if len(repo["description"]) > 50 else repo["description"]
        lines.append(
            f'| [{repo["name"]}]({repo["url"]}) | {desc} | {repo["language"]} | {repo["stars"]} | {repo["updated"]} |'
        )
    
    lines.append("")
    lines.append(f"> 📍 *Last updated: {datetime.now().strftime('%B %d, %Y at %H:%M UTC')}*")
    lines.append("")
    
    return "\n".join(lines)

def update_readme():
    """Update README.md with latest repositories."""
    # Fetch repos
    repos = fetch_repositories()
    formatted_repos = [format_repo_info(r) for r in repos]
    section = generate_readme_section(formatted_repos)
    
    # Read current README
    with open(README_PATH, "r") as f:
        content = f.read()
    
    # Replace content between markers
    pattern = r"(<!-- START_LATEST_REPOS -->).*(<!-- END_LATEST_REPOS -->)"
    replacement = f"\\1{section}\\2"
    
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    # Write updated README
    with open(README_PATH, "w") as f:
        f.write(new_content)
    
    print(f"✅ Updated README with {len(formatted_repos)} repositories")

if __name__ == "__main__":
    update_readme()
