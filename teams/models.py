from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

# Create your models here.
class Team(models.Model):
    name = models.CharField(max_length=50)
    members = models.ManyToManyField(User, related_name='works')
    manager = models.ForeignKey(User, on_delete=models.CASCADE, related_name='team_manager', null=True )

    def get_absolute_url(self): #returns absolute url to instance detail template
        return reverse('teams:teams_detail', kwargs={'id': self.id})

    def __str__(self):
        return 'id=%s %s' % (self.id, self.name)