from django.db import models
from django.contrib.auth.models import User
from projects.models import Project
from django.urls import reverse
# Create your models here.
class Issue(models.Model):


    TO_DO = 'To Do'
    IN_PROGRESS = 'In Progress'
    DONE = 'Done'
    #Set status list with all choices in it
    STATUS = [
        (TO_DO, 'To Do'),
        (IN_PROGRESS, 'In Progress'),
        (DONE, 'Done')
    ]

    LOW = 'Low'
    MEDIUM = 'Medium'
    HIGH = 'High'
    #Set priority list with all choices in it
    PRIORITY = [
        (LOW, 'Low'),
        (MEDIUM, 'Medium'),
        (HIGH, 'High')
    ]

    

    title = models.CharField(max_length=100)
    description = models.TextField(max_length=2000, blank=True)
    creator = models.ForeignKey(User, related_name='issues', on_delete=models.CASCADE)
    assignee = models.ForeignKey(User, related_name='assigned_to', on_delete=models.CASCADE, blank=True, null=True)
    created = models.DateTimeField(auto_now=False, auto_now_add=True)
    modified = models.DateTimeField(auto_now=True, auto_now_add=False)
    status = models.CharField(max_length=20, choices=STATUS, default=TO_DO)
    priority = models.CharField(max_length=20, choices=PRIORITY, default=LOW)
    project = models.ForeignKey(Project, related_name='issues', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return 'id=%d - %s' % (self.id, self.title)

    def get_absolute_url(self):
        return reverse("issues:issues_detail", kwargs={"id": self.id})

    def compressed_title(self):
        if len(self.title) > 30:
            return '%s...' % (self.title[:30])
        else:
            return self.title


class Comment(models.Model):

    creator = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now=False, auto_now_add=True)
    content = models.TextField(max_length=1000)
    issue = models.ForeignKey(Issue, related_name='comments', on_delete=models.CASCADE)

    def __str__(self):
        return '%s... created by: %s issue_id:%d' % (self.content[:14], self.creator, self.issue.id)

class Attachment(models.Model):

    file = models.FileField(upload_to='media/files', max_length=100)
    issue = models.ForeignKey(Issue, related_name='attachments', on_delete=models.CASCADE)

    def __str__(self):
        return self.file.name.split('/')[2] #returns file handle name

class Link(models.Model):

    BLOCKS = 'Blocks'
    BLOCKED_BY = 'Blocked By'
    RELATES_TO = 'Relates To'
    #Set link type list with all choices in it
    LINK_TYPE = [
        (BLOCKS, 'Blocks'),
        (BLOCKED_BY, 'Blocked By'),
        (RELATES_TO, 'Relates To')
    ]

    parent_issue = models.ForeignKey(Issue, related_name='links_to', on_delete=models.CASCADE, null=True)
    kind = models.CharField(choices=LINK_TYPE, max_length=50, blank=True)
    child_issue = models.ForeignKey(Issue, related_name='linked_by', on_delete=models.CASCADE, null=True)