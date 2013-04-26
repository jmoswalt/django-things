from django.conf import settings


def extras(request):
    from .models import Thing
    contexts = {}

    if request.user.is_superuser and "mode" in request.GET:
        if request.GET['mode'] == "edit":
            request.session['edit_mode'] = True
        else:
            request.session['edit_mode'] = False

    contexts['edit_mode'] = request.session.get('edit_mode', False)

    contexts['USE_STATIC_SITE'] = settings.USE_STATIC_SITE

    contexts['CONTENT_APPS'] = Thing.content_apps()

    return contexts
