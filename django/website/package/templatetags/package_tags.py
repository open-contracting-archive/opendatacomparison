from django import template
from django.utils.text import Truncator

from international.models import languages_english as languages
from package.context_processors import used_packages_list

register = template.Library()


class ParticipantURLNode(template.Node):

    def __init__(self, repo, participant):
        self.repo = template.Variable(repo)
        self.participant = template.Variable(participant)

    def render(self, context):
        repo = self.repo.resolve(context)
        participant = self.participant.resolve(context)
        if repo.user_url:
            user_url = repo.user_url % participant
        else:
            user_url = '%s/%s' % (repo.url, participant)
        return user_url


@register.tag
def participant_url(parser, token):
    try:
        tag_name, repo, participant = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires exactly two arguments" % token.contents.split()[0]
    return ParticipantURLNode(repo, participant)


@register.filter
def commits_over_52(package):
    return package.commits_over_52()


@register.inclusion_tag('package/templatetags/_usage_button.html', takes_context=True)
def usage_button(context):
    response = used_packages_list(context['request'])
    response['STATIC_URL'] = context['STATIC_URL']
    response['package'] = context['package']
    if context['package'].pk in response['used_packages_list']:
        response['usage_action'] = "remove"
        response['image'] = "usage_triangle_filled"
    else:
        response['usage_action'] = "add"
        response['image'] = "usage_triangle_hollow"
    return response


@register.filter
def truncatecharsbrute(value, arg):
    try:
        length = int(arg)
    except ValueError:  # Invalid literal for int().
        return value  # Fail silently.
    return Truncator(value).chars(length, truncate='')


@register.filter
def listlanguages(value):
    if len(value) > 0:
        langs = [langtup[1] for langtup in languages if langtup[0] in value]
        return ', '.join(langs)
    else:
        return ''
