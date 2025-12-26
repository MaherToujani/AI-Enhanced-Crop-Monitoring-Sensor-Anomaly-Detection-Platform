"""
Django management command to evaluate ML model performance.

Usage:
    python manage.py evaluate_model --plot-id 1 --readings 100 --anomaly-ratio 0.2
"""

from django.core.management.base import BaseCommand
from farms.models import FieldPlot
from ml_module.test_harness import run_evaluation_test


class Command(BaseCommand):
    help = 'Evaluate ML model performance using synthetic test data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--plot-id',
            type=int,
            default=1,
            help='ID of the plot to use for testing',
        )
        parser.add_argument(
            '--readings',
            type=int,
            default=100,
            help='Number of sensor readings to generate',
        )
        parser.add_argument(
            '--anomaly-ratio',
            type=float,
            default=0.2,
            help='Ratio of readings that should be anomalies (0.0-1.0)',
        )

    def handle(self, *args, **options):
        plot_id = options['plot_id']
        num_readings = options['readings']
        anomaly_ratio = options['anomaly_ratio']

        try:
            plot = FieldPlot.objects.get(id=plot_id)
        except FieldPlot.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Plot with ID {plot_id} does not exist.')
            )
            return

        self.stdout.write(
            self.style.SUCCESS(f'Starting evaluation for plot: {plot.name}')
        )

        metrics = run_evaluation_test(plot, num_readings, anomaly_ratio)

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Evaluation complete!\n'
                f'   Precision: {metrics.precision:.4f}\n'
                f'   Recall: {metrics.recall:.4f}\n'
                f'   F1-Score: {metrics.f1_score:.4f}'
            )
        )


