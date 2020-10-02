from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Issue, Attachment, Comment, Link
from projects.models import Project
from django.contrib.auth.models import User
import datetime #used in issue_detail_view
import math #used for displaying dynamic textarea rows
from notifications.signals import notify
# Create your views here.

def issue_detail_view(request, *args, **kwargs):
    template_name = 'issues_detail.html'
    id_ = kwargs.get('id')
    issue = Issue.objects.get(id=id_)
    attachments = Attachment.objects.filter(issue=issue.id)
    project = issue.project
    issue.created = issue.created.strftime("%B %d, %Y, %H:%M") #used for showing pretty time stamps
    issue.modified = issue.modified.strftime("%B %d, %Y, %H:%M")
    comments = Comment.objects.filter(issue=issue.id).order_by('created')
    links = set(Link.objects.filter(parent_issue=issue.id) | Link.objects.filter(child_issue=issue.id))
    all_issues = Issue.objects.filter(project=issue.project.id).order_by('-created')
   
    if request.method == 'POST' and request.user.id is not 9:
        action = request.POST.get('action')

        if action == 'delete_issue':
            issue = Issue.objects.get(id=request.POST.get('issue_id'))
            issue.delete()
            return redirect('/projects/%s' % (project.id))

        if action == 'create_comment':
            comment = Comment()
            comment.creator = User.objects.get(id=request.POST.get('creator'))
            comment.content = request.POST.get('content')
            comment.issue = Issue.objects.get(id=request.POST.get('issue_id'))
            comment.save()

            if (issue.assignee is not None) and (request.user.id is not issue.assignee.id):
                notify.send(sender=request.user, recipient=issue.assignee,
                        verb='New comment on %s' % (issue.compressed_title()), action_object=issue,
                        description=issue.get_absolute_url())

            comments = Comment.objects.filter(issue=issue.id).order_by('created')

        if action == 'delete_comment':
            comment = Comment.objects.get(id=request.POST.get('comment_id'))
            comment.delete()
            comments = Comment.objects.filter(issue=issue.id).order_by('created')

        if action == 'update_comment':
            comment = Comment.objects.get(id=request.POST.get('comment_id'))
            comment.content = request.POST.get('comment_content')
            comment.save()
            comments = Comment.objects.filter(issue=issue.id).order_by('created')

        if action == 'delete_link':
            link = Link.objects.get(id=request.POST.get('link_id'))
            link.delete()
            links = Link.objects.filter(parent_issue=issue.id)

        if action == 'create_link':
            link = Link()
            link.parent_issue = Issue.objects.get(id=request.POST.get('issue_id'))
            link.kind = request.POST.get('link_kind')
            link.child_issue = Issue.objects.get(id=request.POST.get('child_issue'))
            link.save()

            if (issue.assignee is not None) and (request.user.id is not issue.assignee.id):
                notify.send(sender=request.user, recipient=issue.assignee,
                        verb='New linked issue on %s' % (issue.compressed_title()), action_object=issue)

            links = Link.objects.filter(parent_issue=issue.id)

    if comments:
        rows = [] 
        for comment in comments: #used to display comments in a good way
                rows.append(math.ceil(len(comment.content)/110))#every 110 characters textarea html tag needs +1 rows

        comments = zip(comments, rows)#combines the two list to be able to iterate over them at the same time

    context = {
        'issue': issue,
        'attachments': attachments,
        'comments': comments,
        'links': links,
        'all_issues': all_issues
    }
    return render(request, template_name, context)

def issue_create_view(request, *args, **kwargs):
    template_name = 'issues_create.html'
    id_ = kwargs.get('id')
    project = Project.objects.get(id=id_)
    users = set() #does not repeat users
    teams = project.teams.all()

    for team in teams: #goes through all of the teams and adds the users to the set
        for user in team.members.all():
            users.add(user)

    users.add(project.manager)

    if request.method == 'POST' and request.user.id is not 9:
        issue = Issue()
        issue.title = request.POST.get('title')
        issue.description = request.POST.get('description')
        issue.creator = User.objects.get(id=request.POST.get('creator'))

        if request.POST.get('assignee') is not '':
            issue.assignee = User.objects.get(id=request.POST.get('assignee'))            

        issue.status = request.POST.get('status')
        issue.priority = request.POST.get('priority')
        issue.project = project
        issue.save()

        if issue.assignee is not None and issue.assignee.id is not request.user.id:
            notify.send(sender=request.user, recipient=issue.assignee,
            verb='You were assigned to a new issue', action_object=issue,
            description=issue.get_absolute_url())

        return redirect('/projects/%s' % (project.id))

    else:
        context = {
            'users': users,
            'project': project
            }
        return render(request, template_name, context)

def issue_update_view(request, *args, **kwargs):
    template_name = 'issues_update.html'
    id_ = kwargs.get('id')
    issue = Issue.objects.get(id=id_)
    project = issue.project
    users = set()
    teams = project.teams.all()

    for team in teams: #goes through all of the teams and adds the users to the set
        for user in team.members.all():
            users.add(user)

    users.add(project.manager)

    if request.method == 'POST' and request.user.id is not 9:
        issue.title = request.POST.get('title')
        issue.description = request.POST.get('description')

        if request.POST.get('assignee') == '':
            issue.assignee = None

        elif issue.assignee is not None and issue.assignee.id is not int(request.POST.get('assignee')):
            issue.assignee = User.objects.get(id=request.POST.get('assignee'))

            if int(request.POST.get('assignee')) is not request.user.id:
                notify.send(sender=request.user, recipient=issue.assignee,
                     verb='You were assigned to a new issue', action_object=issue,
                     description=issue.get_absolute_url())

        elif issue.assignee is None:
            issue.assignee = User.objects.get(id=request.POST.get('assignee'))

            if int(request.POST.get('assignee')) is not request.user.id:
                notify.send(sender=request.user, recipient=issue.assignee,
                     verb='You were assigned to a new issue', action_object=issue,
                     description=issue.get_absolute_url())

        issue.status = request.POST.get('status')
        issue.priority = request.POST.get('priority')
        issue.save()
        return redirect('/issues/%s' % (issue.id))

    context = {
        'issue': issue,
        'users': users
    }
    return render(request, template_name, context)

def issue_list_view(request, *args, **kwargs):
    template_name = 'issues_list.html'
    id_ = kwargs.get('id')
    project = Project.objects.get(id=id_)
    users = set() #does not repeat users
    teams = project.teams.all()

    for team in teams: #goes through all of the teams and adds the users to the set
        for user in team.members.all():
            users.add(user)

    users.add(project.manager)

    issues = Issue.objects.filter(project=id_).order_by('-created')
    context = {
            'issues': issues,
            'project': project,
            'users': users
        }

    if request.method == 'POST':

        filters = {
            'search': '',
            'status': False,
            'priority': False,
            'creator': False,
            'assignee': False
        }

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

        if request.POST.get('filter_assignee'):
            assignee_id = request.POST.get('filter_assignee')
            issues = issues.filter(assignee=assignee_id)
            filters['assignee'] = User.objects.get(id=assignee_id)

        context['issues'] = issues #update new issues list
        context['filters'] = filters #send updated filters

    return render(request, template_name, context)
    
def issue_upload_attachment(request,*args, **kwargs):
    template_name = 'issues_upload_attachment.html'
    id_ = kwargs.get('id')
    issue = Issue.objects.get(id=id_)
    context = {
        'issue': issue
    }

    if request.method == 'POST' and request.user.id is not 9:
        attachment = Attachment()
        attachment.file = request.FILES['file']
        attachment.issue = issue
        attachment.save()

        if (issue.assignee is not None) and (request.user.id is not issue.assignee.id):
            notify.send(sender=request.user, recipient=issue.assignee,
                    verb='New file uploaded to %s' % (issue.compressed_title()), action_object=issue)

        return redirect('/issues/%s' % (issue.id))
    
    return render(request, template_name, context)

def issue_download_attachment(request, *args, **kwargs):
    id_ = kwargs.get('id')
    attachment = Attachment.objects.get(id=id_)
    filename = attachment.file.name.split('/')[2] #this line gets the filename only ('example.jpg')
    response = HttpResponse()
    # Let NGINX handle it
    #it's inefficient to let django backend handle file downloads
    response.content = attachment.file.read()
    response["Content-Disposition"] = "attachment; filename={0}".format(filename)
    #I could'n make this next line work to serve files using nginx
    #response["X-Accel-Redirect"] = "/attachments/{0}".format(filename)
    return response

def issue_delete_attachment(request, *args, **kwargs):
    template_name = 'issues_delete_attachment.html'
    id_ = kwargs.get('id')
    issue = Issue.objects.get(id=id_)
    attachments = Attachment.objects.filter(issue=issue.id)

    context = {
        'issue': issue,
        'attachments': attachments
    }

    if request.method == 'POST' and request.user.id is not 9: #Get form data
        ex_attachment = Attachment.objects.get(id=request.POST.get('attachment_id')) #Get team sent by the form
        ex_attachment.delete()
        attachments = Attachment.objects.filter(issue=issue.id) #Refresh context

        context = {
            'issue': issue,
            'attachments': attachments
        }
        return render(request, template_name, context)

    return render(request, template_name, context)