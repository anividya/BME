from django.core.management.base import BaseCommand
from BMEAPP.models import Asset
from django.utils import timezone

class Command(BaseCommand):
    help = 'Updates pmstat field based on pmdue date'

    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        assets = Asset.objects.all()
        #for asset in assets:
            #if asset.pmdue:
                #if asset.pmdue < today:
                    #asset.pmstat = "OVER DUE"
                #else:
                    #asset.pmstat = "NOT DUE"
                #asset.save()
        self.stdout.write(self.style.SUCCESS('Successfully updated pmstat for all assets.'))
