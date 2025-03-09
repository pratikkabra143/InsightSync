import random
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import re
from textblob import TextBlob
from django.utils.timezone import now
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from .models import Customer
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

# --------------------------
# Generate Initial Churn Scores
# --------------------------
def generate_initial_churn_scores():
    """
    Assigns an initial churn score to customers based on their behavior.
    This is used to bootstrap the model before real predictions.
    """
    customers = Customer.objects.all()

    for customer in customers:
        tenure = (now().date() - customer.registration_date).days
        last_purchase_gap = (now().date() - customer.last_purchase_date).days if customer.last_purchase_date else 365
        spending_factor = customer.spending_factor  # Simulate spending influence
        churn_score = min(1, max(0, (last_purchase_gap / (tenure + 1)) * float(spending_factor)))


        # Update churn score in database
        customer.churn_score = round(churn_score, 2)
        customer.save()

    print("✅ Initial churn scores assigned to customers.")

def train_churn_model():
    """
    Trains a Logistic Regression model using real customer churn data.
    """
    df = pd.DataFrame(list(Customer.objects.values("id", "registration_date", "last_purchase_date", "churn_score")))

    if df.empty or len(df) < 10:
        print("⚠️ Not enough customer data to train the model.")
        return None, None

    # Convert date fields to datetime, coercing errors to NaT
    df["registration_date"] = pd.to_datetime(df["registration_date"], errors="coerce")
    df["last_purchase_date"] = pd.to_datetime(df["last_purchase_date"], errors="coerce")

    # Convert now() to a timezone-naive datetime by removing tzinfo
    now_naive = now().replace(tzinfo=None)

    # Compute tenure (days since registration)
    df["tenure"] = (pd.Timestamp(now_naive) - df["registration_date"]).dt.days

    # Compute last purchase gap (days since last purchase)
    df["last_purchase_gap"] = (pd.Timestamp(now_naive) - df["last_purchase_date"]).dt.days
    df["last_purchase_gap"].fillna(365, inplace=True)
    df["last_purchase_gap"] = df["last_purchase_gap"].astype(int)

    # Encode churn as 0 (low risk) and 1 (high risk)
    df["churn"] = df["churn_score"].apply(lambda x: 1 if x and x > 0.5 else 0)

    X = df[["tenure", "last_purchase_gap"]]
    y = df["churn"]

    # Train/Test Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Scale Data
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Train Logistic Regression Model
    model = LogisticRegression()
    model.fit(X_train_scaled, y_train)

    print("✅ Churn model trained successfully.")
    return model, scaler, X_test_scaled, y_test

# Train the model initially
churn_model, churn_scaler, X_test_scaled, y_test = train_churn_model()

def evaluate_churn_model(model, X_test_scaled, y_test):
    # Get predictions and predicted probabilities
    y_pred = model.predict(X_test_scaled)
    y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]

    # Calculate metrics
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, zero_division=0)
    recall = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    roc_auc = roc_auc_score(y_test, y_pred_proba)

    # Print evaluation metrics
    print("Model Evaluation Metrics:")
    print(f"Accuracy  : {accuracy:.4f}")
    print(f"Precision : {precision:.4f}")
    print(f"Recall    : {recall:.4f}")
    print(f"F1 Score  : {f1:.4f}")
    print(f"ROC-AUC   : {roc_auc:.4f}")

# Evaluate the model if the training was successful
if churn_model:
    evaluate_churn_model(churn_model, X_test_scaled, y_test)

def predict_and_update_churn():
    """
    Predicts churn probability for all customers and updates their churn score.
    """
    customers = Customer.objects.all()

    for customer in customers:
        tenure = (now().date() - customer.registration_date).days
        last_purchase_gap = (now().date() - customer.last_purchase_date).days if customer.last_purchase_date else 365

        features_array = np.array([[tenure, last_purchase_gap]])
        features_scaled = churn_scaler.transform(features_array)

        # Predict Churn Probability
        churn_probability = churn_model.predict_proba(features_scaled)[0][1]

        # Update Churn Score
        customer.churn_score = round(churn_probability, 2)
        customer.save()

    print("✅ Updated churn scores for all customers.")


# --------------------------
# Sales Forecasting Model (Placeholder)
# --------------------------
def forecast_sales_for_product(product):
    """
    Generates a sales forecast for a given product using its scraped data.
    The forecast is based on:
      - Extracting a base sales figure from the 'sales_volume' string.
      - Analyzing customer review sentiment from 'customers_say'.
      - Adjusting the base sales with a sentiment-based multiplier.
    
    Parameters:
        product (Product): A Product model instance.
    
    Returns:
        dict: Contains the base sales, sentiment polarity, and forecasted sales.
    """
    # --- Extract base sales from the "sales_volume" field ---
    sales_volume_str = product.sales_volume if product.sales_volume else ""
    # Use regex to extract the first number from the sales_volume string.
    numbers = re.findall(r'\d+', sales_volume_str)
    base_sales = int(numbers[0]) if numbers else 0

    # --- Sentiment Analysis on Customer Reviews ---
    review_text = product.customers_say if product.customers_say else ""
    polarity = 0.0
    if review_text:
        sentiment = TextBlob(review_text).sentiment
        polarity = sentiment.polarity  # Ranges from -1 (negative) to 1 (positive)

    # --- Forecast Calculation ---
    # For demonstration, assume the base forecast is the base_sales.
    # Adjust the forecast with sentiment: for example, each 0.1 positive polarity adds 5% to the forecast.
    # Here we use a multiplier of 0.5 for polarity adjustment.
    sentiment_adjustment_factor = 1 + (polarity * 0.5)
    forecasted_sales = base_sales * sentiment_adjustment_factor

    return {
        "base_sales": base_sales,
        "sentiment_polarity": polarity,
        "forecasted_sales": forecasted_sales
    }

def forecast_sales_for_product(product):
    """
    Generates a sales forecast for a given product using its scraped data.
    The forecast is based on:
      - Extracting a base sales figure from the 'sales_volume' string.
      - Analyzing customer review sentiment from 'customers_say'.
      - Adjusting the base sales with a sentiment-based multiplier.
    
    Parameters:
        product (Product): A Product model instance.
    
    Returns:
        dict: Contains the base sales, sentiment polarity, and forecasted sales.
    """
    # --- Extract base sales from the "sales_volume" field ---
    sales_volume_str = product.sales_volume if product.sales_volume else ""
    # Use regex to extract numeric parts
    numbers = re.findall(r'\d+', sales_volume_str)
    if numbers:
        base_sales = int(numbers[0])
        sales_volume_upper = sales_volume_str.upper()
        # Check for shorthand notation: "K" indicates thousands, "M" indicates millions.
        if "K" in sales_volume_upper:
            base_sales *= 1000
        elif "M" in sales_volume_upper:
            base_sales *= 1000000
    else:
        base_sales = 0

    # --- Sentiment Analysis on Customer Reviews ---
    review_text = product.customers_say if product.customers_say else ""
    polarity = 0.0
    if review_text:
        sentiment = TextBlob(review_text).sentiment
        polarity = sentiment.polarity  # Ranges from -1 (negative) to 1 (positive)

    # --- Forecast Calculation ---
    # For demonstration, assume the base forecast is the base_sales.
    # Adjust the forecast with sentiment: for example, each 0.1 positive polarity might add 5% to the forecast.
    # Here we use a multiplier of 0.5 for polarity adjustment.
    sentiment_adjustment_factor = 1 + (polarity * 0.5)
    forecasted_sales = base_sales * sentiment_adjustment_factor

    return {
        "base_sales": base_sales,
        "sentiment_polarity": polarity,
        "forecasted_sales": forecasted_sales
    }

def forecast_and_store_sales():
    """
    Iterates over all products, computes a sales forecast for each,
    and stores the forecast result in the SalesForecast model.
    """
    products = Product.objects.all()
    # Define the forecast date; you might choose the next month or a specific period.
    forecast_date = timezone.now().date()  
    period = "Monthly"  # or "Weekly", etc.

    for product in products:
        forecast_data = forecast_sales_for_product(product)
        predicted_sales = forecast_data["forecasted_sales"]

        # Create or update the SalesForecast record for this product and forecast date.
        forecast_record, created = SalesForecast.objects.update_or_create(
            product=product,
            forecast_date=forecast_date,
            period=period,
            defaults={"predicted_sales": predicted_sales}
        )

        print(
            f"Forecast for {product.name}: Base Sales = {forecast_data['base_sales']}, "
            f"Polarity = {forecast_data['sentiment_polarity']}, Predicted Sales = {predicted_sales}"
        )

    return "Sales forecast updated for all products."

# --------------------------
# Product Recommendation Model (Placeholder)
# --------------------------
def recommend_products(customer_id):
    """
    Returns a list of randomly recommended product names.
    """
    products = ["Smartphone", "Laptop", "Headphones", "Shoes", "Backpack", "T-Shirt", "Wristwatch"]
    recommended = random.sample(products, 3)  # Pick 3 random products
    return recommended

# --------------------------
# Dynamic Pricing Insights (Placeholder)
# --------------------------
def get_pricing_trends(product_id):
    """
    Simulates pricing trends for a given product.
    """
    base_price = round(random.uniform(100, 500), 2)
    trend = [round(base_price * random.uniform(0.9, 1.1), 2) for _ in range(5)]
    return {
        "product_id": product_id,
        "price_trends": trend,
        "suggested_price": round(sum(trend) / len(trend), 2)
    }
