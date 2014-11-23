import os
from datetime import datetime
from django.conf.urls import url
from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django import forms
from pandas.tseries.offsets import BDay
from app_pms import models
from app_pms.app_acc.models import SaveAccountStatement, AccountStatement
from app_pms.app_pos.models import SavePositionStatement, PositionStatement
from app_pms.app_ta.models import SaveTradeActivity, TradeActivity
from django.contrib.admin import widgets
from django.contrib.admin.models import LogEntry, ADDITION


# noinspection PyMethodMayBeStatic
class UnderlyingAdmin(admin.ModelAdmin):
    list_display = ('symbol', 'company')

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
class FutureAdmin(admin.ModelAdmin):
    list_display = ('lookup', 'symbol', 'description', 'expire_date', 'session', 'spc')

    fieldsets = (
        ('Future', {
            'fields': ('lookup', 'symbol', 'description', 'expire_date', 'session', 'spc')
        }),
    )

    search_fields = ('lookup', 'symbol', 'description', 'expire_date', 'session', 'spc')

    list_per_page = 20
    ordering = ('lookup', 'symbol')

    def has_add_permission(self, request):
        return False


# noinspection PyMethodMayBeStatic
class ForexAdmin(admin.ModelAdmin):
    list_display = ('symbol', 'description')

    fieldsets = (
        ('Forex', {
            'fields': ('symbol', 'description')
        }),
    )

    search_fields = ('symbol', 'description')

    list_per_page = 20
    ordering = ('symbol', )

    def has_add_permission(self, request):
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
            file_date = cleaned_data.get("date").strftime('%Y-%m-%d')

            acc_date = datetime.strptime(
                cleaned_data.get("account_statement").name[:10], '%Y-%m-%d'
            )
            pos_date = datetime.strptime(
                cleaned_data.get("position_statement").name[:10], '%Y-%m-%d'
            )
            ta_date = datetime.strptime(
                cleaned_data.get("trade_activity").name[:10], '%Y-%m-%d'
            )

            acc_date = acc_date - BDay(1)
            acc_date = acc_date.strftime('%Y-%m-%d')
            pos_date = pos_date - BDay(1)
            pos_date = pos_date.strftime('%Y-%m-%d')
            ta_date = ta_date - BDay(1)
            ta_date = ta_date.strftime('%Y-%m-%d')

            if acc_date == pos_date == ta_date:
                if file_date != acc_date:
                    error_message = 'All date must have (-1 BDay, %s != %s).' % (file_date, acc_date)
                    self._errors['date'] = self.error_class([error_message])
            else:
                error_message = 'All file date must be same.'
                self._errors['date'] = self.error_class([error_message])


# noinspection PyMethodMayBeStatic,PyProtectedMember
class AccountStatementInline(admin.TabularInline):
    model = AccountStatement
    extra = 0

    def account_statement_link(self, instance):
        pos_url = reverse(
            'admin:%s_%s_change' %
            (instance._meta.app_label, instance._meta.module_name),
            args=(instance.id,)
        )
        return '<a href="%s">View Position Statement</a>' % pos_url

    account_statement_link.allow_tags = True

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    readonly_fields = (
        'date', 'net_liquid_value', 'stock_buying_power', 'option_buying_power',
        'commissions_ytd', 'futures_commissions_ytd', 'account_statement_link'
    )


# noinspection PyProtectedMember,PyMethodMayBeStatic
class PositionStatementInline(admin.TabularInline):
    model = PositionStatement
    extra = 0

    def position_statement_link(self, instance):
        pos_url = reverse(
            'admin:%s_%s_change' %
            (instance._meta.app_label, instance._meta.module_name),
            args=(instance.id,)
        )
        return '<a href="%s">View Position Statement</a>' % pos_url

    position_statement_link.allow_tags = True

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    readonly_fields = (
        'date', 'cash_sweep', 'pl_ytd', 'futures_bp', 'bp_adjustment',
        'available', 'position_statement_link'
    )


# noinspection PyMethodMayBeStatic,PyProtectedMember
class TradeActivityInline(admin.TabularInline):
    model = TradeActivity
    extra = 0

    def trade_activity_link(self, instance):
        x = 'admin:%s_%s_change' % (instance._meta.app_label, instance._meta.module_name)
        pos_url = reverse(
            'admin:%s_%s_change' %
            (instance._meta.app_label, instance._meta.module_name),
            args=(instance.id,)
        )
        return '<a href="%s">View Trade Activity</a> %s' % (pos_url, x)

    trade_activity_link.allow_tags = True
    trade_activity_link.verbose_name = 'Module'

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    readonly_fields = ('date', 'trade_activity_link')


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

    account_statement_detail.allow_tags = True
    account_statement_detail.short_description = 'Acc Detail'

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

    position_statement_detail.allow_tags = True
    position_statement_detail.short_description = 'Pos Detail'

    def trade_activity_detail(self, obj):
        ta = obj.trade_activity
        output = "Line Count: %d<br>" % len(ta.split('\n'))
        output += "Working Orders Exists: %s<br>" % ('Working Orders' in ta)
        output += "Filled Orders Exists: %s<br>" % ('Filled Orders' in ta)
        output += "Cancelled Orders Exists: %s<br>" % ('Cancelled Orders' in ta)
        output += "Rolling Strategies Exists: %s<br>" % ('Rolling Strategies' in ta)
        return output

    trade_activity_detail.allow_tags = True
    trade_activity_detail.short_description = 'TA Detail'

    list_display = (
        'date', 'account_statement_detail',
        'position_statement_detail', 'trade_activity_detail'
    )

    def account_statement_link(self, obj):
        ta = AccountStatement.objects.get(id=obj.id)
        acc_url = reverse(
            'admin:app_acc_accountstatement_change', args=(ta.id,)
        )
        return '<a href="%s" style="display: block; width: 300px;">%s</a>' % (
            acc_url, 'View Account Statement'
        )

    account_statement_link.allow_tags = True
    account_statement_link.short_description = 'Acc Link'

    def position_statement_link(self, obj):
        ta = PositionStatement.objects.get(id=obj.id)
        pos_url = reverse(
            'admin:app_pos_positionstatement_change', args=(ta.id,)
        )
        return '<a href="%s" style="display: block; width: 300px;">%s</a>' % (
            pos_url, 'View Position Statement'
        )

    position_statement_link.allow_tags = True
    position_statement_link.short_description = 'Pos Link'

    def trade_activity_link(self, obj):
        ta = TradeActivity.objects.get(id=obj.id)
        ta_url = reverse(
            'admin:app_ta_tradeactivity_change', args=(ta.id,)
        )
        return '<a href="%s" style="display: block; width: 300px;">%s</a>' % (
            ta_url, 'View Trade Activity'
        )

    trade_activity_link.allow_tags = True
    trade_activity_link.short_description = 'TA Link'

    fieldsets = (
        ('Date', {
            'fields': ('date', )
        }),
        ('Statements', {
            'fields': (
                ('account_statement', 'account_statement_detail', 'account_statement_link'),
                ('position_statement', 'position_statement_detail', 'position_statement_link'),
                ('trade_activity', 'trade_activity_detail', 'trade_activity_link')
            )
        }),

    )

    readonly_fields = (
        'date', 'account_statement_detail', 'position_statement_detail',
        'trade_activity_detail', 'account_statement_link',
        'position_statement_link', 'trade_activity_link'
    )

    list_per_page = 5
    ordering = ('-date', )
    date_hierarchy = 'date'

    def has_add_permission(self, request):
        return False

    def get_urls(self):
        urls = super(StatementAdmin, self).get_urls()
        my_urls = [
            url(
                r'^import_statements/$',
                self.import_statement,
                name='import_statement',
            ),
            url(
                r'^import_statements/(?P<statement_id>\d)/$',
                self.import_statement,
                name='import_statement',
            ),
        ]
        return my_urls + urls

    @staticmethod
    @staff_member_required
    def import_statement(request, statement_id=0):
        # custom view which should return an HttpResponse
        # return HttpResponse('something')
        template = 'admin/app_pms/statement/import_statement.html'

        if request.method == 'POST':
            import_statement_form = PmsImportStatementsForm(request.POST, request.FILES)
            if import_statement_form.is_valid():
                date = request.POST['date']
                acc_data = request.FILES['account_statement'].read()
                pos_data = request.FILES['position_statement'].read()
                ta_data = request.FILES['trade_activity'].read()

                statement = models.Statement(
                    date=date,
                    account_statement=acc_data,
                    position_statement=pos_data,
                    trade_activity=ta_data
                )
                statement.save()

                # save acc, pos, ta into db

                SaveAccountStatement(
                    date=date,
                    statement=statement,
                    file_data=acc_data
                ).save_all()

                SavePositionStatement(
                    date=date,
                    statement=statement,
                    file_data=pos_data
                ).save_all()

                SaveTradeActivity(
                    date=date,
                    statement=statement,
                    file_data=ta_data
                ).save_all()

                # log import
                LogEntry.objects.log_action(
                    user_id=request.user.id,
                    content_type_id=ContentType.objects.get_for_model(models.Statement).id,
                    object_id=statement.id,
                    object_repr=statement.__unicode__(),
                    action_flag=ADDITION
                )

                return HttpResponseRedirect(
                    #reverse('admin:pms_app_statement_change', args=(statements.id,))
                    reverse('admin:import_statement', kwargs=dict(statement_id=statement.id))
                )
        else:
            import_statement_form = PmsImportStatementsForm()

        parameters = dict(
            request=request,
            form=import_statement_form,
            statement_id=statement_id
        )

        return render(request, template, parameters)


admin.site.register(models.Statement, StatementAdmin)

admin.site.register(models.Underlying, UnderlyingAdmin)
admin.site.register(models.Future, FutureAdmin)
admin.site.register(models.Forex, ForexAdmin)

#admin.site.template = 'admin/app_pms/app_index.html'
