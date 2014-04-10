from django import forms

from .models import Field


class FieldForm(forms.ModelForm):
    class Meta:
        model = Field
        exclude = ('mapsto',)

