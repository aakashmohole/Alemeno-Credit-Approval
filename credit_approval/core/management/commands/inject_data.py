from django.core.management.base import BaseCommand
from core.tasks import ingest_initial_data_task

class Command(BaseCommand):
    help = 'Injects customer and loan data from Excel files using background task'

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting background data ingestion...")
        task = ingest_initial_data_task.delay()
        self.stdout.write(self.style.SUCCESS(f"Task triggered with ID: {task.id}"))
        self.stdout.write("Check Celery logs for progress.")
