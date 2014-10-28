from datetime import datetime
import os
from django.conf.urls import url
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django import forms
from django.utils.encoding import force_unicode
from pandas.tseries.offsets import BDay
from pms_app import models
from pms_app.pos_app.models import PositionInstrument
from django.contrib.admin import widgets
from django.contrib.admin.models import LogEntry, ADDITION


# noinspection PyProtectedMember,PyMethodMayBeStatic
class InstrumentInline(admin.TabularInline):
    """
    Inline Position model inside Position Statement change view
    """
    model = PositionInstrument

    def instrument_link(self, instance):
        url_link = reverse('admin:%s_%s_change' % (instance._meta.app_label,
                                                   instance._meta.module_name),
                           args=(instance.id,))
        return '<a href="%s">View Position</a>' % url_link

    def position_statement_date(self, obj):
        return obj.position_statement.date

    instrument_link.allow_tags = True

    fields = (
        'position_statement_date', 'underlying', 'pct_change',
        'pl_open', 'pl_day', 'bp_effect', 'instrument_link'
    )

    readonly_fields = (
        'position_statement_date', 'underlying', 'pct_change',
        'pl_open', 'pl_day', 'bp_effect', 'instrument_link'
    )
    exclude = ('delta', 'gamma', 'theta', 'vega')
    extra = 0

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


def validate_filename(fname, validate_str):
    """
    Validate filename for all statements
    :param fname: str
    :param validate_str: str
    :return: None
    """
    if validate_str in fname:
        try:
            datetime.strptime(fname[:10], '%Y-%m-%d')
        except ValueError:
            raise forms.ValidationError('Incorrect file date: %s' % fname)

        if fname.split('.', 1)[1] != 'csv':
            raise forms.ValidationError('Incorrect file extension: %s' % fname)
    else:
        raise forms.ValidationError('Incorrect filename: %s' % fname)


class AccountStatementFile(forms.FileField):
    def validate(self, value):
        """
        Validate file name of account statement file
        :param value: dict
        """
        super(AccountStatementFile, self).validate(value)

        fname = os.path.basename(value.name)
        validate_filename(fname, 'AccountStatement')


class PositionStatementFile(forms.FileField):
    def validate(self, value):
        """
        Validate file name of position statement file
        :param value: dict
        """
        super(PositionStatementFile, self).validate(value)

        fname = os.path.basename(value.name)
        validate_filename(fname, 'PositionStatement')


class TradeActivityFile(forms.FileField):
    def validate(self, value):
        """
        Validate file name of position file
        :param value: dict
        """
        super(TradeActivityFile, self).validate(value)

        fname = os.path.basename(value.name)
        validate_filename(fname, 'TradeActivity')


class PmsImportStatementsForm(forms.Form):
    date = forms.DateField(
        widget=widgets.AdminDateWidget
    )

    account_statement = AccountStatementFile(
        label='Account Statement'
    )

    position_statement = PositionStatementFile(
        label='Position Statement'
    )

    trade_activity = TradeActivityFile(
        label='Trace Activity'
    )

    def clean(self):
        """
        Validate date for file date and all import file name date
        """
        cleaned_data = super(PmsImportStatementsForm, self).clean()

        if not len(self._errors):
            # no error found for field
            tomorrow = cleaned_data.get("date") + BDay(1)
            file_date = tomorrow.strftime('%Y-%m-%d')

            acc_date = cleaned_data.get("account_statement").name[:10]
            pos_date = cleaned_data.get("position_statement").name[:10]
            ta_date = cleaned_data.get("trade_activity").name[:10]

            if not (file_date == acc_date == pos_date == ta_date):
                error_message = 'All statement files must have (-1 biz day) as file date.'
                self._errors['date'] = self.error_class([error_message])


# noinspection PyMethodMayBeStatic
class UnderlyingAdmin(admin.ModelAdmin):
    inlines = [InstrumentInline]

    fieldsets = (
        ('Underlying', {
            'fields': ('symbol', 'company')
        }),
    )

    search_fields = ('symbol', 'company')

    list_per_page = 20
    ordering = ('symbol', )

    def has_add_permission(self, request):
        return False


# noinspection PyMethodMayBeStatic
class StatementAdmin(admin.ModelAdmin):
    def account_statement_detail(self, obj):
        acc = obj.account_statement
        output = "Line Count: %d<br>" % len(acc.split('\n'))
        output += "Account Summary Exists: %s<br>" % ('Account Summary' in acc)
        output += "Profits and Losses Exists: %s<br>" % ('Profits and Losses' in acc)
        output += "Account Trade History Exists: %s<br>" % ('Account Trade' in acc)
        output += "Account Order History Exists: %s<br>" % ('Account Order' in acc)
        output += "Cash Balance Exists: %s<br>" % ('Cash Balance' in acc)
        output += "Options Exists: %s<br>" % ('Options' in acc)
        output += "Stocks Exists: %s<br>" % ('Stocks' in acc)
        output += "Futures Statements Exists: %s<br>" % ('Futures Statements' in acc)
        output += "Forex Statements Exists: %s<br>" % ('Forex Statements' in acc)
        return output

    def position_statement_detail(self, obj):
        pos = obj.position_statement
        lines = pos.split('\n')

        instrument_count = 0
        stock_count = 0
        options_count = 0
        for line in lines:
            items = line.split(',')

            if len(items) == 14:
                first_item = items[0].split(' ')
                if ' ' not in items[0]:
                    instrument_count += 1
                elif first_item[0] not in ('100', '10'):
                    if first_item[-1] not in ('CALL', 'PUT'):
                        stock_count += 1
                elif first_item[0].isdigit():
                    if first_item[-1] in ('CALL', 'PUT'):
                        options_count += 1

        overall_count = sum(map(lambda x: True if len(x) else False, lines[-6:-1]))

        output = "Line Count: %d<br>" % len(lines)
        output += "Instrument Position Count: %s<br>" % instrument_count
        output += "Stock Position Count: %s<br>" % stock_count
        output += "Option Position Count: %s<br>" % options_count
        output += "Position Overall Count: %s<br>" % overall_count
        return output

    def trade_activity_detail(self, obj):
        ta = obj.trade_activity
        output = "Line Count: %d<br>" % len(ta.split('\n'))
        output += "Working Orders Exists: %s<br>" % ('Working Orders' in ta)
        output += "Filled Orders Exists: %s<br>" % ('Filled Orders' in ta)
        output += "Cancelled Orders Exists: %s<br>" % ('Cancelled Orders' in ta)
        output += "Rolling Strategies Exists: %s<br>" % ('Rolling Strategies' in ta)
        return output

    account_statement_detail.allow_tags = True
    position_statement_detail.allow_tags = True
    trade_activity_detail.allow_tags = True

    list_display = (
        'date', 'account_statement_detail',
        'position_statement_detail', 'trade_activity_detail'
    )

    fields = ('date', 'account_statement', 'position_statement', 'trade_activity')

    readonly_fields = ('date', )

    list_per_page = 5
    ordering = ('date', )

    def has_add_permission(self, request):
        return False

    def get_urls(self):
        urls = super(StatementAdmin, self).get_urls()
        my_urls = [
            url(
                r'^import_position_statement/$',
                self.import_position_statement,
                name='admin_import_position_statement',
            ),
            url(
                r'^import_position_statement/(?P<statement_id>\d)/$',
                self.import_position_statement,
                name='admin_import_position_statement',
            ),
        ]
        return my_urls + urls

    @staticmethod
    def import_position_statement(request, statement_id=0):
        # custom view which should return an HttpResponse
        # return HttpResponse('something')
        template = 'admin/pms_app/statement/import_position_statement.html'

        if request.method == 'POST':
            import_statement_form = PmsImportStatementsForm(request.POST, request.FILES)
            if import_statement_form.is_valid():
                statements = models.Statement(
                    date=request.POST['date'],
                    account_statement=request.FILES['account_statement'].read(),
                    position_statement=request.FILES['position_statement'].read(),
                    trade_activity=request.FILES['trade_activity'].read()
                )
                statements.save()
                # todo: later save all into model

                # log import
                LogEntry.objects.log_action(
                    user_id=request.user.id,
                    content_type_id=ContentType.objects.get_for_model(models.Statement).id,
                    object_id=statements.id,
                    object_repr=statements.__unicode__(),
                    action_flag=ADDITION
                )

                return HttpResponseRedirect(
                    #reverse('admin:pms_app_statement_change', args=(statements.id,))
                    reverse('admin:admin_import_position_statement',
                            kwargs=dict(statement_id=statements.id))
                )
        else:
            import_statement_form = PmsImportStatementsForm()

        parameters = dict(
            request=request,
            form=import_statement_form,
            statement_id=statement_id
        )

        return render(request, template, parameters)

#class PmsAppAdminSite(admin.AdminSite):
#    app_index_template = 'admin/pms_app/app_index.html'
admin.site.register(models.Underlying, UnderlyingAdmin)
admin.site.register(models.Statement, StatementAdmin)
admin.site.template = 'admin/pms_app/app_index.html'

#admin.site.app_index = PmsAppIndexAdmin

#admin_site = PmsAppAdminSite()
#admin_site.register(models.Underlying, UnderlyingAdmin)
# todo: next account model change, trade activity model change...