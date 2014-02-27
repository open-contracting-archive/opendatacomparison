from floppyforms import ModelForm, ModelMultipleChoiceField

from core.widgets import BetterSelectMultiple

from package.models import Category, Package, Format


def package_help_text():
    help_text = ""
    for category in Category.objects.all():
        help_text += """
        <li><strong>{title}</strong> -  {description}</li>""".format(
            title=category.title, description=category.description)
    help_text = "<ul>{0}</ul>".format(help_text)
    return help_text


class PackageForm(ModelForm):
    formats = ModelMultipleChoiceField(
        required=False,
        queryset=Format.objects.all(),
        widget=BetterSelectMultiple(attrs={
            'data-add': '&darr; Add',
            'data-remove': '&uarr; Remove',
            'size': 3,
            'style': 'width: 30%',
        }),
    )

    def __init__(self, *args, **kwargs):
            super(PackageForm, self).__init__(*args, **kwargs)
            self.fields['category'].help_text = package_help_text()
            self.fields['url'].required = True

    def clean_slug(self):
        return self.cleaned_data['slug'].lower()

    class Meta:
        model = Package
        exclude = ['usage', 'created_by', 'last_modified_by']


class DocumentationForm(ModelForm):

    class Meta:
        model = Package
        fields = ["documentation_url", ]
