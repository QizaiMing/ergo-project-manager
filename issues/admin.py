from django.contrib import admin
from .models import Issue, Comment, Attachment, Link
# Register your models here.
admin.site.register(Issue)
admin.site.register(Comment)
admin.site.register(Attachment)
admin.site.register(Link)