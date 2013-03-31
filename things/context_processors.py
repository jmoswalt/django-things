def extras(request):
    contexts = {}

    if request.user.is_superuser and "mode" in request.GET:
        if request.GET['mode'] == "edit":
            request.session['edit_mode'] = True
        else:
            request.session['edit_mode'] = False

    contexts['edit_mode'] = request.session.get('edit_mode', False)

    return contexts
