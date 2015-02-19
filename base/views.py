from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.contrib.contenttypes.models import ContentType


def base_models(request):
    """
    model list view same as dashboard
    different is using readable name
    :param request: request
    :return: render
    """
    custom_name = {
        'tos_import': 'PMS:Main',
        'statement_account': 'PMS:Account Statement',
        'statement_position': 'PMS:Position Statement',
        'statement_trade': 'PMS:Trade Activity',
        'stat_simple': 'STAT:Main',
    }

    cls_list = list()
    for ct in ContentType.objects.all():
        m = ct.model_class()
        if 'django' not in m.__module__:
            module = m.__module__.split('.')
            cls_list.append(
                dict(
                    app=module[-2],
                    parent=module[0],
                    name=m.__name__,
                )
            )

    models = dict()
    for cls in cls_list:
        if cls['parent'] not in models.keys():
            models[cls['parent']] = dict()

        if cls['app'] not in models[cls['parent']].keys():
            models[cls['parent']][cls['app']] = list()

        admin_url = reverse('admin:%s_%s_changelist' % (cls['app'].lower(), cls['name'].lower()))
        models[cls['parent']][cls['app']].append(
            dict(
                name=cls['name'],
                admin_url=admin_url,
            )
        )

    for key1 in models.keys():
        for key2 in models[key1]:
            models[key1][key2].sort()

    models = [(key, [(k, v, custom_name[k]) for k, v in value.items()])
              for key, value in models.items()]
    models.sort()

    template = 'admin/base/models.html'
    parameters = {
        'models': models
    }

    return render(request, template, parameters)