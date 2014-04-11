from django import forms
from django.forms.formsets import BaseFormSet

from .models import Field, TranslatedField


class FieldForm(forms.ModelForm):
    error_css_class = 'has-error'
    required_css_class = 'required'
    css_class = "form-control"
    class Meta:
        model = Field
        exclude = ('datamap', 'mapsto',)


class TranslatedFieldForm(forms.ModelForm):
    error_css_class = 'has-error'
    required_css_class = 'required'
    field = forms.IntegerField(widget=forms.HiddenInput)

    class Meta:
        model = TranslatedField
