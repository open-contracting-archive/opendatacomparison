from __future__ import unicode_literals
from factory import Sequence
from factory.django import DjangoModelFactory

from django.contrib.auth.models import User

from profiles.models import Profile


class UserFactory(DjangoModelFactory):
    FACTORY_FOR = User
    username = Sequence(lambda n: "user_%d" % n)

class ProfileFactory(DjangoModelFactory):
    FACTORY_FOR = Profile
