 Customer Churn Prediction System

A machine learning system that predicts whether a customer is likely to churn (cancel their subscription) based on their profile, usage patterns, and satisfaction.

 Project Overview

This project builds an end-to-end churn prediction pipeline:
1. Generates a synthetic dataset of 3,500+ customer records
2. Cleans and preprocesses the data
3. Performs exploratory data analysis (EDA) with visualizations
4. Trains and compares multiple classification models
5. Provides an interactive console tool to predict churn for a new customer

 Dataset

`data/customer_churn_data.csv` contains 3,535 synthetic customer records with the following features:

| Column | Description |
|---|---|
| CustomerID | Unique customer identifier |
| Age | Customer age |
| Gender | Male/Female |
| SubscriptionType | Basic/Premium/Enterprise |
| MonthlyCharges | Monthly subscription fee ($) |
| TenureMonths | Number of months as a customer |
| SupportTickets | Number of support requests raised |
| PaymentMethod | Credit Card/UPI/Net Banking/Debit Card |
| SatisfactionScore | Customer satisfaction rating (1–10) |
| UsageHoursPerWeek | Weekly service usage |
| Churn | Target variable (Yes/No) |

 Files

| File | Purpose |
|---|---|
| `data_generation.py` | Generates the synthetic dataset with realistic churn patterns |
| `preprocessing.py` | `ChurnPreprocessor` class — handles missing values, duplicates, range validation, encoding, and scaling |
| `eda_visualization.py` | Runs exploratory data analysis and saves visualizations to `plots/` |
| `model_training.py` | Trains and compares 3 classification models, saves the best one |
| `predict.py` | Interactive console tool for predicting churn on a new customer |
| `churn_analysis.ipynb` | Notebook version of the full analysis with inline outputs and charts |
| `models/churn_model.pkl` | The trained, serialized best-performing model |
| `models/preprocessor.pkl` | The fitted preprocessor (encoder + scaler) used by the model |

## Exploratory Data Analysis

Key findings (see `plots/` for visualizations):
- **Churn distribution**: ~45.7% of customers in the dataset have churned
- **Subscription type**: Churn rate is fairly consistent across Basic, Premium, and Enterprise plans
- **Satisfaction score**: Strongly correlated with support ticket volume — customers with more tickets tend to report lower satisfaction
- **Tenure**: Newer customers show different churn behavior compared to long-tenured ones

Visualizations generated:
- `churn_distribution_pie.png` — overall churn split
- `churn_rate_by_subscription.png` — churn rate by plan type
- `correlation_matrix_heatmap.png` — correlation across all numeric features
- `monthly_charges_histogram.png` — distribution of monthly charges, split by churn status
- `tenure_satisfaction_boxplots.png` — tenure and satisfaction score comparisons between churned and retained customers

 Model Training & Evaluation

Three classification models were trained and compared:

| Model | Accuracy | Precision | Recall | F1-Score |
|---|---|---|---|---|
| Logistic Regression | 94.29% | 0.943 | 0.931 | 0.937 |
| Decision Tree | 91.57% | 0.912 | 0.903 | 0.907 |
| Random Forest | 92.00% | 0.934 | 0.888 | 0.910 |

Selected model: Logistic Regression (highest F1-score on the churn class)

Both target success criteria were met:
- Accuracy ≥ 80%: **Passed** (94.29%)
- F1-score ≥ 0.75: **Passed** (0.937)

Data was split 80/20 (train/test) using stratified sampling to preserve the churn class ratio, and the preprocessor was fit only on training data to prevent data leakage.

 How to Run
 1. Install dependencies
```bash
pip install -r requirements.txt
```

 2. (Optional) Regenerate the dataset
```bash
python3 data_generation.py
```

 3. Train the model
```bash
python3 model_training.py
```
This prints accuracy, precision, recall, F1-score, and confusion matrix for each model, then saves the best one to `models/`.

 4. Run the interactive prediction tool
```bash
python3 predict.py
```
You'll be prompted to enter a customer's Age, Subscription Type, Monthly Charges, Tenure, Satisfaction Score, Support Tickets, and Usage Hours. The tool then predicts whether that customer is **Likely to Churn** or **Likely to Stay**, along with a churn probability.

Type `exit`, `quit`, or `q` at any prompt to exit early.

 5. (Optional) View the notebook
Open `churn_analysis.ipynb` in Jupyter or VS Code to see the full analysis with inline outputs and charts.

 Error Handling

The prediction tool validates all inputs:
- Rejects non-numeric input where numbers are expected
- Enforces valid ranges (e.g. Age 18–100, Satisfaction 1–10)
- Handles missing model/preprocessor files gracefully with clear error messages
- Allows graceful exit at any point

Tech Stack

- Python 3
- pandas, NumPy
- scikit-learn (Logistic Regression, Decision Tree, Random Forest)
- Matplotlib, Seaborn
- joblib (model serialization)
