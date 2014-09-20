from django.shortcuts import render
from django.template import RequestContext


def index(request):
    """
    Testing for menu only
    :param request: dict
    :return: render
    """
    return render(request, 'base/index.html', {'request': request})


def webix_js(request):
    """
    A webix components for views that include 'menu_links' and other component parts
    :param request: dict
    :return: render
    """
    return render(request, 'base/webix.js',
                  content_type='application/javascript')


def logic_js(request):
    """
    A webix actions for views that include only functions that use inside logic js
    :param request: dict
    :return: render
    """
    return render(request, 'base/logic.js',
                  content_type='application/javascript')


def current_path(request):
    """
    Current path tag for all templates
    with TEMPLATE_CONTEXT_PROCESSORS
    :param request: object
    :return: dict
    """
    return {'current_path': request.path}
