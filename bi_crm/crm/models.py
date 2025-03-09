from django.db import models
from django.utils import timezone
import random

# -----------------------------
# Customer & Segmentation
# -----------------------------
class CustomerSegment(models.Model):
    """
    Represents a customer segment (e.g., High Value, Medium Value, Low Value)
    that can be used for targeted marketing and segmentation analysis.
    """
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.name

class Customer(models.Model):
    """
    Stores customer details along with engagement data used for churn prediction,
    customer segmentation, and personalized recommendations.
    """
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    registration_date = models.DateField(blank=True, null=True)
    last_purchase_date = models.DateField(blank=True, null=True)
    # A predicted churn score between 0 and 1 (can be updated via ML predictions)
    churn_score = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    # Link to a segmentation category
    segment = models.ForeignKey(CustomerSegment, on_delete=models.SET_NULL, blank=True, null=True, related_name='customers')
    
     # New field: Spending Factor
    spending_factor = models.DecimalField(
        max_digits=4, decimal_places=2, blank=True, null=True, 
        help_text="Random spending factor (0.5 - 1.5) assigned at creation."
    )

    def save(self, *args, **kwargs):
        """Assign a random spending factor only if it's not set."""
        if self.spending_factor is None:
            self.spending_factor = round(random.uniform(0.5, 1.5), 2)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name} (Spending Factor: {self.spending_factor})"

# -----------------------------
# Product & Pricing
# -----------------------------
class Product(models.Model):
    """
    Represents a product available for sale. Stores detailed information scraped from Amazon.
    """
    # Basic Product Info
    name = models.CharField(max_length=200)
    asin = models.CharField(max_length=20, unique=True, null=True, blank=True)  # Amazon identifier
    category = models.CharField(max_length=100, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    original_price = models.CharField(max_length=50, blank=True, null=True)  # Often includes currency symbols
    currency = models.CharField(max_length=10, blank=True, null=True)
    country = models.CharField(max_length=50, blank=True, null=True)
    
    # Product Details and Description
    description = models.TextField(blank=True, null=True)
    product_byline = models.CharField(max_length=200, blank=True, null=True)
    product_byline_link = models.URLField(blank=True, null=True)
    rating = models.FloatField(blank=True, null=True)
    product_num_ratings = models.PositiveIntegerField(null=True, blank=True)
    product_url = models.URLField(blank=True, null=True)
    product_photo = models.URLField(blank=True, null=True)
    product_num_offers = models.PositiveIntegerField(null=True, blank=True)
    product_availability = models.CharField(max_length=100, blank=True, null=True)
    
    # Flags from Amazon
    is_best_seller = models.BooleanField(default=False)
    is_amazon_choice = models.BooleanField(default=False)
    is_prime = models.BooleanField(default=False)
    climate_pledge_friendly = models.BooleanField(default=False)
    
    # Sales and Review Info
    sales_volume = models.CharField(max_length=50, blank=True, null=True)  # e.g., "400+ bought in past month"
    customers_say = models.TextField(blank=True, null=True)
    
    # Detailed Product Information stored as JSON
    product_information = models.JSONField(blank=True, null=True)  # e.g., dimensions, manufacturer, etc.
    product_details = models.JSONField(blank=True, null=True)      # Additional details like material, closure type, etc.
    
    # Media Assets
    product_photos = models.JSONField(blank=True, null=True)  # List of photo URLs
    product_videos = models.JSONField(blank=True, null=True)  # List of video dictionaries
    video_thumbnail = models.URLField(blank=True, null=True)
    has_video = models.BooleanField(default=False)
    
    # Delivery Information
    delivery = models.TextField(blank=True, null=True)
    primary_delivery_time = models.CharField(max_length=100, blank=True, null=True)
    
    # Category & Variations
    category_path = models.JSONField(blank=True, null=True)      # List of category dictionaries
    product_variations = models.JSONField(blank=True, null=True)   # Variation details (size, color, etc.)
    
    # Deal & Brand Info
    deal_badge = models.CharField(max_length=100, blank=True, null=True)
    has_aplus = models.BooleanField(default=False)
    has_brandstory = models.BooleanField(default=False)
    
    # Additional Info (if any)
    more_info = models.JSONField(blank=True, null=True)

    def __str__(self):
        return self.name


class PriceHistory(models.Model):
    """
    Tracks historical pricing data from various e-commerce platforms.
    Useful for dynamic pricing insights and trend analysis.
    """
    PLATFORM_CHOICES = (
        ('Amazon', 'Amazon'),
        ('Flipkart', 'Flipkart'),
        ('Other', 'Other'),
    )
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='price_history')
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    scraped_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.product.name} on {self.platform} @ {self.price}"

# -----------------------------
# Orders & Order Items
# -----------------------------
class Order(models.Model):
    """
    Represents a customer order. Aggregates order items and records key sales data.
    """
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    )
    order_number = models.CharField(max_length=20, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    order_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    
    def __str__(self):
        return self.order_number

class OrderItem(models.Model):
    """
    An individual item within an order, linking products to a particular order.
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    # Price of the product at the time of purchase
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.product.name} in {self.order.order_number}"

# -----------------------------
# Reviews & Sentiment
# -----------------------------
class Review(models.Model):
    """
    Customer reviews for products, including rating and sentiment analysis.
    """
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='reviews')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True, null=True)
    review_date = models.DateTimeField(auto_now_add=True)
    # Optional: A computed sentiment score (e.g., from sentiment analysis on the comment)
    sentiment_score = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    
    def __str__(self):
        return f"Review by {self.customer} for {self.product}"

# -----------------------------
# ML Predictions & Forecasts
# -----------------------------
class ChurnPrediction(models.Model):
    """
    Stores the results of churn prediction models for a customer.
    """
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='churn_predictions')
    # Predicted churn probability (0 to 1)
    churn_probability = models.FloatField()
    prediction_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Churn prediction for {self.customer} on {self.prediction_date}"

# class SalesForecast(models.Model):
#     product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="sales_forecasts")
#     forecast_date = models.DateField(help_text="Date for which the sales forecast applies")
#     predicted_sales = models.DecimalField(max_digits=12, decimal_places=2)
#     created_at = models.DateTimeField(auto_now_add=True)
#     period = models.CharField(max_length=20, help_text="Forecast period (e.g., Daily, Weekly, Monthly)")

#     def __str__(self):
#         return f"Forecast for {self.product.name} on {self.forecast_date}: {self.predicted_sales}"

class SalesForecast(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='sales_forecasts'
    )
    forecast_date = models.DateField(
        default=timezone.now,
        help_text="Date for which the sales forecast applies"
    )
    predicted_sales = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Predicted sales figure"
    )
    period = models.CharField(
        max_length=20,
        help_text="Forecast period (e.g., Daily, Weekly, Monthly)"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} forecast for {self.forecast_date}: {self.predicted_sales}"
