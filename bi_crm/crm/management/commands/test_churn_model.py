from django.core.management.base import BaseCommand
from crm.ml_models import train_churn_model, evaluate_churn_model

class Command(BaseCommand):
    help = "Trains and evaluates the churn prediction model and prints evaluation metrics."

    def handle(self, *args, **options):
        self.stdout.write("Starting training of the churn prediction model...")
        result = train_churn_model()
        
        if result[0] is None:
            self.stdout.write(self.style.ERROR("Not enough data to train the model."))
            return

        model, scaler, X_test, y_test = result
        self.stdout.write(self.style.SUCCESS("Churn model training completed successfully."))
        
        self.stdout.write("Evaluating the churn prediction model...")
        evaluate_churn_model(model, X_test, y_test)
        
        self.stdout.write(self.style.SUCCESS("Churn model evaluation complete."))
