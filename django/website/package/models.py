from datetime import datetime, timedelta
import re

from django.core.cache import cache
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from distutils.version import LooseVersion as versioner

from core.utils import STATUS_CHOICES
from core.models import BaseModel
from package.signals import signal_fetch_latest_metadata
from package.utils import get_version, get_pypi_version, normalize_license


class NoPyPiVersionFound(Exception):
    pass


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


class Package(BaseModel):

    title = models.CharField(_('Title'), max_length='100')
    slug = models.SlugField(
        _('Slug'),
        help_text='Enter a valid "slug" consisting of letters, numbers, \
            underscores or hyphens. Values will be converted to lowercase.',
        unique=True)
    category = models.ForeignKey(Category, verbose_name='Installation')
    repo_description = models.TextField(_('Repo Description'), blank=True)
    repo_url = models.URLField(
        _('Repository URL'),
        help_text='Enter the URL where the dataset is hosted.',
        blank=True)
    participants = models.TextField(
        _('Participants'),
        help_text='List of collaborats/participants on the project',
        blank=True)
    usage = models.ManyToManyField(User, blank=True)
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
    last_fetched = models.DateTimeField(blank=True,
                                        null=True,
                                        default=timezone.now)
    documentation_url = models.URLField(_('Documentation URL'),
                                        blank=True,
                                        null=True,
                                        default='')

    commit_list = models.TextField(_('Commit List'), blank=True)

    def last_updated(self):
        cache_name = self.cache_namer(self.last_updated)
        last_commit = cache.get(cache_name)
        if last_commit is not None:
            return last_commit
        try:
            last_commit = self.commit_set.latest('commit_date').commit_date
            if last_commit:
                cache.set(cache_name, last_commit)
                return last_commit
        except ObjectDoesNotExist:
            last_commit = None

        return last_commit

    @property
    def active_examples(self):
        return self.packageexample_set.filter(active=True)

    @property
    def license_latest(self):
        try:
            return self.version_set.latest().license
        except Version.DoesNotExist:
            return 'UNKNOWN'

    def grids(self):

        return (x.grid for x in self.gridpackage_set.all())

    def repo_name(self):
        return re.sub(self.repo.url_regex, '', self.repo_url)

    def repo_info(self):
        return dict(
            username=self.repo_name().split('/')[0],
            repo_name=self.repo_name().split('/')[1],
        )

    def participant_list(self):

        return self.participants.split(',')

    def get_usage_count(self):
        return self.usage.count()

    def commits_over_52(self):
        cache_name = self.cache_namer(self.commits_over_52)
        value = cache.get(cache_name)
        if value is not None:
            return value
        now = datetime.now()
        commits = self.commit_set.filter(
            commit_date__gt=now - timedelta(weeks=52),
        ).values_list('commit_date', flat=True)

        weeks = [0] * 52
        for cdate in commits:
            age_weeks = (now - cdate).days // 7
            if age_weeks < 52:
                weeks[age_weeks] += 1

        value = ','.join(map(str, reversed(weeks)))
        cache.set(cache_name, value)
        return value

    def fetch_pypi_data(self, *args, **kwargs):
        # We don't need this for OpenData, but not deleting method so things
        # don't break
        return False

    def fetch_metadata(self, fetch_pypi=True):

        if fetch_pypi:
            self.fetch_pypi_data()
        self.repo.fetch_metadata(self)
        signal_fetch_latest_metadata.send(sender=self)
        self.last_fetched = timezone.now()
        self.save()

    def grid_clear_detail_template_cache(self):
        for grid in self.grids():
            grid.clear_detail_template_cache()

    def save(self, *args, **kwargs):
        if not self.repo_description:
            self.repo_description = ''
        self.grid_clear_detail_template_cache()
        super(Package, self).save(*args, **kwargs)

    def fetch_commits(self):
        self.repo.fetch_commits(self)

    def pypi_version(self):
        cache_name = self.cache_namer(self.pypi_version)
        version = cache.get(cache_name)
        if version is not None:
            return version
        version = get_pypi_version(self)
        cache.set(cache_name, version)
        return version

    def last_released(self):
        cache_name = self.cache_namer(self.last_released)
        version = cache.get(cache_name)
        if version is not None:
            return version
        version = get_version(self)
        cache.set(cache_name, version)
        return version

    @property
    def development_status(self):
        ''' Gets data needed in API v2 calls '''
        return self.last_released().pretty_status

    @property
    def pypi_ancient(self):
        release = self.last_released()
        if release:
            return release.upload_time < datetime.now() - timedelta(365)
        return None

    @property
    def no_development(self):
        commit_date = self.last_updated()
        if commit_date is not None:
            return commit_date < datetime.now() - timedelta(365)
        return None

    class Meta:
        ordering = ['title']
        get_latest_by = 'id'

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ('package', [self.slug])


class PackageExample(BaseModel):

    package = models.ForeignKey(Package)
    title = models.CharField(_('Title'), max_length='100')
    url = models.URLField(_('URL'))
    active = models.BooleanField(
        _('Active'),
        default=True,
        help_text='Moderators have to approve links before they are provided')

    class Meta:
        ordering = ['title']

    def __unicode__(self):
        return self.title

    @property
    def pretty_url(self):
        if self.url.startswith('http'):
            return self.url
        return 'http://' + self.url


class Commit(BaseModel):

    package = models.ForeignKey(Package)
    commit_date = models.DateTimeField(_('Commit Date'))
    commit_hash = models.CharField(
        _('Commit ID'),
        help_text='Something that links to that specific release',
        max_length=150,
        blank=True,
        default='')

    class Meta:
        ordering = ['-commit_date']
        get_latest_by = 'commit_date'

    def __unicode__(self):
        return 'Commit for "%s" on %s' % (self.package.title,
                                          unicode(self.commit_date))

    def save(self, *args, **kwargs):
        # reset the last_updated and commits_over_52 caches on the package
        package = self.package
        cache.delete(package.cache_namer(self.package.last_updated))
        cache.delete(package.cache_namer(package.commits_over_52))
        self.package.last_updated()
        super(Commit, self).save(*args, **kwargs)


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
    development_status = models.IntegerField(_('Development Status'),
                                             choices=STATUS_CHOICES,
                                             default=0)
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
