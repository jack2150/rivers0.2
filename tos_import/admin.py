import os
from datetime import datetime
from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.forms import ModelForm
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django import forms
from pandas.tseries.offsets import BDay
from suit.widgets import AutosizedTextarea, SuitDateWidget
from tos_import import models
from tos_import.statement_account.models import SaveAccountStatement, AccountSummary
from tos_import.statement_position.models import SavePositionStatement, PositionSummary
from tos_import.statement_trade.models import SaveTradeActivity, TradeSummary
from django.contrib.admin.models import LogEntry, ADDITION
from stat_simple.models import SaveDayStat


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


class PmsImportStatementsForm(forms.Form):
    date = forms.DateField(
        # widget=widgets.AdminDateWidget
        widget=SuitDateWidget
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


@staff_member_required
def statement_import(request, statement_id=0):
    # custom view which should return an HttpResponse
    # return HttpResponse('something')
    # template = 'admin/tos_import/statement/import_state.html'
    template = 'admin/tos_import/statement/import.html'

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

            # save date stat
            SaveDayStat(statement).start()

            # log import
            LogEntry.objects.log_action(
                user_id=request.user.id,
                content_type_id=ContentType.objects.get_for_model(models.Statement).id,
                object_id=statement.id,
                object_repr=statement.__unicode__(),
                action_flag=ADDITION
            )

            return HttpResponseRedirect(
                # reverse('admin:pms_app_statement_change', args=(statements.id,))
                reverse('admin:statement_import', kwargs=dict(statement_id=statement.id))
            )
    else:
        import_statement_form = PmsImportStatementsForm()

    parameters = dict(
        request=request,
        form=import_statement_form,
        statement_id=statement_id
    )

    return render(request, template, parameters)


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


# noinspection PyMethodMayBeStatic,PyProtectedMember
class AccountStatementInline(admin.TabularInline):
    model = AccountSummary
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
    model = PositionSummary
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
    model = TradeSummary
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


class StatementForm(ModelForm):
    class Meta:
        widgets = {
            'date': SuitDateWidget(),
            'account_statement': AutosizedTextarea(attrs={'rows': 10, 'style': 'width:95%'}),
            'position_statement': AutosizedTextarea(attrs={'rows': 10, 'style': 'width:95%'}),
            'trade_activity': AutosizedTextarea(attrs={'rows': 10, 'style': 'width:95%'}),
        }


# noinspection PyMethodMayBeStatic
class StatementAdmin(admin.ModelAdmin):
    form = StatementForm

    def account_statement_detail(self, obj):
        acc = obj.account_statement
        output = "Line Count: %d, " % len(acc.split('\n'))
        output += "Account Summary Exists: %s, " % ('Account Summary' in acc)
        output += "Profits and Losses Exists: %s, " % ('Profits and Losses' in acc)
        output += "Account Trade History Exists: %s, " % ('Account Trade' in acc)
        output += "Account Order History Exists: %s, " % ('Account Order' in acc)
        output += "Cash Balance Exists: %s, " % ('Cash Balance' in acc)
        output += "Options Exists: %s, " % ('Options' in acc)
        output += "Stocks Exists: %s, " % ('Stocks' in acc)
        output += "Futures Statements Exists: %s, " % ('Futures Statements' in acc)
        output += "Forex Statements Exists: %s" % ('Forex Statements' in acc)
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

        output = "Line Count: %d, " % len(lines)
        output += "Instrument Position Count: %s, " % instrument_count
        output += "Stock Position Count: %s, " % stock_count
        output += "Option Position Count: %s, " % options_count
        output += "Position Overall Count: %s" % overall_count
        return output

    position_statement_detail.allow_tags = True
    position_statement_detail.short_description = 'Pos Detail'

    def trade_activity_detail(self, obj):
        ta = obj.trade_activity
        output = "Line Count: %d, " % len(ta.split('\n'))
        output += "Working Orders Exists: %s, " % ('Working Orders' in ta)
        output += "Filled Orders Exists: %s, " % ('Filled Orders' in ta)
        output += "Cancelled Orders Exists: %s, " % ('Cancelled Orders' in ta)
        output += "Rolling Strategies Exists: %s" % ('Rolling Strategies' in ta)
        return output

    trade_activity_detail.allow_tags = True
    trade_activity_detail.short_description = 'TA Detail'

    list_display = (
        'date', 'account_statement_detail',
        'position_statement_detail', 'trade_activity_detail'
    )

    def account_statement_link(self, obj):
        ta = AccountSummary.objects.get(id=obj.id)
        acc_url = reverse(
            'admin:statement_account_accountsummary_change', args=(ta.id,)
        )
        return '<a href="%s" style="display: block; width: 300px;">%s</a>' % (
            acc_url, 'View Account Statement'
        )

    account_statement_link.allow_tags = True
    account_statement_link.short_description = 'Acc Link'

    def position_statement_link(self, obj):
        ta = PositionSummary.objects.get(id=obj.id)
        pos_url = reverse(
            'admin:statement_position_positionsummary_change', args=(ta.id,)
        )
        return '<a href="%s" style="display: block; width: 300px;">%s</a>' % (
            pos_url, 'View Position Statement'
        )

    position_statement_link.allow_tags = True
    position_statement_link.short_description = 'Pos Link'

    def trade_activity_link(self, obj):
        ta = TradeSummary.objects.get(id=obj.id)
        ta_url = reverse(
            'admin:statement_trade_tradesummary_change', args=(ta.id,)
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
                'account_statement', 'account_statement_detail', 'account_statement_link',
                'position_statement', 'position_statement_detail', 'position_statement_link',
                'trade_activity', 'trade_activity_detail', 'trade_activity_link'
            )
        }),

    )

    readonly_fields = (
        'account_statement_detail', 'position_statement_detail',
        'trade_activity_detail', 'account_statement_link',
        'position_statement_link', 'trade_activity_link'
    )

    list_per_page = 5
    ordering = ('-date', )
    date_hierarchy = 'date'

    def has_add_permission(self, request):
        return False


admin.site.register(models.Statement, StatementAdmin)

admin.site.register(models.Underlying, UnderlyingAdmin)
admin.site.register(models.Future, FutureAdmin)
admin.site.register(models.Forex, ForexAdmin)

admin.site.register_view(
    'tos_import/statement/import/$',
    urlname='statement_import',
    view=statement_import
)
admin.site.register_view(
    'tos_import/statement/import/(?P<statement_id>\d+)/$',
    urlname='statement_import',
    view=statement_import
)