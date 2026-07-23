import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def run_eda(df, plots_dir="plots"):
    """
    Performs EDA on the customer dataframe, prints statistical insights,
    and generates/saves the four required visualizations.
    """
    # Create plots directory if it doesn't exist
    os.makedirs(plots_dir, exist_ok=True)
    
    print("\n" + "="*50)
    print("EXPLORATORY DATA ANALYSIS (EDA)")
    print("="*50)
    
    # 1. Shape and Basics
    print(f"Dataset shape: {df.shape}")
    print("\nData Columns & Missing Values:")
    print(df.isnull().sum())
    
    # 2. Overall Churn Distribution (FR10, FR15)
    churn_counts = df['Churn'].value_counts(dropna=False)
    churn_pct = df['Churn'].value_counts(normalize=True, dropna=False) * 100
    print("\nChurn Distribution:")
    for label in churn_counts.index:
        label_str = "NaN" if pd.isna(label) else label
        print(f"  {label_str}: {churn_counts[label]} ({churn_pct[label]:.2f}%)")
    
    # Generate Pie Chart (FR15)
    plt.figure(figsize=(6, 6))
    colors = ['#4f46e5', '#f43f5e'] # Modern violet and rose/red colors
    plt.pie(
        churn_counts, 
        labels=churn_counts.index, 
        autopct='%1.1f%%', 
        startangle=90, 
        colors=colors,
        textprops={'fontsize': 12, 'weight': 'bold', 'color': 'white'}
    )
    plt.title("Overall Customer Churn Distribution", fontsize=14, weight='bold', pad=20)
    # Style legend
    plt.legend(churn_counts.index, loc="upper right", frameon=True, facecolor="#ffffff")
    plt.tight_layout()
    pie_path = os.path.join(plots_dir, "churn_distribution_pie.png")
    plt.savefig(pie_path, dpi=150, facecolor='white')
    plt.close()
    print(f"Saved: {pie_path}")
    
    # For sub-analyses, let's work on cleaned/imputed data (so we don't have NaNs interfering)
    # We clean temporary for analysis
    anal_df = df.copy()
    anal_df['Churn'] = anal_df['Churn'].fillna('No')
    anal_df['SubscriptionType'] = anal_df['SubscriptionType'].fillna(anal_df['SubscriptionType'].mode()[0])
    anal_df['TenureMonths'] = anal_df['TenureMonths'].fillna(anal_df['TenureMonths'].median())
    anal_df['SatisfactionScore'] = anal_df['SatisfactionScore'].fillna(anal_df['SatisfactionScore'].median())
    anal_df['MonthlyCharges'] = anal_df['MonthlyCharges'].fillna(anal_df['MonthlyCharges'].median())
    
    # 3. Churn by Subscription Type (FR13, FR16)
    print("\nChurn rate by Subscription Type:")
    sub_churn = pd.crosstab(anal_df['SubscriptionType'], anal_df['Churn'], normalize='index') * 100
    print(sub_churn)
    
    # Generate Subscription Type Bar Chart (FR16)
    plt.figure(figsize=(8, 5))
    # We plot the churn rate (Yes) per subscription type
    churn_rates = anal_df.groupby('SubscriptionType')['Churn'].apply(lambda x: (x == 'Yes').mean() * 100).reset_index()
    sns.barplot(
        x='SubscriptionType', 
        y='Churn', 
        data=churn_rates, 
        palette=['#6366f1', '#818cf8', '#a5b4fc'],
        order=['Basic', 'Premium', 'Enterprise']
    )
    plt.title("Churn Rate (%) by Subscription Type", fontsize=14, weight='bold', pad=15)
    plt.xlabel("Subscription Type", fontsize=12, labelpad=10)
    plt.ylabel("Churn Rate (%)", fontsize=12, labelpad=10)
    plt.ylim(0, 100)
    # Annotate bars
    for index, row in churn_rates.iterrows():
        plt.text(index, row['Churn'] + 2, f"{row['Churn']:.1f}%", color='black', ha="center", weight='bold')
    plt.tight_layout()
    bar_path = os.path.join(plots_dir, "churn_rate_by_subscription.png")
    plt.savefig(bar_path, dpi=150, facecolor='white')
    plt.close()
    print(f"Saved: {bar_path}")
    
    # 4. TenureMonths vs Churn (FR11)
    print("\nTenure (Months) Statistics by Churn Status:")
    tenure_stats = anal_df.groupby('Churn')['TenureMonths'].describe()
    print(tenure_stats)
    
    # 5. SatisfactionScore vs Churn (FR12)
    print("\nSatisfaction Score (1-10) Distribution by Churn Status:")
    sat_stats = anal_df.groupby('Churn')['SatisfactionScore'].describe()
    print(sat_stats)
    
    # 6. Feature Correlation Matrix (FR14, FR17)
    num_cols = ["Age", "MonthlyCharges", "TenureMonths", "SupportTickets", "SatisfactionScore", "UsageHoursPerWeek"]
    # Add numeric target Churn_Numeric
    anal_df['Churn_Numeric'] = np.where(anal_df['Churn'] == 'Yes', 1, 0)
    corr_cols = num_cols + ['Churn_Numeric']
    corr_matrix = anal_df[corr_cols].corr()
    print("\nCorrelation Matrix (Numeric features + Churn_Numeric):")
    print(corr_matrix)
    
    # Generate Heatmap (FR17)
    plt.figure(figsize=(10, 8))
    sns.heatmap(
        corr_matrix, 
        annot=True, 
        fmt=".2f", 
        cmap="coolwarm", 
        vmin=-1, 
        vmax=1, 
        linewidths=0.5,
        annot_kws={"size": 10, "weight": "bold"}
    )
    plt.title("Feature Correlation Matrix (including Churn)", fontsize=14, weight='bold', pad=20)
    plt.tight_layout()
    heatmap_path = os.path.join(plots_dir, "correlation_matrix_heatmap.png")
    plt.savefig(heatmap_path, dpi=150, facecolor='white')
    plt.close()
    print(f"Saved: {heatmap_path}")
    
    # 7. Distribution of MonthlyCharges (FR18)
    # Generate Histogram (FR18)
    plt.figure(figsize=(8, 5))
    sns.histplot(
        data=anal_df, 
        x="MonthlyCharges", 
        hue="Churn", 
        multiple="stack", 
        kde=True,
        palette=['#4f46e5', '#f43f5e'],
        bins=30
    )
    plt.title("Distribution of Monthly Charges by Churn Status", fontsize=14, weight='bold', pad=15)
    plt.xlabel("Monthly Charges ($)", fontsize=12, labelpad=10)
    plt.ylabel("Customer Count", fontsize=12, labelpad=10)
    plt.tight_layout()
    hist_path = os.path.join(plots_dir, "monthly_charges_histogram.png")
    plt.savefig(hist_path, dpi=150, facecolor='white')
    plt.close()
    print(f"Saved: {hist_path}")
    
    # 8. Extra analysis: Tenure vs Churn and Satisfaction Score Boxplots (FR19)
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Tenure Boxplot
    sns.boxplot(ax=axes[0], x='Churn', y='TenureMonths', data=anal_df, palette=['#4f46e5', '#f43f5e'])
    axes[0].set_title("Customer Tenure by Churn Status", fontsize=12, weight='bold')
    axes[0].set_xlabel("Churn", fontsize=10)
    axes[0].set_ylabel("Tenure (Months)", fontsize=10)
    
    # Satisfaction Score Boxplot
    sns.boxplot(ax=axes[1], x='Churn', y='SatisfactionScore', data=anal_df, palette=['#4f46e5', '#f43f5e'])
    axes[1].set_title("Satisfaction Score by Churn Status", fontsize=12, weight='bold')
    axes[1].set_xlabel("Churn", fontsize=10)
    axes[1].set_ylabel("Satisfaction Score (1-10)", fontsize=10)
    
    plt.tight_layout()
    extra_path = os.path.join(plots_dir, "tenure_satisfaction_boxplots.png")
    plt.savefig(extra_path, dpi=150, facecolor='white')
    plt.close()
    print(f"Saved: {extra_path}")
    
    print("="*50)
    print("EDA COMPLETE AND VISUALIZATIONS SAVED")
    print("="*50 + "\n")

if __name__ == "__main__":
    csv_path = os.path.join("data", "customer_churn_data.csv")
    if not os.path.exists(csv_path):
        print(f"Dataset not found at {csv_path}. Please run src/data_generation.py first.")
    else:
        df = pd.read_csv(csv_path)
        run_eda(df)
