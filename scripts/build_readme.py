# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Rewrite the generated blocks in README.md from live GitHub data.

Two kinds of marker are maintained:

    <!-- releases starts -->  ...  <!-- releases ends -->
    <!-- v:<repo> -->  ...  <!-- /v:<repo> -->   (latest release tag, per card)

Everything outside the markers is hand-written and never touched. Run with
`uv run scripts/build_readme.py`; needs GITHUB_TOKEN (or `gh auth token`).
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import urllib.request
from datetime import datetime
from pathlib import Path

OWNER = "hyperb1iss"
README = Path(__file__).resolve().parent.parent / "README.md"
RELEASE_COUNT = 8
MAX_DESC = 84
ENDPOINT = "https://api.github.com/graphql"

QUERY = """
query($cursor: String) {
  user(login: "%s") {
    repositories(first: 100, after: $cursor, ownerAffiliations: OWNER, isFork: false,
                 privacy: PUBLIC, orderBy: {field: PUSHED_AT, direction: DESC}) {
      pageInfo { hasNextPage endCursor }
      nodes {
        name
        url
        description
        isArchived
        releases(first: 5, orderBy: {field: CREATED_AT, direction: DESC}) {
          nodes { name tagName url publishedAt isDraft isPrerelease }
        }
      }
    }
  }
}
""" % OWNER


def token() -> str:
    if tok := os.environ.get("GITHUB_TOKEN"):
        return tok
    try:
        return subprocess.check_output(["gh", "auth", "token"], text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        sys.exit("no GITHUB_TOKEN and `gh auth token` failed")


def graphql(query: str, variables: dict) -> dict:
    body = json.dumps({"query": query, "variables": variables}).encode()
    req = urllib.request.Request(
        ENDPOINT,
        data=body,
        headers={
            "Authorization": f"bearer {token()}",
            "Content-Type": "application/json",
            "User-Agent": f"{OWNER}-profile-builder",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        payload = json.load(resp)
    if "errors" in payload:
        sys.exit(f"graphql errors: {payload['errors']}")
    return payload["data"]


def fetch_repos() -> list[dict]:
    repos: list[dict] = []
    cursor = None
    while True:
        data = graphql(QUERY, {"cursor": cursor})
        page = data["user"]["repositories"]
        repos.extend(page["nodes"])
        if not page["pageInfo"]["hasNextPage"]:
            return repos
        cursor = page["pageInfo"]["endCursor"]


def replace_block(text: str, name: str, content: str) -> str:
    pattern = re.compile(
        rf"(<!-- {name} starts -->)(.*?)(<!-- {name} ends -->)", re.DOTALL
    )
    if not pattern.search(text):
        sys.exit(f"README is missing the <!-- {name} --> markers")
    return pattern.sub(rf"\g<1>{content}\g<3>", text, count=1)


def fill_versions(text: str, latest: dict[str, dict]) -> str:
    """Rewrite every <!-- v:name -->...<!-- /v:name --> span with that repo's tag."""

    def sub(match: re.Match) -> str:
        name = match.group(1)
        rel = latest.get(name)
        if rel is None:
            print(f"warning: no published release for {name}, leaving marker as is")
            return match.group(0)
        return f"<!-- v:{name} -->{rel['tagName']}<!-- /v:{name} -->"

    return re.sub(r"<!-- v:([\w.-]+) -->.*?<!-- /v:\1 -->", sub, text, flags=re.DOTALL)


def fmt_date(iso: str) -> str:
    when = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    fmt = "%b %-d" if when.year == datetime.now(when.tzinfo).year else "%b %-d, %Y"
    return when.strftime(fmt)


def clean_description(raw: str | None) -> str:
    """Trim a repo description to one feed-friendly clause with no markdown."""
    desc = (raw or "").strip()
    desc = re.sub(r"^[^\w]+", "", desc)  # leading emoji
    desc = desc.rstrip(".!")
    if len(desc) > MAX_DESC:
        desc = desc[:MAX_DESC].rsplit(" ", 1)[0].rstrip(",;:") + "…"
    return re.sub(r"([\[\]*_`])", r"\\\1", desc)


def main() -> None:
    repos = [r for r in fetch_repos() if not r["isArchived"]]

    releases = []
    for r in repos:
        # Newest published release; drafts sort first and must be skipped.
        for rel in r["releases"]["nodes"]:
            if rel["isDraft"] or not rel["publishedAt"]:
                continue
            releases.append((rel["publishedAt"], r, rel))
            break
    releases.sort(key=lambda t: t[0], reverse=True)

    lines = []
    for published, repo, rel in releases[:RELEASE_COUNT]:
        desc = clean_description(repo["description"])
        label = f"{repo['name']} {rel['tagName']}"
        line = f"- **[{label}]({rel['url']})** · {fmt_date(published)}"
        if desc:
            line += f" · {desc}"
        lines.append(line)
    block = "\n" + "\n".join(lines) + "\n"

    original = README.read_text()
    updated = replace_block(original, "releases", block)
    updated = fill_versions(updated, {r["name"]: rel for _, r, rel in releases})

    if updated != original:
        README.write_text(updated)
        print(f"README updated: {len(lines)} releases")
    else:
        print("README unchanged")


if __name__ == "__main__":
    main()
