from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    CreateView,
    DetailView,
    DeleteView,
    UpdateView)
from .models import Team
from .forms import TeamForm
from django.contrib.auth.models import User
from notifications.signals import notify
# Create your views here.

class TeamListView(ListView):
    template_name = 'teams_list.html'
    def get_queryset(self):
        user = self.request.user
        return Team.objects.filter(members=User.objects.get(id=user.id)) #Return all teams where the user is member

class TeamCreateView(CreateView):
    template_name = 'teams_create.html'
    success_url = reverse_lazy('teams:teams_list')
    form_class = TeamForm

    def form_valid(self, form):
        if self.request.user.id == 9:
            return redirect('/teams')
        manager = self.request.user
        form.instance.manager = User.objects.get(id=manager.id) #Makes Team Manager the user creating the new team
        form.save()
        form.instance.members.add(User.objects.get(id=manager.id)) #Adds the current user to the list of team members
        return super().form_valid(form) #I don't understand this
    

class TeamDetailView(DetailView):
    template_name = 'teams_detail.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the team members
        user = self.request.user
        id_ = self.kwargs.get('id')
        t = Team.objects.get(id=id_)
        context['members'] = t.members.all()
        context['user_member'] = t.members.filter(id=user.id) #Used for validating if the user is a member of the team he is checking
        return context

    def get_object(self):
        id_ = self.kwargs.get('id')
        return get_object_or_404(Team, id=id_)

class TeamDeleteView(DeleteView):
    template_name = 'teams_delete.html'
    model = Team
    success_url = reverse_lazy('teams:teams_list')

    def get_object(self):
        id_ = self.kwargs.get('id')
        return get_object_or_404(Team, id=id_)

    def post(self, request, *args, **kwargs):
        id_ = self.kwargs.get('id') 
        if self.request.user.id == 9:
            return redirect('/teams/%s' % (id_))
               
        team = Team.objects.get(id=id_)
        notify.send(sender=self.request.user, recipient=team.members.all(),
                verb='Your team %s was deleted' % (team.name), action_object=team)
        return self.delete(request, *args, **kwargs)

class TeamUpdateView(UpdateView):
    template_name = 'teams_update.html'
    form_class = TeamForm

    def get_object(self):
        id_ = self.kwargs.get('id')
        return get_object_or_404(Team, id=id_)

    def form_valid(self, form):
        id_ = self.kwargs.get('id')
        if self.request.user.id == 9:
            return redirect('/teams/%s' % (id_))
        
        team = Team.objects.get(id=id_)
        notify.send(sender=self.request.user, recipient=team.members.all(),
                verb='Your team name was updated', action_object=team, description=team.get_absolute_url())
        return super().form_valid(form)


########
#THESE ARE FUNCTION BASED VIEWS BECAUSE THEY MIX LIST/UPDATE/DELETE
########

def team_add_member_view(request, *args, **kwargs):
    template_name = 'teams_add_member.html'
    id_ = kwargs.get('id')
    users = User.objects.exclude(works=id_) #Get all members that are not part of the team
    team = Team.objects.get(id=id_)
    context = {
        'users': users,
        'team': team
    }

    if request.method == 'POST' and request.user.id is not 9: #Get form data
        new_member = User.objects.get(id=request.POST.get('user_id')) #Get the user sent by the form
        team.members.add(new_member)
        users = User.objects.exclude(works=id_) #Refresh the old queryset
        notify.send(sender=request.user, recipient=new_member,
                    verb='You have been added to a new team', action_object=team, description=team.get_absolute_url())

        context = {
            'users': users,
            'team': team
        }
        return render(request, template_name, context)

    return render(request, template_name, context)

def team_remove_member_view(request, *args, **kwargs):
    template_name = 'teams_remove_member.html'
    id_ = kwargs.get('id')
    team = Team.objects.get(id=id_)
    users = User.objects.filter(works=id_).exclude(id=team.manager.id) #Get all the team members except the team manager
    context = {
        'users': users,
        'team': team
    }

    if request.method == 'POST' and request.user.id is not 9: #Get form data
        ex_member = User.objects.get(id=request.POST.get('user_id')) #Get user sent by the form
        team.members.remove(ex_member)
        users = User.objects.filter(works=id_).exclude(id=team.manager.id) #Refresh the old queryset
        notify.send(sender=request.user, recipient=ex_member,
                    verb='You have been removed from %s' % (team.name), action_object=team)

        context = {
            'users': users,
            'team': team
        }
        return render(request, template_name, context)
        
    return render(request, template_name, context)

def team_update_manager_view(request, *args, **kwargs):
    template_name = 'teams_update_manager.html'
    id_ = kwargs.get('id')
    team = Team.objects.get(id=id_)
    users = User.objects.filter(works=id_).exclude(id=team.manager.id) #Get all team members except the team manager
    context = {
        'users': users,
        'team': team
    }

    if request.method == 'POST' and request.user.id is not 9: #Get form data
        new_manager = User.objects.get(id=request.POST.get('user_id')) #Get user sent by the form
        team.manager = new_manager
        team.save()
        notify.send(sender=request.user, recipient=new_manager,
        verb='You are the new manager of %s' % (team.name), action_object=team, description=team.get_absolute_url())
        
        return redirect('/teams/%s' % (team.id)) #redirect to the team detail template

    return render(request, template_name, context)

def team_leave_member_view(request, *args, **kwargs):
    template_name = 'teams_leave.html'
    id_ = kwargs.get('id')
    team = Team.objects.get(id=id_)
    context = {
        'team': team
    }

    if request.method == 'POST' and request.user.id is not 9: #Get form data
        ex_member = User.objects.get(id=request.POST.get('user_id')) #Get user sent by the form
        team.members.remove(ex_member)
        context = {
            'team': team
        }
        return redirect('/teams') #redirect to the teams list template

    return render(request, template_name, context)
