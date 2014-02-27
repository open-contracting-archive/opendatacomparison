from django import forms

from profiles.models import Profile

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit


class ProfileForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = '.'
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Submit'))

    class Meta:
        model = Profile
        fields = ['url']
