from django.contrib import admin
from django.core.urlresolvers import reverse
from pms_app.pos_app import models
import locale

locale.setlocale(locale.LC_ALL, '')


# noinspection PyProtectedMember,PyMethodMayBeStatic
class PositionInline(admin.TabularInline):
    """
    Inline Position model inside Position Statement change view
    """
    model = models.Instrument

    def instrument_link(self, instance):
        url = reverse('admin:%s_%s_change' % (instance._meta.app_label,
                                              instance._meta.module_name),
                      args=(instance.id,))
        return '<a href="%s">View Position</a>' % url

    instrument_link.allow_tags = True

    readonly_fields = ('underlying', 'pct_change', 'pl_open', 'pl_day', 'bp_effect', 'instrument_link')
    exclude = ('delta', 'gamma', 'theta', 'vega')
    extra = 0

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


# noinspection PyMethodMayBeStatic
class PositionStatementAdmin(admin.ModelAdmin):
    """
    Position Statement admin interface
    """
    inlines = [PositionInline, ]

    def currency_cash_sweep(self, obj):
        return locale.currency(obj.cash_sweep, grouping=True)

    def currency_available(self, obj):
        return locale.currency(obj.available, grouping=True)

    def currency_pl_ytd(self, obj):
        return locale.currency(obj.pl_ytd, grouping=True)

    def currency_futures_bp(self, obj):
        return locale.currency(obj.futures_bp, grouping=True)

    def currency_bp_adjustment(self, obj):
        return locale.currency(obj.bp_adjustment, grouping=True)

    currency_cash_sweep.short_description = 'Cash Sweep'
    currency_available.short_description = 'Dollar Available'
    currency_pl_ytd.short_description = 'PL YTD'
    currency_futures_bp.short_description = 'Futures BP'
    currency_bp_adjustment.short_description = 'BP Adjustment'

    list_display = ('date', 'currency_cash_sweep', 'currency_available', 'currency_pl_ytd')
    fieldsets = (
        ('Position Statement', {
            'fields': (
                'date',
                ('cash_sweep', 'available', 'pl_ytd',
                 'futures_bp', 'bp_adjustment')
            )
        }),
    )

    search_fields = ['date', 'available', 'pl_ytd']

    list_per_page = 20

    def has_add_permission(self, request):
        return False


class PositionStockInline(admin.TabularInline):
    """
    Position Stock inline for Position change view
    """
    model = models.InstrumentStock
    fields = (
        'quantity', 'mark', 'mark_change', 'pct_change',
        'pl_open', 'pl_day', 'bp_effect'
    )
    readonly_fields = (
        'quantity', 'mark', 'mark_change', 'pct_change',
        'pl_open', 'pl_day', 'bp_effect'
    )
    extra = 0

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False


class PositionOptionsInline(admin.TabularInline):
    """
    Position Options inline for Position change view
    """
    model = models.InstrumentOption
    extra = 0

    fields = (
        'quantity', 'days', 'trade_price', 'mark', 'mark_change', 'pct_change',
        'delta', 'gamma', 'theta', 'vega', 'pl_open', 'pl_day', 'bp_effect'
    )

    readonly_fields = (
        'quantity', 'days', 'trade_price', 'mark', 'mark_change', 'pct_change',
        'delta', 'gamma', 'theta', 'vega', 'pl_open', 'pl_day', 'bp_effect'
    )

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False


# noinspection PyMethodMayBeStatic
class PositionInstrumentAdmin(admin.ModelAdmin):
    """
    Position admin interface for Position model only
    """
    list_select_related = True

    inlines = [PositionStockInline, PositionOptionsInline]

    def position_statement_date(self, obj):
        return obj.position_statement.date

    def underlying_symbol(self, obj):
        return obj.underlying.symbol

    def profit_loss(self, obj):
        return True if obj.pl_open > 0 else False
    profit_loss.boolean = True
    profit_loss.short_description = 'P/L'

    list_display = (
        'position_statement_date', 'underlying_symbol', 'pct_change',
        'pl_open', 'pl_day', 'profit_loss'
    )

    fieldsets = (
        ('Position Instrument', {
            'fields': (
                ('position_statement', 'underlying'),
                ('delta', 'gamma', 'theta', 'vega'),
                ('pct_change', 'pl_open', 'pl_day', 'bp_effect')
            )
        }),
    )

    list_per_page = 30
    search_fields = ['position_statement__date', 'underlying__symbol']
    list_filter = ['position_statement__date']

    def has_add_permission(self, request):
        return False


# noinspection PyMethodMayBeStatic
class PositionStockAdmin(admin.ModelAdmin):
    def position_statement_date(self, obj):
        return obj.position_statement.date

    list_display = (
        'position_statement_date', 'underlying',  'quantity',
        'pct_change', 'pl_open', 'pl_day', 'bp_effect'
    )

    list_per_page = 30

    search_fields = ('position_statement__date', 'underlying__symbol')

    def has_add_permission(self, request):
        return False


# noinspection PyMethodMayBeStatic
class PositionOptionAdmin(admin.ModelAdmin):
    list_per_page = 30

    def position_statement_date(self, obj):
        return obj.position_statement.date

    def option(self, obj):
        return obj.__unicode__().split('<Option>')[-1]

    list_display = (
        'position_statement_date', 'option', 'quantity', 'days',
        'trade_price', 'pct_change', 'pl_open', 'pl_day'
    )

    fieldsets = (
        ('Option', {
            'fields': (
                'position_statement', 'underlying', 'instrument',
                ('quantity', 'days', 'mark', 'mark_change'),
                ('delta', 'gamma', 'theta', 'vega'),
                ('pct_change', 'pl_open', 'pl_day', 'bp_effect')
            )
        }),
    )

    search_fields = ['position_statement__date', 'underlying__symbol']

    def has_add_permission(self, request):
        return False


admin.site.register(models.PositionStatement, PositionStatementAdmin)
admin.site.register(models.Instrument, PositionInstrumentAdmin)
admin.site.register(models.InstrumentStock, PositionStockAdmin)
admin.site.register(models.InstrumentOption, PositionOptionAdmin)







