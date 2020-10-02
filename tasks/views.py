from django.shortcuts import render
from django.views.generic import ListView
from issues.models import Issue
from teams.models import Team
from projects.models import Project
from django.contrib.auth.models import User

def tasks_list_view(request, *args, **kwargs):
    template_name = 'tasks_list.html'
    issues = Issue.objects.filter(assignee=request.user.id).order_by('-created')
    teams = Team.objects.filter(members=request.user.id)
    filters = {
            'search': '',
            'status': False,
            'priority': False,
            'creator': False,
            'project': False
        }    
    projects = set()
    users = set()
    
    for team in teams:

        for project in team.projects.all(): #add team projects to projects set
            projects.add(project)
            users.add(project.manager)

            for t in project.teams.all():
                for member in t.members.all():
                    users.add(member)

    for proj in Project.objects.filter(manager=request.user.id): #add all projects which the user
        projects.add(proj)                                       #is manager of and add it to the set

    context = {
        'issues': issues,
        'filters': filters,
        'projects': projects,
        'users': users
    }

    if request.method == 'POST':

        if request.POST.get('filter_search'):
            search = request.POST.get('filter_search')
            issues = issues.filter(title__icontains=search)
            filters['search'] = search

        if request.POST.get('filter_status'):
            status = request.POST.get('filter_status')
            issues = issues.filter(status=status)
            filters['status'] = status

        if request.POST.get('filter_priority'):
            priority = request.POST.get('filter_priority')
            issues = issues.filter(priority=priority)
            filters['priority'] = priority

        if request.POST.get('filter_creator'):
            creator_id = request.POST.get('filter_creator')
            issues = issues.filter(creator=creator_id)
            filters['creator'] = User.objects.get(id=creator_id)

        if request.POST.get('filter_project'):
            project_id = request.POST.get('filter_project')
            issues = issues.filter(project=project_id)
            filters['project'] = Project.objects.get(id=project_id)

        context['issues'] = issues #update new issues list
        context['filters'] = filters #send updated filters

    return render(request, template_name, context)
