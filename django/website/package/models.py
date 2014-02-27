from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _

from distutils.version import LooseVersion as versioner

from core.models import BaseModel
from publisher.models import Publisher

from package.utils import normalize_license


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
        return self.package_set.count()


class Package(BaseModel):
    title = models.CharField(_('Title'), max_length='100')
    slug = models.SlugField(
        _('Slug'),
        help_text='Enter a valid "slug" consisting of letters, numbers, \
            underscores or hyphens. Values will be converted to lowercase.',
        unique=True)
    category = models.ForeignKey(Category)
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
    documentation_url = models.URLField(_('Documentation URL'),
                                        blank=True,
                                        null=True,
                                        default='')

    class Meta:
        verbose_name = 'dataset'
        verbose_name_plural = 'datasets'

    def get_usage_count(self):
        return self.usage.count()

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ('package', [self.slug])


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
