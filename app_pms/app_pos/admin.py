from django.contrib import admin
from django.core.urlresolvers import reverse
from django.db.models import Q
from app_pms.app_pos import models
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


# noinspection PyMethodMayBeStatic
class PositionStatementInlinePL(PositionStatementInline):
    def formatted_pl_open(self, obj):
        return '%+.2f' % obj.pl_open

    def formatted_pl_day(self, obj):
        return '%+.2f' % obj.pl_day

    def profit_loss(self, obj):
        if obj.pl_open > 0:
            result = True
        elif obj.pl_open < 0:
            result = False
        else:
            result = None
        return result

    profit_loss.boolean = True
    profit_loss.short_description = 'P/L'

    formatted_pl_open.short_description = 'P/L Open'
    formatted_pl_day.short_description = 'P/L Day'


# noinspection PyProtectedMember,PyMethodMayBeStatic
class PositionInstrumentInline(PositionStatementInlinePL):
    """
    Inline Position model inside Position Statement change view
    """
    model = models.PositionInstrument

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


# noinspection PyProtectedMember,PyMethodMayBeStatic
class PositionFutureInline(PositionStatementInlinePL):
    """
    Inline Position model inside Position Statement change view
    """
    model = models.PositionFuture

    fields = (
        'future', 'quantity', 'days', 'trade_price',
        'mark', 'mark_change', 'pct_change', 'pl_open', 'pl_day', 'bp_effect',
        'profit_loss', 'link'
    )

    readonly_fields = (
        'future', 'quantity', 'days', 'trade_price',
        'mark', 'mark_change', 'pct_change', 'pl_open', 'pl_day', 'bp_effect',
        'profit_loss', 'link'
    )
    # exclude = ('delta', 'gamma', 'theta', 'vega')
    extra = 0

    ordering = ('future', )


# noinspection PyProtectedMember,PyMethodMayBeStatic
class PositionForexInline(PositionStatementInlinePL):
    """
    Inline Position model inside Position Statement change view
    """
    model = models.PositionForex

    fields = (
        'forex', 'quantity', 'trade_price', 'mark', 'mark_change',
        'pct_change', 'pl_open', 'pl_day', 'bp_effect',
        'profit_loss', 'link'
    )

    readonly_fields = (
        'forex', 'quantity', 'trade_price', 'mark', 'mark_change',
        'pct_change', 'pl_open', 'pl_day', 'bp_effect',
        'profit_loss', 'link'
    )
    # exclude = ('delta', 'gamma', 'theta', 'vega')
    extra = 0

    ordering = ('forex', )


# noinspection PyMethodMayBeStatic
class PositionStatementAdmin(admin.ModelAdmin):
    """
    Position Statement admin interface
    """
    inlines = (PositionInstrumentInline, PositionFutureInline, PositionForexInline)

    def position_statement_date(self, obj):
        return obj.date.strftime('%Y-%m-%d')

    def instruments(self, obj):
        return models.PositionInstrument.objects.filter(position_statement=obj).count()

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
    model = models.PositionEquity

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
    model = models.PositionOption

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
        return (
            ('profit', 'Profit'),
            ('loss', 'Loss'),
            ('even', 'Even'),
        )

    def queryset(self, request, queryset):
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.
        if self.value() == 'profit':
            return queryset.filter(pl_open__gt=0)
        if self.value() == 'loss':
            return queryset.filter(pl_open__lt=0)
        if self.value() == 'even':
            return queryset.filter(pl_open=0)


# noinspection PyMethodMayBeStatic,PyProtectedMember
class PsModelAdmin(admin.ModelAdmin):
    def position_statement_date(self, obj):
        return obj.position_statement.date.strftime('%Y-%m-%d')

    position_statement_date.short_description = 'Date'

    def symbol(self, obj):
        url = reverse(
            'admin:%s_%s_change' % (
                obj.underlying._meta.app_label,
                obj.underlying._meta.module_name
            ),
            args=(obj.underlying.id,)
        )

        return '<a href="%s">%s</a>' % (url, obj.underlying.symbol)

    symbol.allow_tags = True

    def description(self, obj):
        return obj.underlying.company

    def profit_loss(self, obj):
        if obj.pl_open > 0:
            result = True
        elif obj.pl_open < 0:
            result = False
        else:
            result = None
        return result

    profit_loss.boolean = True
    profit_loss.short_description = 'P/L'

    list_per_page = 30

    def has_add_permission(self, request):
        return False


class SpreadTypeListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = 'Position Type'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'position type'

    def lookups(self, request, model_admin):
        return (
            ('closed', 'Closed'),
            ('equity', 'Equity Only'),
            ('hedge', 'Hedge Strategy'),
            ('one_leg', 'One Leg Option'),
            ('two_leg', 'Two Leg Options'),
            ('three_leg', 'Three Leg Options'),
            ('four_leg', 'Four Leg Options'),
            ('custom', 'Custom'),
        )

    def queryset(self, request, queryset):
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.
        if self.value() == 'closed':
            # equity = 0 and options = 0
            pass
        elif self.value() == 'equity':
            pass
        elif self.value() == 'hedge':
            pass

        result = queryset.all()

        return result

# todo: until here... search equity and options quantity


# noinspection PyMethodMayBeStatic
class PositionInstrumentAdmin(PsModelAdmin):
    """
    Position admin interface for Position model only
    """
    list_select_related = True

    inlines = [PositionStockInline, PositionOptionsInline]

    def equity(self, obj):
        return models.PositionEquity.objects.\
            filter(instrument=obj).exclude(quantity=0).count()

    def options(self, obj):
        return models.PositionOption.objects.\
            filter(instrument=obj).exclude(quantity=0).count()

    list_display = (
        'position_statement_date', 'symbol', 'description', 'pct_change',
        'delta', 'gamma', 'theta', 'vega',
        'pct_change', 'pl_open', 'profit_loss', 'pl_day', 'bp_effect',
        'equity', 'options'
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

    search_fields = (
        'position_statement__date', 'underlying__symbol', 'underlying__company'
    )
    list_filter = (
        'position_statement__date', SpreadTypeListFilter, ProfitLossListFilter
    )
    ordering = ('-position_statement__date', 'underlying__symbol')


class QuantityListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = 'Quantity'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'quantity'

    def lookups(self, request, model_admin):
        return (
            ('opened', 'Opened'),
            ('closed', 'Closed'),
        )

    def queryset(self, request, queryset):
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.
        if self.value() == 'opened':
            return queryset.filter(quantity__gt=0)
        elif self.value() == 'closed':
            return queryset.filter(quantity=0)


# noinspection PyMethodMayBeStatic
class PositionEquityAdmin(PsModelAdmin):
    list_display = (
        'position_statement_date', 'symbol', 'description', 'quantity',
        'trade_price', 'mark', 'mark_change', 'pct_change',
        'pl_open', 'profit_loss', 'pl_day', 'bp_effect'
    )

    list_filter = (
        'position_statement__date', ProfitLossListFilter, QuantityListFilter
    )

    fieldsets = (
        ('Foreign Key', {
            'classes': ('wide', 'collapse', 'open'),
            'fields': ('position_statement', 'instrument', 'underlying')
        }),
        ('Stock', {
            'fields': (
                ('trade_price', 'mark', 'mark_change', 'quantity'),
                ('pct_change', 'pl_open', 'pl_day', 'bp_effect')
            )
        }),
    )

    readonly_fields = (
        'position_statement', 'instrument', 'underlying'
    )

    search_fields = (
        'position_statement__date', 'underlying__symbol', 'underlying__company'
    )
    ordering = ('-position_statement__date', 'underlying__symbol')


class DteListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = 'DTE'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'dte'

    def lookups(self, request, model_admin):
        return (
            ('>30', '30 above'),
            ('16-30', '16 until 30'),
            ('0-15', 'below 15'),
        )

    def queryset(self, request, queryset):
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.
        if self.value() == '>30':
            return queryset.filter(days__gt=30)
        if self.value() == '16-30':
            return queryset.filter(Q(days__gte=16) & Q(days__lt=30))
        if self.value() == '0-15':
            return queryset.filter(days__lte=15)


# noinspection PyMethodMayBeStatic
class PositionOptionAdmin(PsModelAdmin):
    def option(self, obj):
        return obj.__unicode__().split('>')[-1]

    list_display = (
        'position_statement_date', 'symbol', 'option',
        'quantity', 'days', 'mark', 'mark_change',
        'delta', 'gamma', 'theta', 'vega', 'pct_change',
        'pl_open', 'profit_loss', 'pl_day', 'bp_effect'
    )

    list_filter = (
        'position_statement__date',
        ProfitLossListFilter, DteListFilter, QuantityListFilter,
        'right', 'special', 'contract',
    )

    search_fields = (
        'position_statement__date', 'underlying__symbol', 'underlying__company',
        'right', 'special', 'ex_month', 'ex_year', 'strike', 'contract'
    )

    fieldsets = (
        ('Foreign Key', {
            'classes': ('wide', 'collapse', 'open'),
            'fields': ('position_statement', 'instrument', 'underlying')
        }),
        ('Detail', {
            'fields': (
                ('quantity', 'days'),
                ('mark', 'mark_change', 'trade_price'),
                ('delta', 'gamma', 'theta', 'vega'),
                ('pct_change', 'pl_open', 'pl_day', 'bp_effect')
            )
        }),
        ('Option', {
            'fields': (
                'right', 'special', 'ex_month',
                'ex_year', 'strike', 'contract'
            )
        }),
    )

    readonly_fields = (
        'position_statement', 'instrument', 'underlying'
    )
    ordering = ('-position_statement__date', 'underlying__symbol')


# noinspection PyMethodMayBeStatic,PyProtectedMember
class PositionFutureAdmin(PsModelAdmin):
    def future_link(self, obj):
        url = reverse(
            'admin:%s_%s_change' % (
                obj.future._meta.app_label,
                obj.future._meta.module_name
            ),
            args=(obj.future.id,)
        )
        return '<a href="%s">%s</a>' % (url, obj.future.symbol)

    future_link.allow_tags = True
    future_link.short_description = 'Futures'

    def description(self, obj):
        return obj.future.description

    list_display = (
        'position_statement_date', 'future_link', 'description',
        'quantity', 'days', 'trade_price', 'mark', 'mark_change', 'pct_change',
        'pl_open', 'profit_loss', 'pl_day', 'bp_effect'
    )

    list_filter = (
        'position_statement__date', ProfitLossListFilter
    )

    search_fields = (
        'position_statement__date', 'future__symbol', 'future__lookup',
        'future__description', 'future__spc', 'future__expire_date'
    )

    fieldsets = (
        ('Foreign Key', {
            'classes': ('wide', 'collapse', 'open'),
            'fields': ('position_statement', 'future')
        }),
        ('Detail', {
            'fields': (
                'quantity', 'days', 'trade_price', 'mark', 'mark_change',
                'pct_change', 'pl_open', 'pl_day', 'bp_effect'
            )
        }),
    )

    readonly_fields = (
        'position_statement', 'future'
    )
    ordering = ('-position_statement__date', 'future__symbol')


# noinspection PyMethodMayBeStatic,PyProtectedMember
class PositionForexAdmin(PsModelAdmin):
    def forex_link(self, obj):
        url = reverse(
            'admin:%s_%s_change' % (
                obj.forex._meta.app_label,
                obj.forex._meta.module_name
            ),
            args=(obj.forex.id,)
        )
        return '<a href="%s">%s</a>' % (url, obj.forex.symbol)

    forex_link.allow_tags = True
    forex_link.short_description = 'Forex'

    def description(self, obj):
        return obj.forex.description

    list_display = (
        'position_statement_date', 'forex_link', 'description',
        'quantity', 'trade_price', 'mark', 'mark_change', 'pct_change',
        'pl_open', 'profit_loss', 'pl_day', 'bp_effect'
    )

    list_filter = (
        'position_statement__date', ProfitLossListFilter
    )

    search_fields = (
        'position_statement__date', 'forex__symbol', 'forex__description',
    )

    fieldsets = (
        ('Foreign Key', {
            'classes': ('wide', 'collapse', 'open'),
            'fields': ('position_statement', 'forex')
        }),
        ('Position Forex', {
            'fields': (
                'quantity', 'trade_price', 'mark', 'mark_change',
                'pct_change', 'pl_open', 'pl_day', 'bp_effect'
            )
        }),
    )

    readonly_fields = (
        'position_statement', 'forex'
    )

    ordering = ('-position_statement__date', 'forex__symbol')

admin.site.register(models.PositionStatement, PositionStatementAdmin)
admin.site.register(models.PositionInstrument, PositionInstrumentAdmin)
admin.site.register(models.PositionEquity, PositionEquityAdmin)
admin.site.register(models.PositionOption, PositionOptionAdmin)
admin.site.register(models.PositionFuture, PositionFutureAdmin)
admin.site.register(models.PositionForex, PositionForexAdmin)




# todo: update to better interface
