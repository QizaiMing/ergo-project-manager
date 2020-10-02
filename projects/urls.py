from django.urls import path
from .views import (
    ProjectListView,
    ProjectCreateView,
    ProjectDetailView,
    ProjectDeleteView,
    ProjectTeamsView,
    ProjectUpdateView,
    project_add_team_view,
    project_remove_team_view,
    project_update_manager_view
)
from issues.views import issue_create_view

app_name = 'projects'
urlpatterns = [
    path('', ProjectListView.as_view(), name='projects_list'),
    path('create', ProjectCreateView.as_view(), name='projects_create'),
    path('<int:id>', ProjectDetailView.as_view(), name='projects_detail'),
    path('<int:id>/teams', ProjectTeamsView.as_view(), name='projects_teams'),
    path('<int:id>/delete', ProjectDeleteView.as_view(), name='projects_delete'),
    path('<int:id>/update', ProjectUpdateView.as_view(), name='projects_update'),
    path('<int:id>/teams/add', project_add_team_view, name='projects_add_team'),
    path('<int:id>/teams/remove', project_remove_team_view, name='projects_remove_team'),
    path('<int:id>/manager', project_update_manager_view, name='projects_update_manager'),
    path('<int:id>/issues/create', issue_create_view, name='issue_create_view') #Issues related urls
]
