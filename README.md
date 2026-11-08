# 🛡️ Gemini PR Sentinel

<div align="center">

[![GitHub Marketplace](https://img.shields.io/badge/Marketplace-Gemini%20PR%20Sentinel-blue?style=for-the-badge&logo=githubactions&logoColor=white)](https://github.com/marketplace/actions/gemini-pr-sentinel)
[![Powered by Gemini](https://img.shields.io/badge/AI-Google%20Gemini-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-F5A623?style=for-the-badge&logo=opensourceinitiative&logoColor=white)](https://opensource.org/licenses/MIT)
[![Release](https://img.shields.io/badge/Version-v1.0.0-emerald?style=for-the-badge)](https://github.com/radwanalmsora/gemini-pr-sentinel/releases)

**An autonomous AI Code Reviewer and Security Audit Agent that inspects GitHub Pull Requests in seconds using Google Gemini.**

[Features](#-key-features) • [Quickstart](#-quickstart) • [Configuration](#-action-inputs) • [Example Output](#-example-pr-review-output) • [License](#-license)

</div>

---

## 🌟 Key Features

- 🧠 **Autonomous Code Review**: Performs deep semantic analysis on code diffs across all languages (JavaScript, TypeScript, Python, Go, Rust, Java, etc.).
- 🛡️ **Security Vulnerability Scanner**: Detects exposed secrets, SQL injections, insecure dependencies, and memory leaks before merging.
- ⚡ **Near-Instant Analysis**: Leverages Google Gemini Flash models for lightning-fast feedback on every Pull Request.
- 💬 **Interactive Markdown PR Comments**: Posts elegant, structured review summaries directly into the Pull Request discussion.
- 🎯 **Actionable Refactoring Tips**: Provides exact code replacement suggestions and best-practice refactoring.
- 🆓 **100% Free**: Operates within Google Gemini's free API tier with zero external servers.

---

## 🚀 Quickstart

Create a workflow file at `.github/workflows/pr-review.yml` in your repository:

```yaml
name: "Gemini PR Sentinel"

on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  review:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write

    steps:
      - name: Checkout Code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Run Gemini PR Sentinel
        uses: radwanalmsora/gemini-pr-sentinel@v1
        with:
          gemini-api-key: ${{ secrets.GEMINI_API_KEY }}
          github-token: ${{ secrets.GITHUB_TOKEN }}
