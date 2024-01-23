from django.core.management.base import BaseCommand
from addresses.models import Address

class Command(BaseCommand):
    help = 'Remove all address from the address model'

    def handle(self, *args, **options):
        try:
            Address.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Successfully removed all addresses'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
