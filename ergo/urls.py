"""ergo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from login.views import home_view, login_view, logout_view
from dashboard.views import dashboard_view, dashboard_list_view, dashboard_detail_view
from user.views import user_update_profile, user_update_picture
from notifies.views import NotificationsListView
import notifications.urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('dashboard', dashboard_view, name='dashboard_view'),
    path('dashboard/list', dashboard_list_view, name='dashboard_list'),
    path('dashboard/detail/<str:filter>', dashboard_detail_view, name='dashboard_detail'),
    path('tasks/', include('tasks.urls')),
    path('profile', user_update_profile),
    path('picture', user_update_picture),
    path('teams/', include('teams.urls')),
    path('projects/', include('projects.urls')),
    path('issues/', include('issues.urls')),
    path('notifications', NotificationsListView.as_view(), name='notifications_list'),
    path('^inbox/notifications/', include(notifications.urls, namespace='notifications')),
    path('', include('login.urls'))
]
