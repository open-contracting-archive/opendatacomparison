from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _

from distutils.version import LooseVersion as versioner

from core.models import BaseModel
from publisher.models import Publisher

from package.utils import normalize_license

from international.models import languages


class Category(BaseModel):
    title = models.CharField(_('Title'), max_length='50')
    slug = models.SlugField(_('slug'))
    description = models.TextField(_('description'), blank=True)
    title_plural = models.CharField(_('Title Plural'),
                                    max_length='50',
                                    blank=True)

    class Meta:
        ordering = ['title']
        verbose_name_plural = 'Categories'

    def __unicode__(self):
        return self.title

    @property
    def package_count(self):
        return self.packages.count()


class Format(BaseModel):
    title = models.CharField(_('Title'), max_length='100')
    slug = models.SlugField(
        _('Slug'),
        help_text='Enter a valid "slug" consisting of letters, numbers, \
            underscores or hyphens. Values will be converted to lowercase.',
        unique=True)
    description = models.TextField(_('Description'), blank=True)

    def __unicode__(self):
        return self.title


class Package(BaseModel):
    """
    A package is a dataset in our revamp.
    """
    title = models.CharField(_('Title'), max_length='100')
    slug = models.SlugField(
        _('Slug'),
        help_text='Enter a valid "slug" consisting of letters, numbers, \
            underscores or hyphens. Values will be converted to lowercase.',
        unique=True)
    category = models.ForeignKey(Category, related_name='packages')
    description = models.TextField(_('Description'), blank=True)
    url = models.URLField(
        _('Link'),
        help_text='Enter the URL where the dataset is hosted.',
        blank=True)
    usage = models.ManyToManyField(User, blank=True)
    publisher = models.ForeignKey(Publisher,
                                  blank=True,
                                  null=True,
                                  related_name='datasets',
                                  on_delete=models.SET_NULL)
    created_by = models.ForeignKey(User,
                                   blank=True,
                                   null=True,
                                   related_name='creator',
                                   on_delete=models.SET_NULL)
    last_modified_by = models.ForeignKey(User,
                                         blank=True,
                                         null=True,
                                         related_name='modifier',
                                         on_delete=models.SET_NULL)
    documentation = models.NullBooleanField(
        _('Documentation?'),
        help_text='Is documentation available?',
        null=True,
    )
    documentation_url = models.URLField(_('Documentation URL'),
                                        blank=True,
                                        null=True,
                                        default='')
    ########## Dataset qualities
    machine_readable = models.BooleanField(
        _('Machine Readable'),
        help_text='Is the dataset available in a machine readable, format - json, csv, xml, API',  # nopep8
        blank=True)
    formats = models.ManyToManyField(Format)
    nesting_depth = models.IntegerField(
        _('Nesting Depth'),
        help_text='How deep is the nesting of the data?',
        choices=((0, 'Flat'),
                 (1, 'Low nesting'),
                 (2, 'High nesting')),
        blank=True,
        null=True)
    nesting = models.TextField(
        _('Nesting Description'),
        help_text='Is the data flat or nested, or available as both? Other nesting notes.',  # nopep8
        blank=True)

    class Meta:
        verbose_name = 'dataset'
        verbose_name_plural = 'datasets'

    def get_usage_count(self):
        return self.usage.count()

    @property
    def usage_count(self):
        return self.usage.count()

    def __unicode__(self):
        return self.title

    def grid_clear_detail_template_cache(self):
        grids = (x.grid for x in self.gridpackage_set.all())
        for grid in grids:
            grid.clear_detail_template_cache()

    @models.permalink
    def get_absolute_url(self):
        return ('package', [self.slug])


class TranslatedPackage(BaseModel):
    package = models.ForeignKey(Package, related_name='translations')
    language = models.CharField(_('Language'),
                                max_length=10,
                                choices=languages,
                                default='en_US')
    title = models.CharField(_('Title'), max_length='100')
    description = models.TextField(_('Description'), blank=True)

    def language_name(self):
        dc = dict(languages)
        return dc.get(self.language)


class VersionManager(models.Manager):
    def by_version(self, *args, **kwargs):
        qs = self.get_query_set().filter(*args, **kwargs)
        return sorted(qs, key=lambda v: versioner(v.number))

    def by_version_not_hidden(self, *args, **kwargs):
        qs = self.get_query_set().filter(*args, **kwargs)
        qs = qs.filter(hidden=False)
        qs = sorted(qs, key=lambda v: versioner(v.number))
        qs.reverse()
        return qs


class Version(BaseModel):
    package = models.ForeignKey(Package, blank=True, null=True)
    number = models.CharField(_('Version'),
                              max_length='100',
                              default='',
                              blank='')
    license = models.CharField(_('license'), max_length='100')
    hidden = models.BooleanField(_('hidden'), default=False)
    upload_time = models.DateTimeField(_('upload_time'),
                                       help_text=_('When this was uploaded?'),
                                       blank=True,
                                       null=True)
    objects = VersionManager()

    class Meta:
        get_latest_by = 'upload_time'
        ordering = ['-upload_time']

    @property
    def pretty_license(self):
        return self.license.replace('License', '').replace('license', '')

    @property
    def pretty_status(self):
        return self.get_development_status_display().split(' ')[-1]

    def save(self, *args, **kwargs):
        self.license = normalize_license(self.license)
        super(Version, self).save(*args, **kwargs)

    def __unicode__(self):
        return '%s: %s' % (self.package.title, self.number)
