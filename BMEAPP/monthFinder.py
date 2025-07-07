from datetime import datetime
from dateutil.relativedelta import relativedelta

def monthfind(date_str, interval):
    try:
        # Parse the date (HTML format is YYYY-MM-DD)
        start_date = datetime.strptime(date_str, "%Y-%m-%d")

        # Ensure interval is an integer
        interval = int(interval)

        # Generate the list of scheduled months
        months = []
        for i in range(0, 12, interval):
            scheduled_date = start_date + relativedelta(months=i)
            months.append(scheduled_date.strftime("%b").upper())  # e.g., 'JAN', 'APR'

        # Join the months into a single comma-separated string
        schedule_string = ",".join(months)
        return schedule_string

    except (ValueError, TypeError) as e:
        return None  # or handle/log the error as needed



