from django.urls import path, include
from .views import home_view, login_view, logout_view

urlpatterns = [
    path('', home_view),
    path('logout/', logout_view),
    path('access', login_view),
    path('', include('django.contrib.auth.urls')),
    path('', include('social_django.urls'))
]