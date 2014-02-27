from floppyforms import ModelForm, TextInput

from package.models import Category, Package


def package_help_text():
    help_text = ""
    for category in Category.objects.all():
        help_text += """<li><strong>{title}</strong> -  {description}</li>""".format(
                        title=category.title,
                        description=category.description
                        )
    help_text = "<ul>{0}</ul>".format(help_text)
    return help_text


class PackageForm(ModelForm):

    def __init__(self, *args, **kwargs):
            super(PackageForm, self).__init__(*args, **kwargs)
            self.fields['category'].help_text = package_help_text()
            self.fields['url'].required = True

    def clean_slug(self):
        return self.cleaned_data['slug'].lower()

    class Meta:
        model = Package
        fields = ['url', 'title', 'slug', 'category', 'publisher', ]


class DocumentationForm(ModelForm):

    class Meta:
        model = Package
        fields = ["documentation_url", ]
