import json

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.db.models import Q, Count
from django.http import (
    HttpResponseRedirect,
    HttpResponse,
    HttpResponseForbidden,
)
from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone
from django.views.generic import DetailView, ListView

from braces.views import LoginRequiredMixin
from extra_views import (
    CreateWithInlinesView,
    UpdateWithInlinesView,
    InlineFormSet
)
from grid.models import Grid
from rest_framework.generics import ListAPIView, RetrieveAPIView

from .forms import PackageForm, DocumentationForm
from .models import Category, Package, TranslatedPackage
from .utils import quote_plus


class CategoryDetailView(DetailView):
    template_name = 'package/category.html'
    model = Category
    context_object_name = 'category'

    def get_context_data(self, **kwargs):
        context = super(CategoryDetailView, self).get_context_data(**kwargs)
        context['packages'] = self.object.packages.order_by('title')
        return context


class PackageListView(ListView):
    """
    We list all the packages by category
    """
    model = Package
    template_name = 'package/package_list.html'
    context_object_name = 'packages'

    def get_queryset(self):
        packages = Package.objects.select_related('publisher', 'category')
        packages = packages.annotate(ucount=Count('usage'))
        packages = packages.annotate(downloadcount=Count('downloads'))
        packages = packages.order_by('publisher__country')
        return packages


class PackageDetailView(DetailView):
    template_name = 'package/package.html'
    model = Package


class TranslatedPackageInline(InlineFormSet):
    model = TranslatedPackage


class PackageCreateView(LoginRequiredMixin,
                        CreateWithInlinesView):
    template_name = 'package/package_form.html'
    model = Package
    inlines = [TranslatedPackageInline]
    form_class = PackageForm

    def dispatch(self, *args, **kwargs):
        user = self.request.user
        if user.is_authenticated() and not user.profile.can_add_package:
            return HttpResponseForbidden("permission denied")
        else:
            return super(PackageCreateView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        new_package = form.save()
        new_package.created_by = self.request.user
        new_package.last_modified_by = self.request.user
        new_package.save()
        return HttpResponseRedirect(reverse('package',
                                    kwargs={'slug': new_package.slug}))


class PackageUpdateView(LoginRequiredMixin,
                        UpdateWithInlinesView):
    template_name = 'package/package_form.html'
    model = Package
    inlines = [TranslatedPackageInline]
    form_class = PackageForm

    def dispatch(self, *args, **kwargs):
        user = self.request.user
        if user.is_authenticated() and not user.profile.can_edit_package:
            return HttpResponseForbidden("permission denied")
        else:
            return super(PackageUpdateView, self).dispatch(*args, **kwargs)

    def forms_valid(self, form, inlines):
        modified_package = form.save()
        modified_package.last_modified_by = self.request.user
        modified_package.save()
        for formset in inlines:
            formset.save()
        messages.add_message(self.request,
                             messages.INFO,
                             'Package updated successfully')
        return HttpResponseRedirect(reverse('package',
                                    kwargs={'slug': modified_package.slug}))


def ajax_package_list(request, template_name="package/ajax_package_list.html"):
    q = request.GET.get("q", "")
    packages = []
    if q:
        _dash = "%s-%s" % ('', q)
        _space = "%s %s" % ('', q)
        _underscore = '%s_%s' % ('', q)
        packages = Package.objects.filter(
                        Q(title__istartswith=q) |
                        Q(title__istartswith=_dash) |
                        Q(title__istartswith=_space) |
                        Q(title__istartswith=_underscore)
                    )

    packages_already_added_list = []
    grid_slug = request.GET.get("grid", "")
    if packages and grid_slug:
        grids = Grid.objects.filter(slug=grid_slug)
        if grids:
            grid = grids[0]
            packages_already_added_list = [x['slug'] for x in grid.packages.all().values('slug')]
            new_packages = tuple(packages.exclude(slug__in=packages_already_added_list))[:20]
            number_of_packages = len(new_packages)
            if number_of_packages < 20:
                try:
                    old_packages = packages.filter(slug__in=packages_already_added_list)[:20 - number_of_packages]
                except AssertionError:
                    old_packages = None

                if old_packages:
                    old_packages = tuple(old_packages)
                    packages = new_packages + old_packages
            else:
                packages = new_packages

    return render(request, template_name, {
        "packages": packages,
        'packages_already_added_list': packages_already_added_list,
        }
    )

def usage(request, slug, action):
    success = False
    # Check if the user is authenticated, redirecting them to the login page if
    # they're not.
    if not request.user.is_authenticated():

        url = settings.LOGIN_URL
        referer = request.META.get('HTTP_REFERER')
        if referer:
            url += quote_plus('?next=/%s' % referer.split('/', 3)[-1])
        else:
            url += '?next=%s' % reverse('usage', args=(slug, action))
        url = reverse('login')
        if request.is_ajax():
            response = {}
            response['success'] = success
            response['redirect'] = url
            return HttpResponse(json.dumps(response))
        return HttpResponseRedirect(url)

    package = get_object_or_404(Package, slug=slug)

    # Update the current user's usage of the given package as specified by the
    # request.
    if package.usage.filter(username=request.user.username):
        if action.lower() == 'add':
            # The user is already using the package
            success = True
            change = 0
        else:
            # If the action was not add and the user has already specified
            # they are a use the package then remove their usage.
            package.usage.remove(request.user)
            success = True
            change = -1
    else:
        if action.lower() == 'lower':
            # The user is not using the package
            success = True
            change = 0
        else:
            # If the action was not lower and the user is not already using
            # the package then add their usage.
            package.usage.add(request.user)
            success = True
            change = 1

    # Invalidate the cache of this users's used_packages_list.
    if change == 1 or change == -1:
        cache_key = 'sitewide_used_packages_list_%s' % request.user.pk
        cache.delete(cache_key)
        package.grid_clear_detail_template_cache()

    # Return an ajax-appropriate response if necessary
    if request.is_ajax():
        response = {'success': success}
        if success:
            response['change'] = change

        return HttpResponse(json.dumps(response))

    # Intelligently determine the URL to redirect the user to based on the
    # available information.
    next = request.GET.get('next') or request.META.get('HTTP_REFERER') or reverse('package', kwargs={'slug': package.slug})
    return HttpResponseRedirect(next)




class PackageListAPIView(ListAPIView):
    model = Package
    paginate_by = 20


class PackageDetailAPIView(RetrieveAPIView):
    model = Package


@login_required
def post_data(request, slug):
    package = get_object_or_404(Package, slug=slug)
    package.last_fetched = timezone.now()
    package.save()
    return HttpResponseRedirect(reverse('package',
                                kwargs={'slug': package.slug}))


@login_required
def edit_documentation(request,
                       slug,
                       template_name='package/documentation_form.html'):
    package = get_object_or_404(Package, slug=slug)
    form = DocumentationForm(request.POST or None, instance=package)
    if form.is_valid():
        form.save()
        messages.add_message(request,
                             messages.INFO,
                             'Package documentation updated successfully')
        return redirect(package)
    return render(request, template_name,
                  dict(
                      package=package,
                      form=form
                  ))
