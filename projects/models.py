from django.db import models
from teams.models import Team
from django.contrib.auth.models import User
from django.urls import reverse
# Create your models here.

class Project(models.Model):

    name = models.CharField(max_length=50)
    teams = models.ManyToManyField(Team, related_name='projects')
    manager = models.ForeignKey(User, related_name='project_manager', on_delete=models.CASCADE)

    def get_absolute_url(self): #Returns instance detail url
        return reverse("projects:projects_detail", kwargs={"id": self.id})

    def get_issues_list_url(self): #Returns instance detail url
        return reverse("issues:issues_list", kwargs={"id": self.id})

    def __str__(self):
        return 'id=%s %s' % (self.id, self.name)