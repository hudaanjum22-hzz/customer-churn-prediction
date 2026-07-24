import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import pandas as pd
import joblib
import os

from preprocessing import ChurnPreprocessor

app = FastAPI(title="Churn Prediction API")

# Allow the Vite frontend (localhost:5173) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://customer-churn-prediction-rho-brown.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_PATH = "models/churn_model.pkl"
PREP_PATH = "models/preprocessor.pkl"

if not os.path.exists(MODEL_PATH) or not os.path.exists(PREP_PATH):
    raise RuntimeError("Model or preprocessor file not found in models/")

model = joblib.load(MODEL_PATH)
preprocessor = joblib.load(PREP_PATH)


class PredictionInput(BaseModel):
    age: int = Field(..., ge=18, le=100)
    subscription_type: str
    monthly_charges: float = Field(..., ge=0)
    tenure_months: int = Field(..., ge=0, le=120)
    satisfaction_score: int = Field(..., ge=1, le=10)
    support_tickets: int = Field(..., ge=0, le=20)
    usage_hours_per_week: float = Field(..., ge=0, le=168)


@app.get("/")
def root():
    return {"status": "Churn Prediction API is running"}


@app.post("/api/predict")
def predict(input_data: PredictionInput):
    if input_data.subscription_type not in ["Basic", "Premium", "Enterprise"]:
        raise HTTPException(status_code=400, detail="Invalid subscription_type")

    raw_input_df = pd.DataFrame({
        "Age": [input_data.age],
        "Gender": ["Male"],
        "SubscriptionType": [input_data.subscription_type],
        "MonthlyCharges": [input_data.monthly_charges],
        "TenureMonths": [input_data.tenure_months],
        "SupportTickets": [input_data.support_tickets],
        "PaymentMethod": ["Credit Card"],
        "SatisfactionScore": [input_data.satisfaction_score],
        "UsageHoursPerWeek": [input_data.usage_hours_per_week]
    })

    try:
        processed_input = preprocessor.transform(raw_input_df, is_training=False)
        pred = model.predict(processed_input)[0]
        prob = model.predict_proba(processed_input)[0][1]

        return {
            "prediction": "Likely to Churn" if pred == 1 else "Likely to Stay",
            "churn_probability": round(float(prob), 4)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analytics")
def analytics():
    try:
        df = pd.read_csv("data/customer_churn_data.csv")

        total_customers = len(df)
        # Churn column is assumed to be 0/1 or Yes/No - handle both
        if df["Churn"].dtype == object:
            churn_flag = df["Churn"].str.lower().isin(["yes", "1", "true"])
        else:
            churn_flag = df["Churn"] == 1
        churn_rate = round(float(churn_flag.mean()) * 100, 1)
        avg_satisfaction = round(float(df["SatisfactionScore"].mean()), 1)

        # Pie chart: churn distribution
        churn_distribution = {
            "churned": int(churn_flag.sum()),
            "retained": int((~churn_flag).sum())
        }

        # Bar chart: churn rate by subscription type
        by_sub = df.groupby("SubscriptionType").apply(
            lambda g: round(float((g["Churn"].str.lower().isin(["yes", "1", "true"]) if g["Churn"].dtype == object else g["Churn"] == 1).mean()) * 100, 1)
        ).to_dict()

        # Correlation heatmap (numeric columns only)
        num_cols = ["Age", "MonthlyCharges", "TenureMonths", "SupportTickets", "SatisfactionScore", "UsageHoursPerWeek"]
        corr_matrix = df[num_cols].corr().round(2).to_dict()

        # Histogram: monthly charges bins
        hist_counts, hist_edges = np.histogram(df["MonthlyCharges"].dropna(), bins=10)
        histogram = {
            "counts": hist_counts.tolist(),
            "bin_edges": [round(float(e), 2) for e in hist_edges]
        }

        return {
            "kpis": {
                "total_customers": total_customers,
                "churn_rate": churn_rate,
                "avg_satisfaction": avg_satisfaction
            },
            "churn_distribution": churn_distribution,
            "churn_by_subscription": by_sub,
            "correlation_matrix": corr_matrix,
            "monthly_charges_histogram": histogram
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
