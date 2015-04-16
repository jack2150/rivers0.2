import locale

from django.contrib import admin
from django.core.urlresolvers import reverse
from django.db.models import Q, Count

from tos_import.statement.statement_position import models


locale.setlocale(locale.LC_ALL, '')


# noinspection PyMethodMayBeStatic,PyProtectedMember
class PositionSummaryInline(admin.TabularInline):
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
class PositionSummaryInlinePL(PositionSummaryInline):
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
class PositionInstrumentInline(PositionSummaryInlinePL):
    """
    Inline Position model inside Position Statement change view
    """
    model = models.PositionInstrument

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

    fields = (
        'symbol', 'delta', 'gamma', 'theta', 'vega',
        'pct_change', 'formatted_pl_open', 'formatted_pl_day',
        'bp_effect', 'profit_loss', 'link'
    )

    readonly_fields = (
        'underlying', 'delta', 'gamma', 'theta', 'vega',
        'pct_change', 'formatted_pl_open', 'formatted_pl_day',
        'bp_effect', 'profit_loss', 'link', 'symbol'
    )
    extra = 0

    ordering = ('underlying', )


# noinspection PyProtectedMember,PyMethodMayBeStatic
class PositionFutureInline(PositionSummaryInlinePL):
    """
    Inline Position model inside Position Statement change view
    """
    model = models.PositionFuture

    def symbol(self, obj):
        url = reverse(
            'admin:%s_%s_change' % (
                obj.future._meta.app_label,
                obj.future._meta.module_name
            ),
            args=(obj.future.id,)
        )
        return '<a href="%s">%s</a>' % (url, obj.future.symbol)

    symbol.allow_tags = True

    fields = (
        'symbol', 'quantity', 'days', 'trade_price',
        'mark', 'mark_change', 'pct_change', 'pl_open', 'pl_day', 'bp_effect',
        'profit_loss', 'link'
    )

    readonly_fields = (
        'future', 'quantity', 'days', 'trade_price',
        'mark', 'mark_change', 'pct_change', 'pl_open', 'pl_day', 'bp_effect',
        'profit_loss', 'link', 'symbol'
    )
    # exclude = ('delta', 'gamma', 'theta', 'vega')
    extra = 0

    ordering = ('future', )


# noinspection PyProtectedMember,PyMethodMayBeStatic
class PositionForexInline(PositionSummaryInlinePL):
    """
    Inline Position model inside Position Statement change view
    """
    model = models.PositionForex

    def symbol(self, obj):
        url = reverse(
            'admin:%s_%s_change' % (
                obj.forex._meta.app_label,
                obj.forex._meta.module_name
            ),
            args=(obj.forex.id,)
        )
        return '<a href="%s">%s</a>' % (url, obj.forex.symbol)

    symbol.allow_tags = True

    fields = (
        'symbol', 'quantity', 'trade_price', 'mark', 'mark_change',
        'pct_change', 'pl_open', 'pl_day', 'bp_effect',
        'profit_loss', 'link'
    )

    readonly_fields = (
        'forex', 'quantity', 'trade_price', 'mark', 'mark_change',
        'pct_change', 'pl_open', 'pl_day', 'bp_effect',
        'profit_loss', 'link', 'symbol'
    )
    # exclude = ('delta', 'gamma', 'theta', 'vega')
    extra = 0

    ordering = ('forex', )


# noinspection PyMethodMayBeStatic
class PositionSummaryAdmin(admin.ModelAdmin):
    """
    Position Statement admin interface
    """
    inlines = (PositionInstrumentInline, PositionFutureInline, PositionForexInline)

    def position_summary_date(self, obj):
        return obj.date.strftime('%Y-%m-%d')

    position_summary_date.short_description = 'Date'
    position_summary_date.admin_order_field = 'date'

    def instruments(self, obj):
        return obj.positioninstrument_set.count()

    def equities(self, obj):
        return 1 if obj.positionequity else 0

    def options(self, obj):
        return obj.positionoption_set.count()

    def futures(self, obj):
        return obj.positionfuture_set.count()

    def forexs(self, obj):
        return obj.positionforex_set.count()

    def currency_cash_sweep(self, obj):
        return locale.currency(obj.cash_sweep, grouping=True)

    currency_cash_sweep.short_description = 'Cash Sweep'
    currency_cash_sweep.admin_order_field = 'cash_sweep'

    def currency_available(self, obj):
        return locale.currency(obj.available, grouping=True)

    currency_available.short_description = 'Dollar Available'
    currency_available.admin_order_field = 'available'

    def currency_pl_ytd(self, obj):
        return locale.currency(obj.pl_ytd, grouping=True)

    currency_pl_ytd.short_description = 'PL YTD'
    currency_pl_ytd.admin_order_field = 'pl_ytd'

    def currency_futures_bp(self, obj):
        return locale.currency(obj.futures_bp, grouping=True)

    currency_futures_bp.short_description = 'Futures BP'
    currency_futures_bp.admin_order_field = 'futures_bp'

    def currency_bp_adjustment(self, obj):
        return locale.currency(obj.bp_adjustment, grouping=True)

    currency_bp_adjustment.short_description = 'BP Adjustment'
    currency_bp_adjustment.admin_order_field = 'bp_adjustment'

    list_display = (
        'position_summary_date', 'currency_cash_sweep', 'currency_available',
        'currency_pl_ytd', 'currency_futures_bp', 'currency_bp_adjustment',
        'instruments', 'equities', 'options', 'futures', 'forexs'
    )

    fieldsets = (
        ('Foreign Key', {
            'fields': (
                'statement',
                'date'
            )
        }),
        ('Position Statement', {
            'fields': (
                'cash_sweep', 'available', 'pl_ytd', 'futures_bp', 'bp_adjustment'
            )
        }),
    )

    readonly_fields = ('statement', 'date')

    search_fields = ['date', 'available', 'pl_ytd']

    date_hierarchy = 'date'

    list_per_page = 30

    def has_add_permission(self, request):
        return False


class PositionStockInline(PositionSummaryInline):
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


class PositionOptionsInline(PositionSummaryInline):
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
    def position_summary_date(self, obj):
        return obj.position_summary.date.strftime('%Y-%m-%d')

    position_summary_date.short_description = 'Date'
    position_summary_date.admin_order_field = 'position_summary__date'

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
    symbol.admin_order_field = 'underlying__symbol'

    def description(self, obj):
        return obj.underlying.company

    description.admin_order_field = 'underlying__company'

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
    profit_loss.admin_order_field = 'pl_open'

    list_per_page = 30

    def has_add_permission(self, request):
        return False


# noinspection PyMethodMayBeStatic
class SpreadTypeListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = 'Spread Type'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'spread_type'

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

    def option_leg_queryset(self, queryset, leg_num):
        """
        Make option 1-4 leg queryset
        :param queryset: QuerySet
        :param leg_num: int
        """
        # equity = 0, option only have 1 row and not quantity 0, done
        return queryset.filter(positionequity__quantity=0).filter(
            Q(positionoption__quantity__gt=0) | Q(positionoption__quantity__lt=0)
        ).annotate(option_count=Count('positionoption')).filter(option_count=leg_num)

    def queryset(self, request, queryset):
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.
        if self.value() == 'closed':
            # equity = 0 and options = 0 or option not exists
            queryset = queryset.filter(positionequity__quantity=0).filter(
                Q(positionoption__quantity=0) | Q(positionoption__isnull=True)
            ).exclude(
                Q(positionoption__quantity__lt=0) | Q(positionoption__quantity__gt=0)
            ).annotate()
        elif self.value() == 'equity':
            # equity exists, option quantity is 0 or option not exists
            queryset = queryset.filter(
                ~Q(positionequity__quantity=0) &
                (Q(positionoption__quantity=0) | Q(positionoption__isnull=True))
            )
        elif self.value() == 'hedge':
            # equity exists, option exists and option is not null
            queryset = queryset.exclude(positionequity__quantity=0)\
                .exclude(positionoption__quantity=0)\
                .exclude(positionoption__isnull=True)
        elif self.value() == 'one_leg':
            # equity = 0, option only have 1 row and not quantity 0, done
            queryset = self.option_leg_queryset(queryset, 1)
        elif self.value() == 'two_leg':
            # equity = 0, option only have 1 row and not quantity 0, done
            queryset = self.option_leg_queryset(queryset, 2)
        elif self.value() == 'three_leg':
            # equity = 0, option only have 1 row and not quantity 0, done
            queryset = self.option_leg_queryset(queryset, 3)
        elif self.value() == 'four_leg':
            # equity = 0, option only have 1 row and not quantity 0, done
            queryset = self.option_leg_queryset(queryset, 4)

        return queryset


# noinspection PyMethodMayBeStatic
class PositionInstrumentAdmin(PsModelAdmin):
    """
    Position admin interface for Position model only
    """
    list_select_related = True

    inlines = (PositionStockInline, PositionOptionsInline)

    def equity(self, obj):
        return 1 if obj.positionequity.quantity != 0 else 0

    def options(self, obj):
        return obj.positionoption_set.exclude(quantity=0).count()

    list_display = (
        'position_summary_date', 'symbol', 'description',
        'delta', 'gamma', 'theta', 'vega',
        'pct_change', 'pl_open', 'profit_loss', 'pl_day', 'bp_effect',
        'equity', 'options'
    )

    fieldsets = (
        ('Foreign Key', {
            'fields': (
                ('position_summary', 'underlying', 'position_set')
            )
        }),
        ('Instrument', {
            'fields': (
                'delta', 'gamma', 'theta', 'vega',
                'pct_change', 'pl_open', 'pl_day', 'bp_effect'
            )
        }),
    )

    readonly_fields = ('position_summary', 'underlying', 'position_set')

    search_fields = (
        'position_summary__date', 'underlying__symbol', 'underlying__company'
    )
    list_filter = (
        'position_summary__date', SpreadTypeListFilter, ProfitLossListFilter
    )
    ordering = ('-position_summary__date', 'underlying__symbol')


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
        'position_summary_date', 'symbol', 'description', 'quantity',
        'trade_price', 'mark', 'mark_change', 'pct_change',
        'pl_open', 'profit_loss', 'pl_day', 'bp_effect'
    )

    list_filter = (
        'position_summary__date', ProfitLossListFilter, QuantityListFilter
    )

    fieldsets = (
        ('Foreign Key', {
            'fields': ('position_summary', 'instrument', 'underlying')
        }),
        ('Equity', {
            'fields': (
                'trade_price', 'mark', 'mark_change', 'quantity',
                'pct_change', 'pl_open', 'pl_day', 'bp_effect'
            )
        }),
    )

    readonly_fields = (
        'position_summary', 'instrument', 'underlying'
    )

    search_fields = (
        'position_summary__date', 'underlying__symbol', 'underlying__company'
    )
    ordering = ('-position_summary__date', 'underlying__symbol')


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
        'position_summary_date', 'symbol', 'option',
        'quantity', 'days', 'mark', 'mark_change',
        'delta', 'gamma', 'theta', 'vega', 'pct_change',
        'pl_open', 'profit_loss', 'pl_day', 'bp_effect'
    )

    list_filter = (
        'position_summary__date',
        ProfitLossListFilter, DteListFilter, QuantityListFilter,
        'right', 'special', 'contract',
    )

    search_fields = (
        'position_summary__date', 'underlying__symbol', 'underlying__company',
        'right', 'special', 'ex_month', 'ex_year', 'strike', 'contract'
    )

    fieldsets = (
        ('Foreign Key', {
            'fields': ('position_summary', 'instrument', 'underlying')
        }),
        ('Detail', {
            'fields': (
                'quantity', 'days',
                'mark', 'mark_change', 'trade_price',
                'delta', 'gamma', 'theta', 'vega',
                'pct_change', 'pl_open', 'pl_day', 'bp_effect'
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
        'position_summary', 'instrument', 'underlying'
    )
    ordering = ('-position_summary__date', 'underlying__symbol')


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
        'position_summary_date', 'future_link', 'description',
        'quantity', 'days', 'trade_price', 'mark', 'mark_change', 'pct_change',
        'pl_open', 'profit_loss', 'pl_day', 'bp_effect'
    )

    list_filter = (
        'position_summary__date', ProfitLossListFilter
    )

    search_fields = (
        'position_summary__date', 'future__symbol', 'future__lookup',
        'future__description', 'future__spc', 'future__expire_date'
    )

    fieldsets = (
        ('Foreign Key', {
            'fields': ('position_summary', 'future', 'position_set')
        }),
        ('Detail', {
            'fields': (
                'quantity', 'days', 'trade_price', 'mark', 'mark_change',
                'pct_change', 'pl_open', 'pl_day', 'bp_effect'
            )
        }),
    )

    readonly_fields = ('position_summary', 'future', 'position_set')
    ordering = ('-position_summary__date', 'future__symbol')


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
        'position_summary_date', 'forex_link', 'description',
        'quantity', 'trade_price', 'mark', 'mark_change', 'pct_change',
        'pl_open', 'profit_loss', 'pl_day', 'bp_effect'
    )

    list_filter = (
        'position_summary__date', ProfitLossListFilter
    )

    search_fields = (
        'position_summary__date', 'forex__symbol', 'forex__description',
    )

    fieldsets = (
        ('Foreign Key', {
            'fields': ('position_summary', 'forex', 'position_set')
        }),
        ('Position Forex', {
            'fields': (
                'quantity', 'trade_price', 'mark', 'mark_change',
                'pct_change', 'pl_open', 'pl_day', 'bp_effect'
            )
        }),
    )

    readonly_fields = ('position_summary', 'forex', 'position_set')

    ordering = ('-position_summary__date', 'forex__symbol')

admin.site.register(models.PositionSummary, PositionSummaryAdmin)
admin.site.register(models.PositionInstrument, PositionInstrumentAdmin)
admin.site.register(models.PositionEquity, PositionEquityAdmin)
admin.site.register(models.PositionOption, PositionOptionAdmin)
admin.site.register(models.PositionFuture, PositionFutureAdmin)
admin.site.register(models.PositionForex, PositionForexAdmin)
