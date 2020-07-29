# from datetime import date, datetime
#
# # https://github.com/jazzband/django-push-notifications
# from apscheduler.triggers.combining import OrTrigger
# from apscheduler.triggers.cron import CronTrigger
# from fcm_django.models import FCMDevice
#
# from businessManagement.models import Notifications
# from businessManagement.serializers import NotificationsSerializer
# from userManagement.models import User
# from userManagement.serializers import UserSerializer
#
# from apscheduler.schedulers.background import BackgroundScheduler
#
#
# def notificationsJob():
#     try:
#         fcm_device = FCMDevice.objects.create(
#             type='andriod',
#             registration_id="d0lCz617Szuo8otAoUul5N:APA91bHWtKAP05Iymke0kmPBp7c1ehM"
#                             "-AHrUrE43J_BJIyraUaAbzt4DysVlrH5j12axa0LXwl5eCkWpu5L_rkSgan0B526_cyvVHhJqcr"
#                             "-HFtw5CQUqVyl7eOu5FvMYx2O-GP81dBV6")
#         fcm_device.send_message(title="Title", body="Message", data={"test": "test"})
#         notifications = Notifications.objects.filter(date_to_deliver__year=datetime.now().date().year,
#                                                      date_to_deliver__month=datetime.now().date().month,
#                                                      date_to_deliver__day=datetime.now().date().day,
#                                                      date_to_deliver__hour=datetime.now().time().hour,
#                                                      date_to_deliver__minute=datetime.now().time().minute,
#                                                      delivered=False)
#         notifications_data = NotificationsSerializer(notifications, many=True).data
#         print(notifications_data)
#         for data in notifications_data:
#             user = User.objects.get(id=data['user'])
#             users_data = UserSerializer(data=user, many=False).data
#             if users_data['active']:
#                 fcm_device = FCMDevice.objects.get(
#                     type=users_data['deviceType'],
#                     registration_id=users_data['registration_id'])
#                 message = data['message']
#                 message["click_action"] = "FLUTTER_NOTIFICATION_CLICK";
#                 fcm_device.send_message(title=data['title'], body=data['message'],
#                                         data=message)
#                 Notifications.objects.filter(registration_id=users_data['registration_id']).update(delivered=True)
#     except Exception as error:
#         print(error)
#
#
# def start():
#     scheduler = BackgroundScheduler()
#     # trigger = OrTrigger([
#     #     CronTrigger(hour='23', minute='59-59'),
#     # ])
#     once_per_minute = CronTrigger('*', '*', '*', '*', '*', '*', '*', '0')
#     scheduler.add_job(notificationsJob, trigger=once_per_minute)
#     # scheduler.add_job(notificationsJob, trigger)
#     scheduler.start()
