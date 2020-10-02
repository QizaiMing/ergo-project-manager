from django import forms
from .models import Project

class ProjectForm(forms.ModelForm):

    name = forms.CharField(max_length=50, required=True, label='Project Name', label_suffix='',
    widget=forms.TextInput(attrs={
        'placeholder': 'Your Project Name',
        'class': 'form-control mt-1 col-4'
    }))

    class Meta():
        model = Project
        exclude = ['manager', 'teams']
        fields = [
            'name',
        ]