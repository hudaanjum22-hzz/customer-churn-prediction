import os
import numpy as np
import pandas as pd

def generate_synthetic_data(num_records=3500, random_seed=42):
    """
    Generates a realistic synthetic customer dataset for churn prediction.
    Injects a small percentage of missing values and duplicates to test preprocessing.
    """
    np.random.seed(random_seed)
    
    # 1. Generate core features
    customer_ids = [f"CUST-{i:04d}" for i in range(1001, 1001 + num_records)]
    
    # Age: Uniform distribution between 18 and 75
    age = np.random.randint(18, 76, size=num_records)
    
    # Gender: 50/50 split
    gender = np.random.choice(["Male", "Female"], size=num_records, p=[0.5, 0.5])
    
    # SubscriptionType: Basic, Premium, Enterprise
    sub_types = ["Basic", "Premium", "Enterprise"]
    subscription_type = np.random.choice(sub_types, size=num_records, p=[0.4, 0.35, 0.25])
    
    # MonthlyCharges: Dependent on SubscriptionType with some variance
    monthly_charges = []
    for sub in subscription_type:
        if sub == "Basic":
            charge = np.random.normal(50, 10)
            charge = np.clip(charge, 20, 80)
        elif sub == "Premium":
            charge = np.random.normal(100, 15)
            charge = np.clip(charge, 70, 130)
        else: # Enterprise
            charge = np.random.normal(150, 20)
            charge = np.clip(charge, 110, 220)
        monthly_charges.append(round(charge, 2))
    monthly_charges = np.array(monthly_charges)
    
    # TenureMonths: Uniform distribution between 1 and 72
    tenure_months = np.random.randint(1, 73, size=num_records)
    
    # SatisfactionScore: Integer from 1 to 10
    satisfaction_score = np.random.randint(1, 11, size=num_records)
    
    # SupportTickets: Integer from 0 to 10. Higher for lower satisfaction.
    support_tickets = []
    for sat in satisfaction_score:
        # Mean support tickets is higher for lower satisfaction score
        mean_tickets = max(0.5, 6 - (sat * 0.6))
        tickets = np.random.poisson(mean_tickets)
        tickets = np.clip(tickets, 0, 10)
        support_tickets.append(tickets)
    support_tickets = np.array(support_tickets)
    
    # PaymentMethod: 4 methods
    payment_methods = ["Bank Transfer", "Credit Card", "Electronic Check", "Mailed Check"]
    payment_method = np.random.choice(payment_methods, size=num_records, p=[0.25, 0.35, 0.25, 0.15])
    
    # UsageHoursPerWeek: Uniform/Normal around 25 hours, clipped between 1 and 60
    usage_hours = np.random.normal(25, 10, size=num_records)
    usage_hours = np.clip(usage_hours, 1, 60)
    usage_hours = np.round(usage_hours, 1)
    
    # 2. Probability of Churn calculation (FR3)
    # Satisfaction score (low satisfaction -> high churn)
    # Tenure (low tenure -> high churn)
    # Support tickets (high tickets -> high churn)
    # Usage hours (low usage -> high churn)
    # SubscriptionType = Basic (higher churn)
    
    # Normalize features to [0, 1] for standard risk scale calculation
    sat_risk = 1.0 - (satisfaction_score / 10.0)    # 0 (sat=10) to 0.9 (sat=1)
    tenure_risk = 1.0 - (tenure_months / 72.0)      # 0 (tenure=72) to 0.98 (tenure=1)
    tickets_risk = support_tickets / 10.0            # 0 to 1.0
    usage_risk = 1.0 - (usage_hours / 60.0)         # 0 to 0.98
    
    sub_risk = np.where(subscription_type == "Basic", 0.6, 
                        np.where(subscription_type == "Premium", 0.2, 0.0))
    
    charges_risk = monthly_charges / 220.0
    
    # Calculate a composite risk score (0 to 1 scale)
    # Lower satisfaction, lower tenure, higher tickets, lower usage, basic subscription, higher charges -> higher risk
    risk_score = (
        0.35 * sat_risk +
        0.20 * tenure_risk +
        0.25 * tickets_risk +
        0.10 * usage_risk +
        0.05 * sub_risk +
        0.05 * charges_risk
    )
    
    # Threshold risk score to determine baseline churn (Yes/No)
    churn = np.where(risk_score > 0.45, "Yes", "No")
    
    # Add a small amount of probabilistic noise (flip ~6% of labels to represent random churn/retention)
    flip_mask = np.random.uniform(0, 1, size=num_records) < 0.06
    churn = np.where(flip_mask, np.where(churn == "Yes", "No", "Yes"), churn)
    
    # Create DataFrame
    df = pd.DataFrame({
        "CustomerID": customer_ids,
        "Age": age,
        "Gender": gender,
        "SubscriptionType": subscription_type,
        "MonthlyCharges": monthly_charges,
        "TenureMonths": tenure_months,
        "SupportTickets": support_tickets,
        "PaymentMethod": payment_method,
        "SatisfactionScore": satisfaction_score,
        "UsageHoursPerWeek": usage_hours,
        "Churn": churn
    })
    
    # 3. Deliberately inject some missing values to test preprocessing (FR5)
    # We will randomly set ~1.5% of values to NaN in Age, MonthlyCharges, SatisfactionScore, and SubscriptionType
    num_missing = int(num_records * 0.015)
    
    for col in ["Age", "MonthlyCharges", "SatisfactionScore", "SubscriptionType"]:
        missing_idx = np.random.choice(num_records, size=num_missing, replace=False)
        df.loc[missing_idx, col] = np.nan
        
    # 4. Deliberately inject some duplicate records to test preprocessing (FR6)
    # We will duplicate ~1% of records (approx 35 rows)
    num_dupes = int(num_records * 0.01)
    dupe_idx = np.random.choice(num_records, size=num_dupes, replace=False)
    dupe_df = df.iloc[dupe_idx].copy()
    # Modify customer IDs for some duplicates, keep same for others
    # To represent exact duplicate rows, we'll keep them exactly identical
    df = pd.concat([df, dupe_df], ignore_index=True)
    
    # Shuffle the dataset to mix duplicates and missing values
    df = df.sample(frac=1, random_state=random_seed).reset_index(drop=True)
    
    return df

if __name__ == "__main__":
    print("Generating synthetic customer churn dataset...")
    df = generate_synthetic_data()
    
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)
    
    # Save to CSV
    csv_path = os.path.join("data", "customer_churn_data.csv")
    df.to_csv(csv_path, index=False)
    print(f"Dataset successfully created and saved to {csv_path}")
    print(f"Shape: {df.shape}")
    print(f"Churn Distribution:\n{df['Churn'].value_counts(dropna=False)}")
    print(f"Missing Values:\n{df.isnull().sum()}")
    print(f"Number of Duplicate Rows: {df.duplicated().sum()}")
