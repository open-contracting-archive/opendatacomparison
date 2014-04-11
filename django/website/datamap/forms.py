from django import forms

from .models import Field, TranslatedField


class FieldForm(forms.ModelForm):
    class Meta:
        model = Field
        exclude = ('datamap', 'mapsto',)


class TranslatedFieldForm(forms.ModelForm):
    field = forms.IntegerField(widget=forms.HiddenInput)

    class Meta:
        model = TranslatedField
