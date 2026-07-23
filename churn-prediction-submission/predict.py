import os
import sys
import joblib
import pandas as pd
import numpy as np

def get_input(prompt, val_type, validator=None, default=None, options_display=None):
    """
    Prompts the user for input and validates it.
    Allows user to type 'exit' or 'quit' at any prompt to exit.
    """
    full_prompt = prompt
    if options_display:
        full_prompt += f" ({options_display})"
    if default is not None:
        full_prompt += f" [Default: {default}]"
    full_prompt += ": "
    
    while True:
        user_in = input(full_prompt).strip()
        
        # Check for exit commands
        if user_in.lower() in ["exit", "quit", "q"]:
            print("\nExiting prediction tool. Goodbye!")
            sys.exit(0)
            
        # Use default if input is empty
        if not user_in and default is not None:
            return default
            
        if not user_in:
            print("Error: Input cannot be empty. Please enter a value.")
            continue
            
        # Try to cast to correct type
        try:
            val = val_type(user_in)
            # Run range/option validation
            if validator and not validator(val):
                print("Error: Input is out of acceptable bounds or options. Try again.")
                continue
            return val
        except ValueError:
            type_name = "number" if val_type in [int, float] else "text"
            print(f"Error: Invalid input format. Please enter a valid {type_name}.")

def main():
    print("="*60)
    print("CUSTOMER CHURN PREDICTION CLI TOOL")
    print("="*60)
    print("Type 'exit', 'quit', or 'q' at any prompt to exit.")
    
    # 1. Load resources (FR27, FR30)
    model_path = "models/churn_model.pkl"
    prep_path = "models/preprocessor.pkl"
    
    if not os.path.exists(model_path) or not os.path.exists(prep_path):
        print(f"Error: Trained model or preprocessor files not found.")
        print(f"Expected:\n  - {model_path}\n  - {prep_path}")
        print("Please run 'python3 src/model_training.py' first to train and save the model.")
        sys.exit(1)
        
    try:
        model = joblib.load(model_path)
        preprocessor = joblib.load(prep_path)
        print("Model and Preprocessor loaded successfully!\n")
    except Exception as e:
        print(f"Error loading files: {str(e)}")
        print("Ensure model pickles are not corrupted.")
        sys.exit(1)
        
    # 2. Main prediction loop
    run_count = 1
    while True:
        print(f"\n--- Customer Profile #{run_count} ---")
        
        # Age: 18 to 100
        age = get_input(
            "Enter customer age", 
            int, 
            validator=lambda x: 18 <= x <= 100,
            options_display="18-100"
        )
        
        # Subscription Type: Basic, Premium, Enterprise
        sub_type = get_input(
            "Enter Subscription Type",
            str,
            validator=lambda x: x.strip().title() in ["Basic", "Premium", "Enterprise"],
            options_display="Basic/Premium/Enterprise"
        ).strip().title()
        
        # Monthly Charges: >= 0
        monthly_charges = get_input(
            "Enter Monthly Charges ($)",
            float,
            validator=lambda x: x >= 0,
            options_display="e.g. 50.00"
        )
        
        # Tenure Months: 1 to 120
        tenure = get_input(
            "Enter Tenure (months)",
            int,
            validator=lambda x: 0 <= x <= 120,
            options_display="0-120"
        )
        
        # Satisfaction Score: 1 to 10
        satisfaction = get_input(
            "Enter Satisfaction Score",
            int,
            validator=lambda x: 1 <= x <= 10,
            options_display="1-10"
        )
        
        # Support Tickets: 0 to 20
        tickets = get_input(
            "Enter Support Tickets in last month",
            int,
            validator=lambda x: 0 <= x <= 20,
            options_display="0-20"
        )
        
        # Usage Hours Per Week: 0 to 168
        usage_hours = get_input(
            "Enter Usage Hours per week",
            float,
            validator=lambda x: 0.0 <= x <= 168.0,
            options_display="0-168"
        )
        
        # 3. Create dataframe for preprocessor
        # Note: Gender and PaymentMethod are defaulted as they aren't prompted in FR24
        raw_input_df = pd.DataFrame({
            "Age": [age],
            "Gender": ["Male"],
            "SubscriptionType": [sub_type],
            "MonthlyCharges": [monthly_charges],
            "TenureMonths": [tenure],
            "SupportTickets": [tickets],
            "PaymentMethod": ["Credit Card"],
            "SatisfactionScore": [satisfaction],
            "UsageHoursPerWeek": [usage_hours]
        })
        
        # 4. Run Preprocessing & Inference (FR25)
        try:
            processed_input = preprocessor.transform(raw_input_df, is_training=False)
            
            # Predict
            pred = model.predict(processed_input)[0]
            prob = model.predict_proba(processed_input)[0][1] # Probability of Churn (Class 1)
            
            print("\n" + "-"*35)
            print("PREDICTION RESULT:")
            print("-"*35)
            if pred == 1:
                print(">>> STATUS: CUSTOMER LIKELY TO CHURN <<<")
            else:
                print(">>> STATUS: Customer Likely to Stay <<<")
            print(f"Churn Probability: {prob:.2%}")
            print("-"*35)
            
        except Exception as e:
            print(f"An error occurred during inference: {str(e)}")
            
        # Ask to continue
        cont = input("\nDo you want to predict for another customer? (y/n) [Default: y]: ").strip().lower()
        if cont in ["n", "no"]:
            print("\nThank you for using the Churn Prediction CLI tool. Goodbye!")
            break
        run_count += 1

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nPrediction tool terminated by user. Goodbye!")
        sys.exit(0)
