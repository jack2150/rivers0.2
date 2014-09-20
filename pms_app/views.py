from django.shortcuts import render


def links(request):
    """
    A webix components for views
    :param request: dict
    :return: render
    """
    return render(request, 'pos_app/links.js',
                  content_type='application/javascript')
