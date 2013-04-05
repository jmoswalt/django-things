import os
import re

from johnny.cache import enable


def load_theme_snippets(theme_path):
    enable()
    from .models import Snippet

    for root, dirs, files in os.walk(os.path.join(theme_path, 'templates')):
        for f in files:
            with open(os.path.join(root, f)) as fi:

                matches = re.findall("{% snippet ([\\w\\-\\s\\'\\\"]+) %}([^{%]+){% endsnippet %}", fi.read(), re.I)
                for match in matches:
                    snippet_key = re.search("([\\'\\\"])([\\w\\-]+)([\\'\\\"])( striptags)?", match[0], re.I)
                    snippet_value = match[1]

                    try:
                        slug = snippet_key.group(2)
                        name = slug.replace('-', ' ').replace('_', ' ').title()
                    except IndexError:
                        slug = None

                    striptags = snippet_key.group(4)
                    allow_html = 'True'

                    if striptags:
                        allow_html = ''

                    if slug:
                        try:
                            Snippet.objects.get(slug=slug)
                        except Snippet.DoesNotExist:
                            print "New Snippet found: ", name
                            new_snippet = Snippet()
                            new_snippet.name = name
                            new_snippet.slug = slug
                            new_snippet.values = {'content': snippet_value, 'allow_html': allow_html}
                            new_snippet.save()
                        except Exception as e:
                            print e
