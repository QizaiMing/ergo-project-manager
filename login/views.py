from django.shortcuts import render, redirect
from dashboard.views import dashboard_view

#logout related imports
from django.contrib.auth import logout as log_out
from django.conf import settings
from django.http import HttpResponseRedirect
from urllib.parse import urlencode

# Create your views here.

def home_view(request, *args, **kwargs):#if user is logged show dashboard, else show home
    user = request.user
    if user.is_authenticated:
        return redirect(dashboard_view)
    else:
        return render(request, 'home.html')

def login_view(request, *args, **kwargs): #my own pre-auth0 login view
    template_name = 'login.html'
    return render(request, template_name)

def logout_view(request): #handles logout button action
    log_out(request)
    return_to = urlencode({'returnTo': request.build_absolute_uri('/')})
    logout_url = 'https://%s/v2/logout?client_id=%s&%s' % \
                 (settings.SOCIAL_AUTH_AUTH0_DOMAIN, settings.SOCIAL_AUTH_AUTH0_KEY, return_to)
    return HttpResponseRedirect(logout_url)



