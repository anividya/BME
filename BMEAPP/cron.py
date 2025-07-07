from django_cron import CronJobBase, Schedule
from .models import Asset
from django.utils import timezone

class UpdatePmStatJob(CronJobBase):
    RUN_AT_TIMES = ['00:01']  # Daily at 1 AM

    schedule = Schedule(run_at_times=RUN_AT_TIMES)
    code = 'BMEAPP.update_pmstat'    # Unique ID

    def do(self):
        today = timezone.now().date()
        #for asset in Asset.objects.all():
            #if asset.pmdue:
                #if asset.pmdue < today:
                    #asset.pmstat = "Due"
                #else:
                    #asset.pmstat = "Not Due"
                #asset.save()
