from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),  # Home Dashboard
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/<int:id>/', views.customer_detail, name='customer_detail'),
    path('products/', views.product_list, name='product_list'),
    path('orders/', views.order_list, name='order_list'),
    path('churn-prediction/', views.churn_prediction, name='churn_prediction'),
    path('sales-forecast/', views.sales_forecast, name='sales_forecast'),
    path('recommendations/', views.product_recommendations, name='product_recommendations'),
    path('pricing-insights/', views.pricing_insights, name='pricing_insights'),  # New URL for pricing insights

]
