from django.shortcuts import render
from issues.models import Issue

#login related imports
from django.contrib.auth.decorators import login_required
# Create your views here.
@login_required
def dashboard_view(request, *args, **kwargs): #handles dashboard sidebar
    template_name = 'dashboard.html'
    user = request.user
    context = {}

    return render(request, template_name, context)

def dashboard_list_view(request, *args, **kwargs): #shows user data on dashboard content page
    template_name = 'dashboard_list.html'
    issues = Issue.objects.filter(assignee=request.user.id)
    todo = issues.filter(status='To Do').count
    inprogress = issues.filter(status='In Progress').count
    done = issues.filter(status='Done').count
    low = issues.filter(priority='Low').count
    medium = issues.filter(priority='Medium').count
    high = issues.filter(priority='High').count

    context = {
        'todo': todo,
        'inprogress': inprogress,
        'done': done,
        'low': low,
        'medium': medium,
        'high': high
    }

    return render(request, template_name, context)

def dashboard_detail_view(request, *args, **kwargs):
    template_name = 'dashboard_detail.html'
    issues = Issue.objects.filter(assignee=request.user.id).order_by('-created')
    issues_by_status = issues.filter(status=kwargs.get('filter'))
    issues_by_priority = issues.filter(priority=kwargs.get('filter'))
    issues = issues_by_status | issues_by_priority

    context = {
        'issues': issues
    }
    return render(request, template_name, context)