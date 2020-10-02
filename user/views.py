from django.shortcuts import render, redirect
import json
import http.client #used for calling auth0 management api
from .models import UserPicture
from .forms import UserPictureForm
from filestack import Client, Filelink #filestack api used for uploading profile picture to CDN and transforming
from django.contrib.auth.models import User
from issues.models import Issue
from projects.models import Project

# Create your views here.

def user_update_picture(request, *args, **kwargs): #upload and update a new profile picture
    template_name = 'update_profile_picture.html'

    user = request.user
    auth0user = user.social_auth.get(provider='auth0')
    context = {}
    if request.method == 'POST' and request.user.id is not 9: #retrieve form data
        form = UserPictureForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            filename = request.FILES['picture'].name
            filelink = upload_picture(filename) #sends the picture to filestack api
            user.picture = filelink #saves it
            user.save()

            token = get_access_token()
            uid = auth0user.uid
            body = {
                "picture": filelink
            }#body that will be sent to auth0 management api
        
            response = update_user_data(token, uid, body) #updates user data on auth0 and returns a response with the new body
            return redirect('/profile')
    
    return render(request, template_name, context)

def user_update_profile(request, *args, **kwargs): #update new user data
    template_name = 'profile.html'

    user = request.user
    auth0user = user.social_auth.get(provider='auth0')
    issues = Issue.objects.filter(assignee=user.id).order_by('-created')[:5]
    teams = user.works.all()[:3]
    projects = set()

    for team in teams:
        for project in team.projects.all():
            projects.add(project)

    for p in user.project_manager.all():
        projects.add(p)

    context = {
        'issues': issues,
        'teams': teams,
        'projects': list(projects)[:3]
    }

    if request.method == 'POST' and request.user.id is not 9: #retrieving form data
        user.first_name = request.POST.get('display_name')
        user.job_title = request.POST.get('job_title')
        user.department = request.POST.get('department')
        user.location = request.POST.get('location')
        user.teams = request.POST.get('teams')
        user.save()

        token = get_access_token()
        uid = auth0user.uid
        body = {
            "name": request.POST.get('display_name')
        }
        
        response = update_user_data(token, uid, body) #response from api

    return render(request, template_name, context)


def get_access_token(): #gets access token for the management api (AUTH0 TOKEN API)
    conn = http.client.HTTPSConnection("APP DOMAIN")

    payload = "{\"client_id\":\"CLIENT ID\",\"client_secret\":\"CLIENT SECRET\",\"audience\":\"https://APP DOMAIN/api/v2/\",\"grant_type\":\"client_credentials\"}"

    headers = { 'content-type': "application/json" }

    conn.request("POST", "/oauth/token", payload, headers)

    res = conn.getresponse()
    data = res.read()
    decoded = data.decode("utf-8")
    datadict = json.loads(decoded)

    return datadict["access_token"] #returns access token (str)

# def get_user_profile(token, uid, field): #access token, user id, field you want to retrieve

#     conn = http.client.HTTPSConnection("ergoauth.auth0.com")

#     headers = {
#         'content-type': "application/json",
#         'authorization': "Bearer %s" % token
#         }

#     conn.request("GET", "/api/v2/users/%s?fields=%s" % (uid,field), headers=headers)

#     res = conn.getresponse()
#     data = res.read()
#     decoded_data = data.decode("utf-8")

#     return json.loads(decoded_data) #returns user_metadata dictionary

def update_user_data(token, uid, body): #access token, user id, body to be updated (AUTH0 MANAGEMENT API)

    conn = http.client.HTTPSConnection("APP DOMAIN")
    headers = {
        'content-type': "application/json",
        'authorization': "Bearer %s" % token
        }

    conn.request("PATCH", "/api/v2/users/%s" % uid, json.dumps(body), headers=headers)

    res = conn.getresponse()
    data = res.read()
    decoded_data = data.decode("utf-8")
    return json.loads(decoded_data) #(dict)

def upload_picture(name): #uploads user picture to filestackcdn and returns a 500x500 img (FILESTACK API)
    client = Client('API KEY')

    filelink = client.upload(filepath='media/%s' % name)
    handle = Filelink(filelink.handle)
    new_filelink = handle.resize(width=500, height=500).store()
    return new_filelink.url #return link of the new file uploaded (str)
