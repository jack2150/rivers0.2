from django.core.urlresolvers import reverse
from django.shortcuts import render
# noinspection PyUnresolvedReferences
from django.contrib.contenttypes.models import ContentType
# noinspection PyUnresolvedReferences
from rivers.urls import *
from django.contrib import admin


# noinspection PyProtectedMember
def base_model_list(request):
    """
    List all model for admin site
    """
    app_parent_label_list = {
        'statement_account': 'tos_import',
        'statement_position': 'tos_import',
        'statement_trade': 'tos_import',
    }

    module_list = list()

    for item in admin.site._registry:
        module = item
        """:type : ModelBase"""

        app = str(module._meta.app_label)
        try:
            app_parent_label = app_parent_label_list[app]
        except KeyError:
            app_parent_label = app

        name = str(module.__name__)

        module_list.append(
            {
                'name': name,
                'url': reverse('admin:%s_%s_changelist' % (app.lower(), name.lower())),
                'app': app,
                'app_label': ' '.join(map(lambda x: x.capitalize(), app.split('_'))),
                'app_parent': app_parent_label
            }
        )

    app_parent_list = set(module['app_parent'] for module in module_list)

    new_app_parent_list = list()
    for app_parent in app_parent_list:
        new_app_parent_list.append(
            {
                'name': app_parent,
                'label': ' '.join(map(lambda x: x.upper(), app_parent.split('_'))),
                'child': set(module['app'] for module in module_list
                             if module['app_parent'] == app_parent)
            }
        )

    app_label_list = dict()
    for app in set(module['app'] for module in module_list):
        app_label_list[app] = ' '.join(map(lambda x: x.capitalize(), app.split('_')))

    template = 'base/model_list.html'
    parameters = {
        'app_parent_list': new_app_parent_list,
        'app_label_list': app_label_list,
        'module_list': module_list
    }

    return render(request, template, parameters)