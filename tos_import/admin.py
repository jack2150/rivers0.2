from django.contrib import admin
from django.core.urlresolvers import reverse
from django.forms import ModelForm
from django import forms
from tos_import.models import Statement, Underlying, Future, Forex
from tos_import.statement.statement_account.models import AccountSummary
from tos_import.statement.statement_position.models import PositionSummary
from tos_import.statement.statement_trade.models import TradeSummary
from tos_import.views import statement_import, statement_import_all


class UnderlyingAdmin(admin.ModelAdmin):
    list_display = ('symbol', 'company')

    fieldsets = (
        ('Underlying', {
            'fields': ('symbol', 'company')
        }),
    )

    search_fields = ('symbol', 'company')

    list_per_page = 30
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

    list_per_page = 30
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

    list_per_page = 30
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
    date = forms.DateField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )

    account_statement = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control'})
    )

    position_statement = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control'})
    )

    trade_activity = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control'})
    )


# noinspection PyMethodMayBeStatic
class StatementAdmin(admin.ModelAdmin):
    form = StatementForm

    def formatted_date(self, obj):
        return obj.date.strftime('%Y-%m-%d')

    formatted_date.short_description = 'Date'

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
        'formatted_date', 'account_statement_detail',
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
        ('Import Date', {
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

    list_per_page = 10
    ordering = ('-date', )
    date_hierarchy = 'date'

    def has_add_permission(self, request):
        return False


admin.site.register(Statement, StatementAdmin)
admin.site.register(Underlying, UnderlyingAdmin)
admin.site.register(Future, FutureAdmin)
admin.site.register(Forex, ForexAdmin)

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

admin.site.register_view(
    'tos_import/statement/import/all/$',
    urlname='statement_import_all',
    view=statement_import_all
)