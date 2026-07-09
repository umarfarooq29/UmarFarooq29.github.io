# GitHub Setup

This project is intended to be a separate GitHub repository.

After GitHub CLI is installed and authenticated:

```bash
gh auth login
gh repo create data-analysis-retail-dashboard --public --source . --remote origin --push
```

Recommended repo description:

```text
Retail sales analytics dashboard with Python cleaning, SQL metrics, Excel export, and BI-ready data.
```
