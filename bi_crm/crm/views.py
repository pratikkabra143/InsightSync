from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Customer, Product, Order
from .ml_models import predict_and_update_churn, forecast_and_store_sales, recommend_products, get_pricing_trends

# Dashboard View
def dashboard(request):
    return render(request, 'crm/dashboard.html')

# Customers
def customer_list(request):
    customers = Customer.objects.all()
    return render(request, 'crm/customers.html', {'customers': customers})

def customer_detail(request, id):
    customer = get_object_or_404(Customer, id=id)
    return JsonResponse({'customer': {'name': f"{customer.first_name} {customer.last_name}", 'email': customer.email}})

# Products
def product_list(request):
    products = Product.objects.all()
    return render(request, 'crm/products.html', {'products': products})

# Orders
def order_list(request):
    orders = Order.objects.all()
    return render(request, 'crm/orders.html', {'orders': orders})

# Churn Prediction View
def churn_prediction(request):
    customer_id = request.GET.get("customer_id", 1)  # Default customer ID if not provided
    churn_score = predict_churn(customer_id)
    return JsonResponse({'customer_id': customer_id, 'churn_score': churn_score})

# Sales Forecasting View
def sales_forecast(request):
    forecast = forecast_sales()
    return JsonResponse(forecast)

# Product Recommendation View
def product_recommendations(request):
    customer_id = request.GET.get("customer_id", 1)  # Default customer ID if not provided
    recommendations = recommend_products(customer_id)
    return JsonResponse({'customer_id': customer_id, 'recommended_products': recommendations})

# Pricing Insights View
def pricing_insights(request):
    product_id = request.GET.get("product_id", 1)  # Default product ID if not provided
    pricing_data = get_pricing_trends(product_id)
    return JsonResponse(pricing_data)
