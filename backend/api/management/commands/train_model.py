from django.core.management.base import BaseCommand
from sklearn.linear_model import LogisticRegression
from processing.models import EvaluationData
import numpy as np

class Command(BaseCommand):
    help = 'Train the recommendation model'

    def handle(self, *args, **kwargs):
        data = EvaluationData.objects.all()
        X = np.array([eval_data.features for eval_data in data])
        y = np.array([eval_data.kept for eval_data in data])

        model = LogisticRegression()
        model.fit(X, y)

        # You can save the model or use it directly
        print("Model trained with coefficients:", model.coef_)