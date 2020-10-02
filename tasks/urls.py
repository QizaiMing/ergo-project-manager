from django.urls import path
from .views import (
    tasks_list_view)

app_name = 'tasks'
urlpatterns = [
    path('', tasks_list_view, name='tasks_list_view')
]