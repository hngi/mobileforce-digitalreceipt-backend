from datetime import date


# https://github.com/jazzband/django-push-notifications
from apscheduler.triggers.combining import OrTrigger
from apscheduler.triggers.cron import CronTrigger
from push_notifications.models import GCMDevice, APNSDevice

from businessManagement.models import Notifications
from businessManagement.serializers import NotificationsSerializer
from userManagement.models import User
from userManagement.serializers import UserSerializer

from apscheduler.schedulers.background import BackgroundScheduler


def notificationsJob():
    try:
        notifications = Notifications.objects.get(date_to_deliver=date.today(), delivered=False)
        notifications_data = NotificationsSerializer(data=notifications, many=True).data
        for data in notifications_data:
            user = User.objects.get(id=data.user)
            users_data = UserSerializer(data=user, many=False).data
            if users_data['active']:
                if users_data['deviceType'] == 'Andriod':
                    device = GCMDevice.objects.get(registration_id=users_data['registration_id'])
                    device.send_message(data['message'])
                else:
                    device = APNSDevice.objects.get(registration_id=users_data['registration_id'])
                    device.send_message(data['message'])
                Notifications.objects.filter(registration_id=users_data['registration_id']).update(delivered=True)
    except Exception as error:
        print(error)


def start():
    scheduler = BackgroundScheduler()
    trigger = OrTrigger([
        CronTrigger(hour='23', minute='58-59'),
    ])
    # scheduler.add_job(notificationsJob, 'interval', minutes=30)
    scheduler.add_job(notificationsJob, trigger)
    scheduler.start()

