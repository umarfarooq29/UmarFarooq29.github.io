# Customer Churn Machine Learning and Forecasting Report

## Project Question

Which customers are most likely to churn, and how many churn events should the business expect over the next six months?

## Exploratory Data Analysis

- Customers analyzed: 900
- Overall churn rate: 55.0%
- Highest-risk segment is visible through contract-level churn rates.

| Contract type | Customers | Churn rate |
| --- | --- | --- |
| Month-to-month | 477 | 63.5% |
| One year | 260 | 45.8% |
| Two year | 163 | 44.8% |

## Model Evaluation

| Metric | Value |
| --- | --- |
| Accuracy | 0.738 |
| Precision | 0.769 |
| Recall | 0.775 |
| F1 score | 0.772 |
| ROC AUC | 0.764 |

## Forecast

| Month | Expected churned customers | Retention program effect |
| --- | --- | --- |
| Month 1 | 79.5 | 2.5% |
| Month 2 | 77.4 | 5.0% |
| Month 3 | 75.4 | 7.5% |
| Month 4 | 73.3 | 10.0% |
| Month 5 | 71.3 | 12.5% |
| Month 6 | 69.3 | 15.0% |

## Portfolio Interpretation

The project demonstrates EDA, supervised machine learning, model evaluation, churn scoring, and practical forecasting. It is ready to be extended with Pandas, NumPy, scikit-learn, and notebook visuals.
