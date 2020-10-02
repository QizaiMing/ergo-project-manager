from django.urls import path
from .views import (
    issue_detail_view,
    issue_update_view,
    issue_list_view,
    issue_upload_attachment,
    issue_download_attachment,
    issue_delete_attachment
)

app_name = 'issues'
urlpatterns = [
    path('<int:id>', issue_detail_view, name='issues_detail'),
    path('<int:id>/update', issue_update_view, name='issues_update'),
    path('<int:id>/list', issue_list_view, name='issues_list'),
    path('<int:id>/attachment', issue_upload_attachment, name='issues_upload_attachment'),
    path('<int:id>/attachment/delete', issue_delete_attachment, name='issues_delete_attachment'),
    path('attachment/download/<int:id>', issue_download_attachment, name='issues_download_attachment')
]