$ErrorActionPreference = "Stop"

if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
  throw "GitHub CLI is not installed. Install it from https://cli.github.com/ and run: gh auth login"
}

gh auth status

$projects = @(
  @{
    Path = "data-analysis-retail-dashboard"
    Repo = "data-analysis-retail-dashboard"
    Description = "Retail sales analytics dashboard with Python cleaning, SQL metrics, Excel export, and BI-ready data."
  },
  @{
    Path = "data-science-churn-forecasting"
    Repo = "data-science-churn-forecasting"
    Description = "Customer churn machine learning project with EDA, model evaluation, and forecasting outputs."
  },
  @{
    Path = "flutter-firebase-taskflow"
    Repo = "taskflow-flutter-firebase"
    Description = "Flutter Firebase task management app with REST API loading and responsive UI."
  }
)

foreach ($project in $projects) {
  Push-Location -LiteralPath (Join-Path $PSScriptRoot $project.Path)
  try {
    $remote = git remote get-url origin 2>$null
    if (-not $remote) {
      gh repo create $project.Repo --public --source . --remote origin --push --description $project.Description
    } else {
      git push -u origin main
    }
  } finally {
    Pop-Location
  }
}
