# Umar Farooq Portfolio

Modern static portfolio for Umar Farooq, built with HTML, CSS, JavaScript, and Bootstrap 5.3.

## Local Preview

Run a local static server from the project root:

```bash
python -m http.server 5500
```

Then open:

```text
http://localhost:5500/
```

Using a local server is recommended because the site loads JSON data files with `fetch()`.

## Statistics Projects

The `statistics_projects/` folder contains three portfolio-ready case studies:

- Student Performance Research Study
- Auto MPG Regression Analysis
- BAC Probability and Hypothesis Testing Experiment

Run the analyses from the project root:

```bash
python statistics_projects/student_performance_study/analyze.py
python statistics_projects/auto_mpg_regression/analyze.py
python statistics_projects/bac_probability_experiment/analyze.py
```

Each script generates a report and SVG charts inside its `output/` folder.

## GitHub-Ready Project Repos

The `github_projects/` folder contains three separate local git repositories prepared for GitHub:

- `github_projects/data-analysis-retail-dashboard`
- `github_projects/data-science-churn-forecasting`
- `github_projects/flutter-firebase-taskflow`

GitHub CLI is not installed on this machine, so these projects are committed locally but not pushed yet. After installing and logging in with `gh`, each folder includes `docs/github-setup.md` with the exact publish command.

## Deployment

This project can be deployed to any static host, including GitHub Pages, Netlify, Vercel, Cloudflare Pages, or shared hosting.

Before deploying:

1. Replace `https://umarfarooq.example.com/` with your real domain in `index.html`, `robots.txt`, and `sitemap.xml`.
2. Replace placeholder education and experience entries in `data/education.json` and `data/experience.json`.
3. Keep the downloadable CV current at `assets/documents/Umar_Farooq_Complete_CV.pdf`.
4. Upload the full project folder to your static hosting provider.

## Final Checks

```bash
node --check assets/js/main.js
node --check assets/js/navbar.js
node --check assets/js/darkmode.js
node --check assets/js/typewriter.js
node --check assets/js/particles.js
node --check assets/js/counter.js
node --check assets/js/skills.js
node --check assets/js/animation.js
node --check assets/js/scrollspy.js
node --check assets/js/contact.js
```
