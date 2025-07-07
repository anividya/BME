from datetime import datetime
from dateutil.relativedelta import relativedelta
import calendar

def next_ppmMonth(donedate, ppmmonths):

    if isinstance(donedate, str):
        try:
            date_obj = datetime.strptime(donedate, "%Y-%m-%dT%H:%M")
        except ValueError:
            date_obj = datetime.strptime(donedate, "%Y-%m-%d")
    else:
        date_obj = donedate

    pm_months = [month.strip().upper() for month in ppmmonths.split(",")]
    # Convert month abbreviations to numbers
    month_abbr_to_num = {
        'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4, 'MAY': 5, 'JUN': 6,
        'JUL': 7, 'AUG': 8, 'SEP': 9, 'OCT': 10, 'NOV': 11, 'DEC': 12
    }
    pm_month_nums = sorted([month_abbr_to_num[m] for m in pm_months])

    # Current month and year
    curr_month = date_obj.month
    curr_year = date_obj.year

    # Find the next PM month
    for m in pm_month_nums:
        if m > curr_month:
            next_month = m
            break
    else:
        next_month = pm_month_nums[0]
        curr_year += 1

    # Get the last day of the target month
    last_day_of_target_month = calendar.monthrange(curr_year, next_month)[1]

    # Final PM due date as the last day of the selected month
    new_pmdate = datetime(curr_year, next_month, last_day_of_target_month)
    return new_pmdate.strftime("%Y-%m-%d")


def next_ppmMonthview(donedate, ppmmonths):
    if isinstance(donedate, str):
        try:
            date_obj = datetime.strptime(donedate, "%Y-%m-%dT%H:%M")
        except ValueError:
            try:
                date_obj = datetime.strptime(donedate, "%Y-%m-%d")
            except ValueError:
                date_obj = datetime.strptime(donedate, "%Y-%m-%d %H:%M:%S")
    else:
        date_obj = donedate

    pm_months = [month.strip().upper() for month in ppmmonths.split(",")]
    month_abbr_to_num = {
        'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4, 'MAY': 5, 'JUN': 6,
        'JUL': 7, 'AUG': 8, 'SEP': 9, 'OCT': 10, 'NOV': 11, 'DEC': 12
    }
    pm_month_nums = sorted([month_abbr_to_num[m] for m in pm_months])

    curr_month = date_obj.month
    curr_year = date_obj.year

    if curr_month in pm_month_nums:
        last_day_curr = calendar.monthrange(curr_year, curr_month)[1]
        candidate_end = datetime(curr_year, curr_month, last_day_curr, 23, 59, 59)
        if candidate_end > date_obj:
            new_pmdate = datetime(curr_year, curr_month, last_day_curr)
            return new_pmdate.strftime("%Y-%m-%d")

    for m in pm_month_nums:
        if m > curr_month:
            next_month = m
            next_year = curr_year
            break
    else:
        next_month = pm_month_nums[0]
        next_year = curr_year + 1

    last_day_of_target_month = calendar.monthrange(next_year, next_month)[1]
    new_pmdate = datetime(next_year, next_month, last_day_of_target_month)
    return new_pmdate.strftime("%Y-%m-%d")
# Example usage
ppmmonths = 'FEB,JUL,DEC'
donedate = 	'2025-07-29T12:58'
pmdue = next_ppmMonth(donedate, ppmmonths)
print(pmdue)  # Output: 2025-11-30
