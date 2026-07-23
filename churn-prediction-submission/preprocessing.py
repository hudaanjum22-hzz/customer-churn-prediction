import numpy as np
import pandas as pd
from sklearn.preprocessing import OneHotEncoder, StandardScaler

class ChurnPreprocessor:
    """
    A unified preprocessor class for the Customer Churn Prediction System.
    Handles data cleaning, missing value imputation, value range validation,
    one-hot encoding for categorical features, and standard scaling for numeric features.
    
    Shared between training and CLI prediction scripts.
    """
    def __init__(self):
        # Stored values for imputation (fit on training data)
        self.impute_values_ = {}
        
        # Categorical and numerical column lists
        self.num_cols = ["Age", "MonthlyCharges", "TenureMonths", "SupportTickets", "SatisfactionScore", "UsageHoursPerWeek"]
        self.cat_cols = ["Gender", "SubscriptionType", "PaymentMethod"]
        
        # Define exact categories for deterministic encoding columns
        self.categories = [
            ["Female", "Male"],
            ["Basic", "Premium", "Enterprise"],
            ["Credit Card", "UPI", "Net Banking", "Debit Card"]
        ]
        
        # Initializing encoder and scaler
        try:
            self.encoder = OneHotEncoder(categories=self.categories, handle_unknown="ignore", sparse_output=False)
        except TypeError:
            # Fallback for older scikit-learn versions
            self.encoder = OneHotEncoder(categories=self.categories, handle_unknown="ignore", sparse=False)
            
        self.scaler = StandardScaler()
        self.is_fitted = False

    def clean_data(self, df, is_training=True):
        """
        Detects and handles missing values, duplicates, and range anomalies.
        """
        # Make a copy to avoid SettingWithCopyWarning
        cleaned_df = df.copy()
        
        # Note: Duplicate records should be removed from the full DataFrame (including target) 
        # prior to calling fit/transform to prevent length mismatch with target y.
        
        # 2. Drop CustomerID since it's an identifier, not a predictor
        if "CustomerID" in cleaned_df.columns:
            cleaned_df = cleaned_df.drop(columns=["CustomerID"])
            
        # 3. Handle missing values
        # Numeric columns imputation
        for col in self.num_cols:
            if col in cleaned_df.columns:
                # During training, compute and save medians
                if is_training:
                    # Exclude NaN when computing median
                    self.impute_values_[col] = cleaned_df[col].median(skipna=True)
                
                # Fill missing values
                fill_val = self.impute_values_.get(col, 35.0) # default fallback
                cleaned_df[col] = cleaned_df[col].fillna(fill_val)
                
        # Categorical columns imputation
        for col in self.cat_cols:
            if col in cleaned_df.columns:
                # During training, compute and save mode
                if is_training:
                    self.impute_values_[col] = cleaned_df[col].mode().dropna().iloc[0]
                
                fill_val = self.impute_values_.get(col, "Basic" if col == "SubscriptionType" else "Male" if col == "Gender" else "Credit Card")
                cleaned_df[col] = cleaned_df[col].fillna(fill_val)
                
        # 4. Range and type validations
        # Clip numeric variables to valid ranges if they go out of bounds
        if "Age" in cleaned_df.columns:
            cleaned_df["Age"] = cleaned_df["Age"].astype(float).clip(lower=1.0, upper=120.0)
        if "SatisfactionScore" in cleaned_df.columns:
            cleaned_df["SatisfactionScore"] = cleaned_df["SatisfactionScore"].astype(float).clip(lower=1.0, upper=10.0)
        if "SupportTickets" in cleaned_df.columns:
            cleaned_df["SupportTickets"] = cleaned_df["SupportTickets"].astype(float).clip(lower=0.0, upper=20.0)
        if "TenureMonths" in cleaned_df.columns:
            cleaned_df["TenureMonths"] = cleaned_df["TenureMonths"].astype(float).clip(lower=0.0, upper=120.0)
        if "UsageHoursPerWeek" in cleaned_df.columns:
            cleaned_df["UsageHoursPerWeek"] = cleaned_df["UsageHoursPerWeek"].astype(float).clip(lower=0.0, upper=168.0)
        if "MonthlyCharges" in cleaned_df.columns:
            cleaned_df["MonthlyCharges"] = cleaned_df["MonthlyCharges"].astype(float).clip(lower=0.0)
            
        return cleaned_df

    def fit(self, df):
        """
        Fits encoders and scalers on the cleaned DataFrame.
        """
        # First clean the data to set up imputation parameters
        cleaned_df = self.clean_data(df, is_training=True)
        
        # Fit OneHotEncoder
        self.encoder.fit(cleaned_df[self.cat_cols])
        
        # Fit StandardScaler
        self.scaler.fit(cleaned_df[self.num_cols])
        
        self.is_fitted = True
        return self

    def transform(self, df, is_training=False):
        """
        Cleans and transforms input DataFrame using the fitted preprocessor.
        """
        if not self.is_fitted:
            raise ValueError("Preprocessor has not been fitted yet! Call fit() before transform().")
            
        # Clean input dataframe
        cleaned_df = self.clean_data(df, is_training=is_training)
        
        # Encode categorical columns
        encoded_cats = self.encoder.transform(cleaned_df[self.cat_cols])
        encoded_cols = self.encoder.get_feature_names_out(self.cat_cols)
        encoded_df = pd.DataFrame(encoded_cats, columns=encoded_cols, index=cleaned_df.index)
        
        # Scale numerical columns
        scaled_nums = self.scaler.transform(cleaned_df[self.num_cols])
        scaled_df = pd.DataFrame(scaled_nums, columns=self.num_cols, index=cleaned_df.index)
        
        # Merge scaled numeric features and encoded categorical features
        processed_df = pd.concat([scaled_df, encoded_df], axis=1)
        
        return processed_df

    def fit_transform(self, df):
        """
        Combines fit and transform.
        """
        self.fit(df)
        return self.transform(df, is_training=True)
