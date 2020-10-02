from django import forms
from django.core.files.images import get_image_dimensions

from user.models import UserPicture


class UserPictureForm(forms.ModelForm):
    class Meta:
        model = UserPicture
        fields = '__all__'

    def clean_avatar(self): #I think this whole function doesn't work
        avatar = self.cleaned_data['picture']

        try:
            w, h = get_image_dimensions(picture) #gets img dimensions

            #validate dimensions
            max_width = max_height = 500
            if w > max_width or h > max_height:
                raise forms.ValidationError(
                    u'Please use an image that is '
                     '%s x %s pixels or smaller.' % (max_width, max_height))

            #validate content type
            main, sub = picture.content_type.split('/')
            if not (main == 'image' and sub in ['jpeg', 'pjpeg', 'gif', 'png']):
                raise forms.ValidationError(u'Please use a JPEG, '
                    'GIF or PNG image.')

            #validate file size
            if len(picture) > (20 * 1024):
                raise forms.ValidationError(
                    u'Avatar file size may not exceed 20k.')

        except AttributeError:
            """
            Handles case when we are updating the user profile
            and do not supply a new avatar
            """
            pass

        return picture