#!/usr/bin/env python3
"""
Devcontainer Scanner
--------------------
Scrapes GitHub organizations, custom lists, and GDS repo pages to locate
repositories that contain a configured devcontainer.json file.
"""

import csv
import logging
import os
import sys
import time
from typing import List, Set
import urllib.parse

from bs4 import BeautifulSoup
import requests

# Set up clean, structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

# Devcontainer paths relative to the repo root
DEVCONTAINER_PATHS = [
    ".devcontainer/devcontainer.json",
    ".devcontainer.json",
]


class DevcontainerScanner:
    def __init__(self, token: str = None):
        """Initialize GitHub client session with mandatory authentication headers."""
        self.token = token or os.environ.get("GITHUB_TOKEN")
        self.session = requests.Session()
        
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "GDS-Devcontainer-Scanner",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        else:
            logging.warning(
                "No GITHUB_TOKEN provided. Unauthenticated requests will be heavily rate-limited (60 req/hr)."
            )

        self.session.headers.update(headers)

    def _check_rate_limit(self, response: requests.Response):
        """Handle GitHub REST API rate limits and automatically pause if exhausted."""
        remaining = response.headers.get("X-RateLimit-Remaining")
        reset_time = response.headers.get("X-RateLimit-Reset")

        if remaining and int(remaining) == 0 and reset_time:
            sleep_duration = max(int(reset_time) - int(time.time()), 1) + 5
            logging.warning(f"Rate limit reached. Sleeping for {sleep_duration} seconds...")
            time.sleep(sleep_duration)

    def fetch_org_repos(self, org_name: str) -> List[str]:
        """Fetch all public repositories for a given GitHub organization."""
        repos = []
        page = 1
        url = f"https://api.github.com/orgs/{org_name}/repos"

        logging.info(f"Fetching repository list for organization: '{org_name}'...")
        while True:
            params = {"per_page": 100, "page": page, "type": "public"}
            resp = self.session.get(url, params=params)
            self._check_rate_limit(resp)

            if resp.status_code != 200:
                logging.error(f"Failed to fetch repos for org '{org_name}': {resp.status_code}")
                break

            data = resp.json()
            if not data:
                break

            for repo in data:
                repos.append(repo["full_name"])

            page += 1

        logging.info(f"Found {len(repos)} repositories in organization '{org_name}'.")
        return repos

    def parse_govuk_doc_repos(self, html_url: str) -> List[str]:
        """Scrape GOV.UK publishing documentation HTML page to extract GitHub repository names."""
        logging.info(f"Parsing repository list from docs URL: {html_url}...")
        try:
            resp = self.session.get(html_url, timeout=15)
            resp.raise_for_status()
        except requests.RequestException as e:
            logging.error(f"Failed to retrieve documentation page: {e}")
            return []

        soup = BeautifulSoup(resp.text, "html.parser")
        repo_names: Set[str] = set()

        # Non-repository system path keywords
        ignored_segments = {
            "features", "sponsors", "orgs", "topics", 
            "settings", "marketplace", "explore", "search"
        }

        for anchor in soup.find_all("a", href=True):
            href = anchor["href"]
            if "github.com/" in href:
                parsed = urllib.parse.urlparse(href)
                parts = [p for p in parsed.path.strip("/").split("/") if p]
                if len(parts) >= 2:
                    org, repo = parts[0], parts[1]
                    # Filter out non-repository GitHub URLs
                    if org not in ignored_segments and repo not in ignored_segments:
                        repo_names.add(f"{org}/{repo}")

        logging.info(f"Extracted {len(repo_names)} unique repo URLs from documentation page.")
        return list(repo_names)

    def check_devcontainer_exists(self, repo_full_name: str) -> bool:
        """Check if any devcontainer.json configuration file exists in the target repository."""
        for path in DEVCONTAINER_PATHS:
            url = f"https://api.github.com/repos/{repo_full_name}/contents/{path}"
            resp = self.session.get(url)
            self._check_rate_limit(resp)

            if resp.status_code == 200:
                return True
        return False


def main():
    scanner = DevcontainerScanner()

    # Step 1: Collect repositories from all target sources
    target_repos: Set[str] = set()

    # Target 1: GitHub Organizations
    orgs = ["alphagov", "govuk-one-login"]
    for org in orgs:
        for repo in scanner.fetch_org_repos(org):
            target_repos.add(repo)

    # Target 2: GOV.UK publishing documentation page
    doc_url = "https://docs.publishing.service.gov.uk/repos.html"
    for repo in scanner.parse_govuk_doc_repos(doc_url):
        target_repos.add(repo)

    total_count = len(target_repos)
    logging.info(f"Total unique repositories queue size: {total_count}")

    # Step 2: Scan each repository for devcontainer configuration
    results = []
    matched_count = 0

    for idx, repo in enumerate(sorted(target_repos), start=1):
        has_devcontainer = scanner.check_devcontainer_exists(repo)
        if has_devcontainer:
            matched_count += 1
            logging.info(f"[{idx}/{total_count}] ✅ MATCH: {repo} contains a devcontainer!")
            results.append({"repository": repo, "has_devcontainer": True, "url": f"https://github.com/{repo}"})
        else:
            logging.debug(f"[{idx}/{total_count}] ❌ {repo} - No devcontainer found.")

    # Step 3: Export findings to CSV
    output_filename = "devcontainer_audit_results.csv"
    with open(output_filename, mode="w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=["repository", "has_devcontainer", "url"])
        writer.writeheader()
        writer.writerows(results)

    # Final Summary
    logging.info("=" * 60)
    logging.info(f"Scan complete. Found {matched_count} repos with devcontainers out of {total_count} checked.")
    logging.info(f"Results successfully saved to {os.path.abspath(output_filename)}")
    logging.info("=" * 60)


if __name__ == "__main__":
    main()