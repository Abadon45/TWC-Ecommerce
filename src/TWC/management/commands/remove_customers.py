from django.core.management.base import BaseCommand
from billing.models import Customer

class Command(BaseCommand):
    help = 'Remove all customers from the Customer model'

    def handle(self, *args, **options):
        try:
            Customer.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Successfully removed all customers'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
