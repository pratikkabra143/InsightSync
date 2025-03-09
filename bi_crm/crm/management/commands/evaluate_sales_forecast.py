import math
import re
from django.core.management.base import BaseCommand
from crm.models import Product
from crm.ml_models import forecast_sales_for_product

class Command(BaseCommand):
    help = "Evaluates the sales forecast model on product data using MAE, RMSE, and MAPE."

    def handle(self, *args, **options):
        products = Product.objects.all()
        if not products.exists():
            self.stdout.write(self.style.ERROR("No product data available to evaluate."))
            return

        errors = []
        percentage_errors = []

        self.stdout.write("Evaluating sales forecast for each product...\n")

        for product in products:
            # Get forecast data using our sales forecast function.
            forecast_data = forecast_sales_for_product(product)
            base_sales = forecast_data.get("base_sales", 0)
            forecasted_sales = forecast_data.get("forecasted_sales", 0)
            error = abs(forecasted_sales - base_sales)
            errors.append(error)

            # Only calculate percentage error if base_sales > 0 to avoid division by zero.
            if base_sales > 0:
                percentage_errors.append((error / base_sales) * 100)

            self.stdout.write(
                f"{product.name} (ASIN: {product.asin}): Base Sales = {base_sales}, "
                f"Forecast = {forecasted_sales:.2f}, Error = {error:.2f}"
            )

        if errors:
            mae = sum(errors) / len(errors)
            rmse = math.sqrt(sum(e ** 2 for e in errors) / len(errors))
            mape = sum(percentage_errors) / len(percentage_errors) if percentage_errors else None

            self.stdout.write("\n" + self.style.SUCCESS("Evaluation Metrics:"))
            self.stdout.write(f"MAE  : {mae:.2f}")
            self.stdout.write(f"RMSE : {rmse:.2f}")
            if mape is not None:
                self.stdout.write(f"MAPE : {mape:.2f}%")
        else:
            self.stdout.write(self.style.WARNING("No errors computed, check the product data."))
