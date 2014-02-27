from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.generic.base import RedirectView
from django.views.generic import DetailView, ListView
from django.views.generic.edit import UpdateView

from braces.views import LoginRequiredMixin

from profiles.forms import ProfileForm
from profiles.models import Profile


class ProfileRedirectView(RedirectView):
    pattern_name = 'profile_detail'

    def get_redirect_url(self, *args, **kwargs):
        slug = self.request.user.username
        kwargs = {'slug': slug}
        return super(ProfileRedirectView,
                     self).get_redirect_url(*args, **kwargs)


class ProfileDetailView(DetailView):
    template_name = 'profiles/profile.html'
    model = Profile

    def get_slug_field(self):
        return 'user__username'


class ProfileListView(ListView):
    template_name = 'profiles/profiles.html'
    model = Profile
    context_object_name = 'users'

    def dispatch(self, request, *args, **kwargs):
        self.request_user = request.user
        return super(ProfileListView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        if self.request_user.is_staff:
            users = User.objects.all()
        else:
            users = User.objects.filter(is_active=True)
        return users


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = 'profiles/profile_edit.html'

    def get_success_url(self):
        return reverse('profile_detail',
                       kwargs={'slug': self.object.user.username})

    def get_slug_field(self):
        return 'user__username'

    def form_valid(self, form):
        messages.add_message(self.request, messages.INFO, 'Profile Saved')
        return super(ProfileUpdateView, self).form_valid(form)
