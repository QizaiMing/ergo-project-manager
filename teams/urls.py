from django.urls import path
from .views import (
    TeamListView,
    TeamCreateView,
    TeamDetailView,
    TeamDeleteView,
    TeamUpdateView,
    team_add_member_view,
    team_remove_member_view,
    team_update_manager_view,
    team_leave_member_view)

app_name = 'teams'
urlpatterns = [
    path('', TeamListView.as_view(), name='teams_list'),
    path('create', TeamCreateView.as_view(), name='teams_create'),
    path('<int:id>', TeamDetailView.as_view(), name='teams_detail'),
    path('<int:id>/delete', TeamDeleteView.as_view(), name='teams_delete'),
    path('<int:id>/update', TeamUpdateView.as_view(), name='teams_update'),
    path('<int:id>/add', team_add_member_view, name='teams_add_member'),
    path('<int:id>/remove', team_remove_member_view, name='teams_remove_member'),
    path('<int:id>/manager', team_update_manager_view, name='teams_update_manager'),
    path('<int:id>/leave', team_leave_member_view, name='teams_leave_member')

]