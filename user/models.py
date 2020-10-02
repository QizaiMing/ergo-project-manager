from django.db import models
# Create your models here.
class UserPicture(models.Model):
    picture = models.ImageField(upload_to='media')