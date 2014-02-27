import json

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.db.models import Count
from django.http import (
    HttpResponseRedirect,
    HttpResponse,
    HttpResponseForbidden
)
from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone
from django.views.generic import DetailView, ListView

from rest_framework.generics import ListAPIView, RetrieveAPIView

from homepage.models import Dpotw, Gotw

from .forms import PackageForm, DocumentationForm
from .models import Category, Package

from .utils import quote_plus


class CategoryDetailView(DetailView):
    template_name = 'package/category.html'
    model = Category
    context_object_name = 'category'

    def get_context_data(self, **kwargs):
        context = super(CategoryDetailView, self).get_context_data(**kwargs)
        context['packages'] = self.object.package_set.annotate(
            usage_count=Count('usage')).order_by('title')
        return context


class PackageListView(ListView):
    """
    We list all the packages by category
    """
    model = Category
    template_name = 'package/package_list.html'
    context_object_name = 'categories'


class PackageDetailView(DetailView):
    template_name = 'package/package.html'
    model = Package



@login_required
def add_package(request, template_name='package/package_form.html'):

    if not request.user.profile.can_add_package:
        return HttpResponseForbidden('permission denied')

    new_package = Package()
    form = PackageForm(request.POST or None, instance=new_package)

    if form.is_valid():
        new_package = form.save()
        new_package.created_by = request.user
        new_package.last_modified_by = request.user
        new_package.save()
        return HttpResponseRedirect(reverse('package',
                                    kwargs={'slug': new_package.slug}))

    return render(request, template_name, {
        'form': form,
        'action': 'add'})


@login_required
def edit_package(request, slug, template_name='package/package_form.html'):

    if not request.user.profile.can_edit_package:
        return HttpResponseForbidden('permission denied')

    package = get_object_or_404(Package, slug=slug)
    form = PackageForm(request.POST or None, instance=package)

    if form.is_valid():
        modified_package = form.save()
        modified_package.last_modified_by = request.user
        modified_package.save()
        messages.add_message(request,
                             messages.INFO,
                             'Package updated successfully')
        return HttpResponseRedirect(reverse('package',
                                    kwargs={'slug': modified_package.slug}))

    return render(request, template_name, {
        'form': form,
        'package': package,
        'action': 'edit', })


@login_required
def update_package(request, slug):

    package = get_object_or_404(Package, slug=slug)
    package.fetch_metadata()
    package.fetch_commits()
    messages.add_message(request,
                         messages.INFO,
                         'Package updated successfully')

    return HttpResponseRedirect(reverse('package',
                                        kwargs={'slug': package.slug}))


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
