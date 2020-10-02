from django import forms
from .models import Team
from social_django.models import UserSocialAuth

class TeamForm(forms.ModelForm):

    name = forms.CharField(max_length=50, required=True, label='Team Name', label_suffix='',
    widget=forms.TextInput(attrs={
        'placeholder': 'Your Team Name',
        'class': 'form-control mt-1 col-4'
    }))

    class Meta():
        model = Team
        exclude = ['manager', 'members']
        fields = [
            'name'
        ]