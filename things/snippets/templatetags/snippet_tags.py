from django.template import Library, Context, Node
from django.template.loader import get_template
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe

from ..utils import get_snippet_from_cache

register = Library()


@register.tag
def snippet(parser, token):
    """
    Outputs the text from a Snippet object based on a key that is passed.

    Snippets may be auto-loaded initially by reading the templates in
    a theme.

    Some inspiration to do a wrapper tag came from https://github.com/wellfire/django-addendum

    Examples::

        {% snippet 'sitename' %}<h1>My Site</h1>{% endsnippet %}

        {% snippet 'sitename' striptags %}No html loading here.{% endsnippet %}
    """
    nodelist = parser.parse(('endsnippet',))
    parser.delete_first_token()
    kwargs = {}

    bits = token.split_contents()

    slug = bits[1][1:-1]

    for bit in bits[2:]:
        if bit == "striptags":
            kwargs.update({"striptags": True})

    return SnippetNode(nodelist, slug, **kwargs)


class SnippetNode(Node):
    striptags = False

    def __init__(self, nodelist, slug, **kwargs):
        self.slug = slug
        if 'striptags' in kwargs:
            self.striptags = kwargs['striptags']

    def render(self, context):
        striptags = self.striptags

        context.update({
            'snippet_obj': None,
            'snippet_content': None
        })

        snippet = get_snippet_from_cache(slug=self.slug)

        if snippet:
            content = snippet.content
            if striptags:
                content = strip_tags(content)
            content = mark_safe(content)
            context.update({
                'strip_tags': striptags,
                'snippet_obj': snippet,
                'snippet_content': content
            })

        t = get_template("_snippet.html")
        return t.render(Context(context))
