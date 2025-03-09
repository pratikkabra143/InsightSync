from django.core.management.base import BaseCommand
from crm.ml_models import generate_initial_churn_scores

class Command(BaseCommand):
    help = "Updates churn scores for all customers"

    def handle(self, *args, **kwargs):
        generate_initial_churn_scores()
        self.stdout.write(self.style.SUCCESS("✅ Churn scores updated successfully!"))
