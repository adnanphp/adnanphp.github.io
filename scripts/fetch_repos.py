#!/usr/bin/env python3
"""Fetch public repos for adnanphp and save to data/repos.json."""
import json, os, urllib.request, urllib.error
from pathlib import Path

USER = "adnanphp"
URL  = f"https://api.github.com/users/{USER}/repos?per_page=100&sort=updated"
OUT  = Path("data/repos.json")

def headers():
    h = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "adnanphp-site-builder",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h

def fetch(url):
    req = urllib.request.Request(url, headers=headers())
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

def main():
    repos = fetch(URL)

    # Handle pagination (>100 repos)
    page = 2
    while True:
        try:
            more = fetch(URL + f"&page={page}")
            if not more:
                break
            repos.extend(more)
            page += 1
        except urllib.error.HTTPError:
            break

    keep = ["name", "description", "html_url", "homepage",
            "language", "topics", "stargazers_count",
            "forks_count", "updated_at", "pushed_at", "archived"]
    repos = [{k: r.get(k) for k in keep} for r in repos]
    repos.sort(key=lambda r: r["pushed_at"] or "", reverse=True)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(repos, indent=2), encoding="utf-8")
    print(f"Saved {len(repos)} repos → {OUT}")

if __name__ == "__main__":
    main()
