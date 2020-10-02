from django.shortcuts import render
from django.views.generic import ListView
from notifications.models import Notification

class NotificationsListView(ListView):
    template_name = 'notifications_list.html'

    def get_queryset(self):
        qs = Notification.objects.filter(recipient=self.request.user.id)
        qs.mark_all_as_read()
        return qs
    
