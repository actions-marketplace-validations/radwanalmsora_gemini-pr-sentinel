"""
Gemini PR Sentinel - Core AI Reviewer Engine.
Autonomous Pull Request review & security audit agent powered by Google Gemini.
"""

import os
import sys
import json
import urllib.request
import urllib.error

# Environment Inputs
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()
PR_NUMBER = os.getenv("PR_NUMBER", "").strip()
REPO_NAME = os.getenv("REPO_NAME", "").strip()
MAX_DIFF_LINES = int(os.getenv("MAX_DIFF_LINES", "4000"))


def log(msg: str):
    print(f"[Gemini-PR-Sentinel] {msg}", flush=True)


def get_pr_diff() -> str:
    """Fetches the unified diff of the Pull Request from GitHub API."""
    url = f"https://api.github.com/repos/{REPO_NAME}/pulls/{PR_NUMBER}"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3.diff",
        "User-Agent": "Gemini-PR-Sentinel",
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as response:
            return response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        log(f"Failed to fetch PR diff: HTTP {e.code} - {e.read().decode()}")
        sys.exit(1)


def analyze_with_gemini(diff_text: str) -> str:
    """Sends PR diff to Gemini API for high-precision code review."""
    endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"

    system_prompt = (
        "You are Gemini PR Sentinel, a world-class Principal Software Engineer and Security Specialist. "
        "Review the provided Git pull request diff thoroughly.\n\n"
        "Your review MUST include:\n"
        "1. Verdict: (Approve / Changes Requested / Comment)\n"
        "2. Executive Summary: 2-3 sentences explaining what was changed.\n"
        "3. Key Findings (Table): File, Line, Severity (Critical/Warning/Info), and Issue description.\n"
        "4. Security & Performance: Check for secret leaks, injection flaws, memory leaks, missing cleanup.\n"
        "5. Concrete Code Suggestions: Exact replacement snippets in markdown codeblocks.\n\n"
        "Formatting: Output clean, professional GitHub-flavored Markdown. Be constructive, precise, and concise."
    )

    # Safe diff truncation to fit token budget
    lines = diff_text.splitlines()
    if len(lines) > MAX_DIFF_LINES:
        truncated_diff = "\n".join(lines[:MAX_DIFF_LINES]) + "\n\n... [Diff truncated due to size limits] ..."
    else:
        truncated_diff = diff_text

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": system_prompt},
                    {"text": f"### Pull Request Diff:\n```diff\n{truncated_diff}\n```"}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 3000
        }
    }

    req = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )

    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["candidates"][0]["content"]["parts"][0]["text"]
    except urllib.error.HTTPError as e:
        log(f"Gemini API error: HTTP {e.code} - {e.read().decode()}")
        sys.exit(1)


def post_comment_to_pr(review_markdown: str):
    """Posts the generated review as a comment on the GitHub PR."""
    url = f"https://api.github.com/repos/{REPO_NAME}/issues/{PR_NUMBER}/comments"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Gemini-PR-Sentinel",
        "Content-Type": "application/json"
    }

    body_content = (
        "## 🛡️ Gemini PR Sentinel Review\n\n"
        f"{review_markdown}\n\n"
        "---\n"
        "*Powered by [Gemini PR Sentinel](https://github.com/marketplace/actions/gemini-pr-sentinel)*"
    )

    payload = {"body": body_content}

    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            log("Review comment successfully posted to PR!")
    except urllib.error.HTTPError as e:
        log(f"Failed to post comment to PR: HTTP {e.code} - {e.read().decode()}")
        sys.exit(1)


def main():
    if not GEMINI_API_KEY:
        log("ERROR: Missing GEMINI_API_KEY input.")
        sys.exit(1)

    if not GITHUB_TOKEN:
        log("ERROR: Missing GITHUB_TOKEN.")
        sys.exit(1)

    if not PR_NUMBER:
        log("No PR_NUMBER detected. This action runs on pull_request events.")
        sys.exit(0)

    log(f"Starting review for PR #{PR_NUMBER} in {REPO_NAME}...")
    diff = get_pr_diff()
    if not diff.strip():
        log("Empty diff detected. Skipping review.")
        sys.exit(0)

    log(f"Diff fetched ({len(diff.splitlines())} lines). Querying Gemini AI...")
    review = analyze_with_gemini(diff)
    log("Review generated successfully. Posting comment...")
    post_comment_to_pr(review)
    log("All tasks completed successfully!")


if __name__ == "__main__":
    main()
