from decouple import config
from datetime import datetime
import requests
from .models import Holiday, BusManagement
from dateutil.relativedelta import relativedelta


def add_holidays():
    """
    adding public holidays cron
    :return:
    """
    today = datetime.now()
    print(' cron stated', today)
    api_key = config('CALENDARIFIC_API_KEY')
    request_url = 'https://calendarific.com/api/v2/holidays?api_key=%sf&country=BM&year=%s' % (api_key, today.year)
    response = requests.get(request_url)
    response = response.json()
    data = response['response']
    if 'holidays' in data:
        holidays = data['holidays']
        for holiday in holidays:
            dates = holiday['date']['iso'].split('T')
            Holiday.objects.create(
                name=holiday['name'],
                holiday_date=dates[0],
                description=holiday['description'],
                is_public_holiday=True if 'National holiday' in holiday['type'] else False,
                holiday_type=holiday['type'][0],
            )
    print(' cron stated', today)


def change_licence_date():
    """
    Change the year of date after that is todays date
    :return:
    """
    today = datetime.now()
    bus = BusManagement.objects.filter(vehicle_licensing=today.date())
    for b in bus:
        b.vehicle_licensing = b.vehicle_licensing + relativedelta(years=+1)
        b.save()
    print(' cron stated', today)