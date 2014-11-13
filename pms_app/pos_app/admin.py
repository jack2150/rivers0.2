from django.contrib import admin
from django.core.urlresolvers import reverse
from pms_app.pos_app import models
import locale

locale.setlocale(locale.LC_ALL, '')


# noinspection PyMethodMayBeStatic,PyProtectedMember
class PositionStatementInline(admin.TabularInline):
    def link(self, instance):
        url = reverse(
            'admin:%s_%s_change' % (
                instance._meta.app_label, instance._meta.module_name
            ),
            args=(instance.id,)
        )
        return '<a href="%s">Change</a>' % url

    link.allow_tags = True
    link.short_description = 'Action'

    extra = 0

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


# noinspection PyProtectedMember,PyMethodMayBeStatic
class PositionInline(PositionStatementInline):
    """
    Inline Position model inside Position Statement change view
    """
    model = models.Instrument

    def formatted_pl_open(self, obj):
        return '%+.2f' % obj.pl_open

    def formatted_pl_day(self, obj):
        return '%+.2f' % obj.pl_day

    def profit_loss(self, obj):
        return True if obj.pl_open >= 0 else False
    profit_loss.boolean = True
    profit_loss.short_description = 'P/L'

    formatted_pl_open.short_description = 'P/L Open'
    formatted_pl_day.short_description = 'P/L Day'

    fields = (
        'underlying', 'delta', 'gamma', 'theta', 'vega',
        'pct_change', 'formatted_pl_open', 'formatted_pl_day',
        'bp_effect', 'profit_loss', 'link'
    )

    readonly_fields = (
        'underlying', 'delta', 'gamma', 'theta', 'vega',
        'pct_change', 'formatted_pl_open', 'formatted_pl_day',
        'bp_effect', 'profit_loss', 'link'
    )
    #exclude = ('delta', 'gamma', 'theta', 'vega')
    extra = 0

    ordering = ('underlying', )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


# noinspection PyMethodMayBeStatic
class PositionStatementAdmin(admin.ModelAdmin):
    """
    Position Statement admin interface
    """
    inlines = (PositionInline, )

    def position_statement_date(self, obj):
        return obj.date.strftime('%Y-%m-%d')

    def instruments(self, obj):
        return models.Instrument.objects.filter(position_statement=obj).count()

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
    position_statement_date.short_description = 'Date'

    list_display = (
        'position_statement_date', 'currency_cash_sweep', 'currency_available',
        'currency_pl_ytd', 'currency_futures_bp', 'currency_bp_adjustment', 'instruments'
    )

    fieldsets = (
        ('Foreign Key', {
            'fields': (
                'statement',
            )
        }),
        ('Position Statement', {
            'fields': (
                'date',
                ('cash_sweep', 'available', 'pl_ytd'),
                ('futures_bp', 'bp_adjustment')
            )
        }),
    )

    readonly_fields = ('statement', 'date')

    search_fields = ['date', 'available', 'pl_ytd']

    date_hierarchy = 'date'

    list_per_page = 20

    def has_add_permission(self, request):
        return False


class PositionStockInline(PositionStatementInline):
    """
    Position Stock inline for Position change view
    """
    model = models.InstrumentStock

    fields = (
        'quantity', 'trade_price', 'mark', 'mark_change', 'pct_change',
        'pl_open', 'pl_day', 'bp_effect', 'link'
    )
    readonly_fields = (
        'quantity', 'trade_price', 'mark', 'mark_change', 'pct_change',
        'pl_open', 'pl_day', 'bp_effect', 'link'
    )

    verbose_name_plural = 'Stock'


class PositionOptionsInline(PositionStatementInline):
    """
    Position Options inline for Position change view
    """
    model = models.InstrumentOption

    fields = (
        'quantity', 'days', 'trade_price', 'mark', 'mark_change', 'pct_change',
        'delta', 'gamma', 'theta', 'vega', 'pl_open', 'pl_day', 'bp_effect', 'link'
    )

    readonly_fields = (
        'quantity', 'days', 'trade_price', 'mark', 'mark_change', 'pct_change',
        'delta', 'gamma', 'theta', 'vega', 'pl_open', 'pl_day', 'bp_effect', 'link'
    )

    verbose_name_plural = 'Options'


class ProfitLossListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = 'Profit Loss'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'profit_loss'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('profit', 'Profit'),
            ('loss', 'Loss'),
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.
        if self.value() == 'profit':
            return queryset.filter(pl_open__gte=0)
        if self.value() == 'loss':
            return queryset.filter(pl_open__lt=0)


# noinspection PyMethodMayBeStatic
class PositionInstrumentAdmin(admin.ModelAdmin):
    """
    Position admin interface for Position model only
    """
    list_select_related = True

    inlines = [PositionStockInline, PositionOptionsInline]

    def position_statement_date(self, obj):
        return obj.position_statement.date.strftime('%Y-%m-%d')

    def underlying_symbol(self, obj):
        return obj.underlying.symbol

    def profit_loss(self, obj):
        return True if obj.pl_open >= 0 else False
    profit_loss.boolean = True
    profit_loss.short_description = 'P/L'

    list_display = (
        'position_statement_date', 'underlying_symbol', 'pct_change',
        'pl_open', 'pl_day', 'profit_loss'
    )

    fieldsets = (
        ('Foreign Key', {
            'classes': ('wide', ),
            'fields': (
                ('position_statement', 'underlying')
            )
        }),
        ('Instrument', {
            'fields': (
                ('delta', 'gamma', 'theta', 'vega'),
                ('pct_change', 'pl_open', 'pl_day', 'bp_effect')
            )
        }),
    )

    readonly_fields = ('position_statement', 'underlying')

    list_per_page = 30
    search_fields = ('position_statement__date', 'underlying__symbol')
    list_filter = ('position_statement__date', ProfitLossListFilter)

    ordering = ('-position_statement__date', 'underlying__symbol')

    def has_add_permission(self, request):
        return False


# noinspection PyMethodMayBeStatic
class PositionStockAdmin(admin.ModelAdmin):
    def position_statement_date(self, obj):
        return obj.position_statement.date.strftime('%Y-%m-%d')
    position_statement_date.short_description = 'Date'

    list_display = (
        'position_statement_date', 'underlying',
        'quantity', 'trade_price', 'mark', 'mark_change',
        'pct_change', 'pl_open', 'pl_day', 'bp_effect'
    )

    fieldsets = (
        ('Foreign Key', {
            'classes': ('wide', 'collapse', 'open'),
            'fields': ('position_statement', 'underlying', 'instrument')
        }),
        ('Stock', {
            'fields': (
                ('trade_price', 'mark', 'mark_change', 'quantity'),
                ('pct_change', 'pl_open', 'pl_day', 'bp_effect')
            )
        }),
    )

    readonly_fields = (
        'position_statement', 'underlying', 'instrument'
    )

    list_per_page = 30
    ordering = ('-position_statement__date', 'underlying__symbol')

    search_fields = ('position_statement__date', 'underlying__symbol')

    def has_add_permission(self, request):
        return False


# noinspection PyMethodMayBeStatic
class PositionOptionAdmin(admin.ModelAdmin):
    list_per_page = 30

    def position_statement_date(self, obj):
        return obj.position_statement.date.strftime('%Y-%m-%d')

    def option(self, obj):
        return obj.__unicode__().split('>')[-1]

    list_display = (
        'position_statement_date', 'option',
        'quantity', 'days', 'mark', 'mark_change',
        'delta', 'gamma', 'theta', 'vega',
        'pct_change', 'pl_open', 'pl_day', 'bp_effect'
    )

    list_filter = (
        'position_statement__date',
        'right', 'special', 'ex_month', 'ex_year', 'contract'
    )

    search_fields = (
        'position_statement__date', 'underlying__symbol',
        'right', 'special', 'ex_month', 'ex_year', 'strike_price', 'contract'
    )

    fieldsets = (
        ('Foreign Key', {
            'classes': ('wide', 'collapse', 'open'),
            'fields': ('position_statement', 'underlying', 'instrument')
        }),
        ('Detail', {
            'fields': (
                ('mark', 'mark_change', 'trade_price', 'quantity', 'days'),
                ('delta', 'gamma', 'theta', 'vega'),
                ('pct_change', 'pl_open', 'pl_day', 'bp_effect')
            )
        }),
        ('Option', {
            'fields': (
                'right', 'special', 'ex_month',
                'ex_year', 'strike_price', 'contract'
            )
        }),
    )

    readonly_fields = (
        'position_statement', 'underlying', 'instrument'
    )

    def has_add_permission(self, request):
        return False



admin.site.register(models.PositionStatement, PositionStatementAdmin)
admin.site.register(models.Instrument, PositionInstrumentAdmin)
admin.site.register(models.InstrumentStock, PositionStockAdmin)
admin.site.register(models.InstrumentOption, PositionOptionAdmin)




# todo: update to better interface


# todo: support for future