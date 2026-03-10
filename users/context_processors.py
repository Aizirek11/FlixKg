from notifications.models import Notification

def notifications_processor(request):
    if request.user.is_authenticated:
        unread_count = Notification.objects.filter(
            recipient=request.user, is_read=False
        ).count()
        return {'nav_unread_count': unread_count}
    return {'nav_unread_count': 0}