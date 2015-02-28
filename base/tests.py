from pprint import pprint
from django.contrib.contenttypes.models import ContentType
from django.db.models.base import ModelBase
from tos_import.classes.test import TestSetUp
from rivers.urls import *
from django.contrib import admin
from django.core.urlresolvers import reverse


# noinspection PyUnresolvedReferences
class TestBaseModelListing(TestSetUp):
    # todo: write better test
    def test123(self):
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

            module_list.append(
                {
                    'name': module.__name__,
                    'url': reverse('admin:%s_%s_changelist' % (app.lower(), module.__name__.lower())),
                    'app': app,
                    'app_label': ' '.join(map(lambda label: label.capitalize(), app.split('_'))),
                    'app_parent': app_parent_label
                }
            )

        app_parent_list = set(module['app_parent'] for module in module_list)

        new_app_parent_list = list()
        for app_parent in app_parent_list:
            new_app_parent_list.append(
                {
                    'name': app_parent,
                    'label': ' '.join(map(lambda label: label.upper(), app_parent.split('_'))),
                    'child': set(module['app'] for module in module_list
                                 if module['app_parent'] == app_parent)
                }
            )

        app_label_list = dict()
        for app in set(module['app'] for module in module_list):
            app_label_list[app] = ' '.join(map(lambda label: label.capitalize(), app.split('_')))

        pprint(module_list)

        for x in app_parent_list:
            print x

