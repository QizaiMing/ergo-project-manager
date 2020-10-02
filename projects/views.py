from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    CreateView,
    DetailView,
    DeleteView,
    UpdateView
)
from .models import Project
from .forms import ProjectForm
from teams.models import Team
from django.contrib.auth.models import User
from issues.models import Issue
from notifications.signals import notify
# Create your views here.

class ProjectListView(ListView):
    template_name = 'projects_list.html'
    
    def get_queryset(self):
        user = self.request.user
        teams = Team.objects.filter(members=User.objects.get(id=user.id)) #Get all teams with the current user as a member
        projects = set() #New empty set object, sets can not have duplicates

        for t in teams: #For every team, gets all projects and dumps them into a set
            for p in t.projects.all():
                projects.add(p)

        projects_manager = set(Project.objects.filter(manager=User.objects.get(id=user.id))) #Get all projects where the user is manager and turns them into a set
        return projects.union(projects_manager) #Combine both sets of projects (member of a team thats is a project and projects that the user is manager)

class ProjectCreateView(CreateView):
    template_name = 'projects_create.html'
    success_url = reverse_lazy('projects:projects_list')
    form_class = ProjectForm

    def form_valid(self, form):
        if self.request.user.id == 9:
            return redirect('/projects')
        manager = self.request.user
        form.instance.manager = User.objects.get(id=manager.id) #Make user the project manager
        form.save()
        return super().form_valid(form)

class ProjectTeamsView(DetailView):
    template_name = 'projects_detail_teams.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        id_ = self.kwargs.get('id')
        p = Project.objects.get(id=id_)
        context['teams'] = p.teams.all() #Get all teams whithin the project
        return context

    def get_object(self):
        id_ = self.kwargs.get('id')
        return get_object_or_404(Project, id=id_)

class ProjectDetailView(DetailView):
    template_name = 'projects_detail.html'
    model = Issue

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        id_ = self.kwargs.get('id')
        i = Issue.objects.filter(project=id_)
        context['to_do'] = i.filter(status='To Do')
        context['in_progress'] = i.filter(status='In Progress')
        context['done'] = i.filter(status='Done').order_by('-created')[:5]
        return context
    

    def get_object(self):
        id_ = self.kwargs.get('id')
        return get_object_or_404(Project, id=id_)

class ProjectDeleteView(DeleteView):
    template_name = 'projects_delete.html'
    model = Project
    success_url = reverse_lazy('projects:projects_list')

    def get_object(self):        
        id_ = self.kwargs.get('id')
        return get_object_or_404(Project, id=id_)

    def post(self, request, *args, **kwargs):
        id_ = self.kwargs.get('id')
        if self.request.user.id == 9:
            return redirect('/projects/%s' % (id_))       
        project = Project.objects.get(id=id_)
        project_members = set()

        for team in project.teams.all():
            for member in team.members.all():
                project_members.add(member)
        
        project_members.add(project.manager)

        notify.send(sender=self.request.user, recipient=list(project_members),
                verb='Your project %s was deleted' % (project.name), action_object=project)
        return self.delete(request, *args, **kwargs)

class ProjectUpdateView(UpdateView):
    template_name = 'projects_create.html'
    form_class = ProjectForm

    def get_object(self):
        id_ = self.kwargs.get('id')
        return get_object_or_404(Project, id=id_)

    def form_valid(self, form):
        id_ = self.kwargs.get('id')
        if self.request.user.id == 9:
            return redirect('/projects/%s' % (id_))
        project = Project.objects.get(id=id_)
        project_members = set()

        for team in project.teams.all():
            for member in team.members.all():
                project_members.add(member)
        
        project_members.add(project.manager)

        notify.send(sender=self.request.user, recipient=list(project_members),
                verb='Your project name was updated', action_object=project, description=project.get_absolute_url())
        return super().form_valid(form)

def project_add_team_view(request, *args, **kwargs):
    template_name = 'projects_add_team.html'
    id_ = kwargs.get('id')
    teams = Team.objects.exclude(projects=id_) #Get all teams that are not part of the project
    project = Project.objects.get(id=id_)# Get current project object
    context = {
        'teams': teams,
        'project': project
    }

    if request.method == 'POST' and request.user.id is not 9: #Get form data
        new_team = Team.objects.get(id=request.POST.get('team_id')) #Get team sent by the form
        project.teams.add(new_team)
        teams = Team.objects.exclude(projects=id_) #Refresh context
        notify.send(sender=request.user, recipient=new_team.members.all(),
                     verb='Your team %s was added to a new project' % (new_team.name), action_object=new_team,
                     target=project, description=project.get_absolute_url())

        context = {
            'teams': teams,
            'project': project
        }
        return render(request, template_name, context)

    return render(request, template_name, context)

def project_remove_team_view(request, *args, **kwargs):
    template_name = 'projects_remove_team.html'
    id_ = kwargs.get('id')
    project = Project.objects.get(id=id_) #Get current project object
    teams = Team.objects.filter(projects=id_) #Get all teams whithin the project
    
    context = {
        'teams': teams,
        'project': project
    }

    if request.method == 'POST' and request.user.id is not 9: #Get form data
        ex_team = Team.objects.get(id=request.POST.get('team_id')) #Get team sent by the form
        project.teams.remove(ex_team)
        teams = Team.objects.filter(projects=id_) #Refresh context
        notify.send(sender=request.user, recipient=ex_team.members.all(),
                     verb='Your team %s was removed from %s' % (ex_team.name, project.name), action_object=ex_team,
                     target=project)

        context = {
            'teams': teams,
            'project': project
        }
        return render(request, template_name, context)

    return render(request, template_name, context)

def project_update_manager_view(request, *args, **kwargs):
    template_name = 'projects_update_manager.html'
    id_ = kwargs.get('id')
    project = Project.objects.get(id=id_) #Get current project object
    users = User.objects.exclude(id=project.manager.id) #Get all users except the current project manager
    context = {
        'users': users,
        'project': project
    }

    if request.method == 'POST' and request.user.id is not 9: #Get form data
        new_manager = User.objects.get(id=request.POST.get('user_id')) #Get user sent by form
        project.manager = new_manager
        project.save()
        notify.send(sender=request.user, recipient=new_manager,
                     verb='You are the new project manager of %s' % (project.name), action_object=project,
                     description=project.get_absolute_url())

        return redirect('/projects/%s' % (project.id)) #Redirect to project detail URL

    return render(request, template_name, context)