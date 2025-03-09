from django.core.management.base import BaseCommand
from crm.ml_models import predict_and_update_churn

class Command(BaseCommand):
    help = "Updates churn scores for all customers"

    def handle(self, *args, **kwargs):
        predict_and_update_churn()
        self.stdout.write(self.style.SUCCESS("✅ Churn scores updated successfully!"))
