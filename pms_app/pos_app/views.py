from django.contrib.auth.decorators import permission_required
from django.shortcuts import render, render_to_response
from django.template import RequestContext


# custom admin view
@permission_required('blog.add_post')
def admin_import_pos_csv(request, model_admin):
    """
    Import Position CSV File View
    :param model_admin: model_admin
    :param request: Dict
    :return: Render
    """
    opts = model_admin.model._meta
    admin_site = model_admin.admin_site
    has_perm = request.user.has_perm(opts.app_label + '.' + opts.get_change_permission())

    context = {
        'admin_site': admin_site.name,
        'title': "My Custom View",
        'opts': opts,
        'root_path': '/%s' % admin_site.root_path,
        'app_label': opts.app_label,
        'has_change_permission': has_perm
    }

    template = 'admin/pms_app/pos_app/import_pos_csv.html'
    return render_to_response(template, context, context_instance = RequestContext(request))