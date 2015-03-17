import locale
from django.contrib import admin
from django.core.urlresolvers import reverse
from tos_import.statement.statement_account import models


# noinspection PyMethodMayBeStatic,PyProtectedMember
class AccountSummaryInline(admin.TabularInline):
    def symbol(self, obj):
        if obj.underlying:
            url = reverse(
                'admin:%s_%s_change' % (
                    obj.underlying._meta.app_label, obj.underlying._meta.module_name
                ),
                args=(obj.underlying.id,)
            )
        elif obj.future:
            url = reverse(
                'admin:%s_%s_change' % (
                    obj.future._meta.app_label, obj.future._meta.module_name
                ),
                args=(obj.future.id,)
            )
        elif obj.forex:
            url = reverse(
                'admin:%s_%s_change' % (
                    obj.forex._meta.app_label, obj.forex._meta.module_name
                ),
                args=(obj.forex.id,)
            )
        else:
            url = None

        return '<a href="%s">%s</a>' % (url, obj.get_symbol())

    symbol.allow_tags = True

    def description(self, obj):
        return obj.get_description()

    def custom_status(self, obj):
        return obj.status.split(':')[0] if ':' in obj.status else obj.status

    custom_status.short_description = 'Status'

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class ProfitLossInline(AccountSummaryInline):
    model = models.ProfitLoss

    readonly_fields = (
        'symbol', 'description', 'pl_open', 'pl_pct',
        'pl_day', 'pl_ytd', 'margin_req', 'mark_value'
    )
    exclude = ('underlying', 'future')


# noinspection PyMethodMayBeStatic
class OrderHistoryInline(AccountSummaryInline):
    model = models.OrderHistory

    def time_plc(self, obj):
        return obj.time_placed.strftime('%H:%M')

    time_plc.short_description = 'Time Placed'

    readonly_fields = (
        'symbol', 'description', 'time_plc', 'custom_status', 'pos_effect', 'quantity', 'contract',
        'side', 'price', 'expire_date', 'tif', 'strike', 'order', 'spread'
    )
    exclude = ('underlying', 'future', 'forex', 'status', 'time_placed')


# noinspection PyMethodMayBeStatic
class TradeHistoryInline(AccountSummaryInline):
    model = models.TradeHistory

    def exec_time(self, obj):
        return obj.execute_time.strftime('%H:%M')

    exec_time.short_description = 'Execute Time'

    readonly_fields = (
        'symbol', 'description', 'exec_time', 'spread', 'side', 'contract', 'pos_effect',
        'expire_date', 'order_type', 'quantity', 'strike', 'net_price', 'price'
    )
    exclude = ('underlying', 'future', 'forex', 'status', 'execute_time')


class CashBalanceInline(AccountSummaryInline):
    model = models.CashBalance

    readonly_fields = (
        'time', 'contract', 'ref_no', 'description',
        'fees', 'commissions', 'amount', 'balance'
    )


class ForexStatementInline(AccountSummaryInline):
    model = models.ForexStatement

    readonly_fields = (
        'time', 'contract', 'ref_no', 'description',
        'commissions', 'amount', 'amount_usd', 'balance'
    )


# noinspection PyProtectedMember
class HoldingForexInline(AccountSummaryInline):
    model = models.HoldingForex

    def symbol(self, obj):
        url = reverse(
            'admin:%s_%s_change' % (
                obj.forex._meta.app_label, obj.forex._meta.module_name
            ),
            args=(obj.forex.id,)
        )
        return '<a href="%s">%s</a>' % (url, obj.forex.symbol)
    symbol.allow_tags = True

    readonly_fields = (
        'symbol', 'description', 'quantity', 'mark', 'trade_price', 'fpl'
    )
    exclude = ('forex', )


class ForexSummaryInline(AccountSummaryInline):
    model = models.ForexSummary

    readonly_fields = (
        'cash', 'upl', 'floating', 'equity', 'margin',
        'available_equity', 'risk_level'
    )


class FutureStatementInline(AccountSummaryInline):
    model = models.FutureStatement

    readonly_fields = (
        'execute_date', 'execute_time', 'contract',
        'ref_no', 'description', 'fee', 'commission', 'amount', 'balance'
    )


# noinspection PyProtectedMember
class HoldingFutureInline(AccountSummaryInline):
    model = models.HoldingFuture

    def symbol(self, obj):
        url = reverse(
            'admin:%s_%s_change' % (
                obj.future._meta.app_label, obj.future._meta.module_name
            ),
            args=(obj.future.id,)
        )
        return '<a href="%s">%s</a>' % (url, obj.future.symbol)

    symbol.allow_tags = True

    def description(self, obj):
        return obj.future.description

    readonly_fields = (
        'symbol', 'description', 'quantity', 'trade_price', 'mark', 'pl_day'
    )
    exclude = ('future', )


# noinspection PyProtectedMember
class HoldingEquityInline(AccountSummaryInline):
    model = models.HoldingEquity

    def symbol(self, obj):
        url = reverse(
            'admin:%s_%s_change' % (
                obj.underlying._meta.app_label, obj.underlying._meta.module_name
            ),
            args=(obj.underlying.id,)
        )
        return '<a href="%s">%s</a>' % (url, obj.underlying.symbol)

    symbol.allow_tags = True

    readonly_fields = (
        'symbol', 'description', 'quantity', 'trade_price', 'mark', 'mark_value'
    )
    exclude = ('underlying', )


# noinspection PyProtectedMember
class HoldingOptionInline(AccountSummaryInline):
    model = models.HoldingOption

    def symbol(self, obj):
        url = reverse(
            'admin:%s_%s_change' % (
                obj.underlying._meta.app_label, obj.underlying._meta.module_name
            ),
            args=(obj.underlying.id,)
        )
        return '<a href="%s">%s</a>' % (url, obj.underlying.symbol)

    symbol.allow_tags = True

    readonly_fields = (
        'symbol', 'description', 'option_code', 'expire_date', 'strike',
        'contract', 'quantity', 'trade_price', 'mark', 'mark_value'
    )
    exclude = ('underlying', )


# noinspection PyMethodMayBeStatic
class AccountSummaryAdmin(admin.ModelAdmin):
    inlines = (
        TradeHistoryInline, OrderHistoryInline,
        ProfitLossInline,
        HoldingEquityInline, HoldingOptionInline,
        CashBalanceInline,
        ForexSummaryInline, HoldingForexInline, ForexStatementInline,
        HoldingFutureInline, FutureStatementInline,

    )

    def formatted_date(self, obj):
        return obj.date.strftime('%Y-%m-%d')
    formatted_date.short_description = 'Date'
    formatted_date.admin_order_field = 'date'

    def currency_net_liquid_value(self, obj):
        return locale.currency(obj.net_liquid_value, grouping=True)
    currency_net_liquid_value.short_description = 'Net Liquid Value'
    currency_net_liquid_value.admin_order_field = 'net_liquid_value'

    def currency_stock_buying_power(self, obj):
        return locale.currency(obj.stock_buying_power, grouping=True)
    currency_stock_buying_power.short_description = 'Stock Buying Power'
    currency_stock_buying_power.admin_order_field = 'stock_buying_power'

    def currency_option_buying_power(self, obj):
        return locale.currency(obj.option_buying_power, grouping=True)
    currency_option_buying_power.short_description = 'Option Buying Power'
    currency_option_buying_power.admin_order_field = 'option_buying_power'

    def currency_commissions_ytd(self, obj):
        return locale.currency(obj.commissions_ytd, grouping=True)
    currency_commissions_ytd.short_description = 'Commissions YTD'
    currency_commissions_ytd.admin_order_field = 'commissions_ytd'

    def currency_futures_commissions_ytd(self, obj):
        return locale.currency(obj.futures_commissions_ytd, grouping=True)
    currency_futures_commissions_ytd.short_description = 'Futures Commissions YTD'
    currency_futures_commissions_ytd.admin_order_field = 'futures_commissions_ytd'

    list_display = (
        'formatted_date', 'currency_net_liquid_value',
        'currency_stock_buying_power', 'currency_option_buying_power',
        'currency_commissions_ytd', 'currency_futures_commissions_ytd'
    )

    fieldsets = (
        ('Foreign Key', {
            'fields': ('statement', 'date')
        }),
        ('Account Statement', {
            'fields': (
                'net_liquid_value', 'stock_buying_power', 'option_buying_power',
                'commissions_ytd', 'futures_commissions_ytd'
            )
        })
    )

    readonly_fields = ('statement', 'date')

    date_hierarchy = 'date'
    search_fields = ['date', 'net_liquid_value']
    ordering = ('-date', )

    def has_add_permission(self, request):
        return False


# noinspection PyMethodMayBeStatic
class AccountStatementForeignAdmin(admin.ModelAdmin):
    def account_summary_date(self, obj):
        return obj.account_summary.date.strftime('%Y-%m-%d')

    account_summary_date.short_description = 'Date'
    account_summary_date.admin_order_field = 'account_summary__date'

    list_per_page = 30

    readonly_fields = (
        'account_summary', 'underlying'
    )

    ordering = (
        '-account_summary__date', 'underlying__symbol'
    )

    def has_add_permission(self, request):
        return False


class StatusListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = 'Status'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return (
            ('filled', 'FILLED'),
            ('working', 'WORKING'),
            ('accepted', 'ACCEPTED'),
            ('expired', 'EXPIRED'),
            ('rejected', 'REJECTED')
        )

    def queryset(self, request, queryset):
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.
        if self.value() == 'filled':
            return queryset.filter(status='FILLED')
        elif self.value() == 'working':
            return queryset.filter(status='WORKING')
        elif self.value() == 'accepted':
            return queryset.filter(status='ACCEPTED')
        elif self.value() == 'expired':
            return queryset.filter(status='EXPIRED')
        elif self.value() == 'rejected':
            return queryset.filter(status__contains='REJECTED')


# noinspection PyProtectedMember,PyMethodMayBeStatic
class OrderTradeAdmin(AccountStatementForeignAdmin):
    def symbol(self, obj):
        if obj.future:
            url = reverse(
                'admin:%s_%s_change' % (
                    obj.future._meta.app_label, obj.future._meta.module_name
                ),
                args=(obj.future.id,)
            )
        elif obj.forex:
            url = reverse(
                'admin:%s_%s_change' % (
                    obj.forex._meta.app_label, obj.forex._meta.module_name
                ),
                args=(obj.forex.id,)
            )
        else:
            url = reverse(
                'admin:%s_%s_change' % (
                    obj.underlying._meta.app_label, obj.underlying._meta.module_name
                ),
                args=(obj.underlying.id,)
            )
        return '<a href="%s">%s</a>' % (url, obj.get_symbol())

    symbol.allow_tags = True


# noinspection PyMethodMayBeStatic
class OrderHistoryAdmin(OrderTradeAdmin):
    def custom_status(self, obj):
        return obj.status.split(':')[0] if ':' in obj.status else obj.status

    custom_status.short_description = 'Status'

    list_display = (
        'account_summary_date', 'symbol',
        'custom_status', 'time_placed', 'pos_effect', 'contract', 'side',
        'spread', 'expire_date', 'strike', 'tif', 'price', 'order', 'quantity'
    )

    search_fields = (
        'account_summary__date',
        'underlying__symbol', 'underlying__company',
        'future__symbol', 'future__lookup', 'future__description',
        'forex__symbol', 'forex__description',
        'expire_date', 'quantity', 'status'
    )

    list_filter = (
        StatusListFilter, 'pos_effect', 'contract',
        'side', 'spread', 'tif', 'order'
    )

    fieldsets = (
        ('Foreign Key', {
            'fields': ('account_summary', 'underlying', 'future', 'forex')
        }),
        ('Order History', {
            'fields': (
                'time_placed',
                'status', 'pos_effect', 'quantity',
                'contract', 'side', 'price',
                'expire_date', 'tif', 'strike',
                'order', 'spread'
            )
        })
    )

    readonly_fields = ('account_summary', 'underlying', 'future', 'forex')


# noinspection PyMethodMayBeStatic
class TradeHistoryAdmin(OrderTradeAdmin):
    list_display = (
        'account_summary_date', 'symbol',
        'execute_time', 'spread', 'side', 'quantity', 'pos_effect',
        'expire_date', 'strike', 'contract', 'price', 'net_price', 'order_type'
    )

    search_fields = (
        'account_summary__date',
        'underlying__symbol', 'underlying__company',
        'future__symbol', 'future__lookup', 'future__description',
        'forex__symbol', 'forex__description',
        'expire_date', 'quantity'
    )

    list_filter = (
        'spread', 'side', 'pos_effect', 'contract', 'order_type'
    )

    fieldsets = (
        ('Foreign Key', {
            'fields': ('account_summary', 'underlying', 'future', 'forex')
        }),
        ('Trade History', {
            'fields': (
                'execute_time',
                'spread', 'side', 'contract',
                'pos_effect', 'expire_date', 'order_type',
                'quantity', 'strike', 'net_price', 'price'
            )
        })
    )

    readonly_fields = ('account_summary', 'underlying', 'future', 'forex')


class ContractListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = 'Status'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return (
            ('future', 'FUTURE'),
            ('equity_options', 'EQUITY & OPTIONS')
        )

    def queryset(self, request, queryset):
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.
        if self.value() == 'future':
            return queryset.filter(underlying__isnull=True)
        elif self.value() == 'equity_options':
            return queryset.filter(future__isnull=True)


# noinspection PyMethodMayBeStatic,PyProtectedMember
class ProfitLossAdmin(AccountStatementForeignAdmin):
    def symbol(self, obj):
        if obj.future:
            url = reverse(
                'admin:%s_%s_change' % (
                    obj.future._meta.app_label, obj.future._meta.module_name
                ),
                args=(obj.future.id,)
            )
        else:
            url = reverse(
                'admin:%s_%s_change' % (
                    obj.underlying._meta.app_label, obj.underlying._meta.module_name
                ),
                args=(obj.underlying.id,)
            )
        return '<a href="%s">%s</a>' % (url, obj.get_symbol())

    symbol.allow_tags = True

    def description(self, obj):
        return obj.get_description()

    list_display = (
        'account_summary_date', 'symbol', 'description',
        'pl_open', 'pl_pct', 'pl_day', 'pl_ytd', 'margin_req', 'mark_value'
    )

    search_fields = (
        'account_summary__date',
        'underlying__symbol', 'underlying__company',
        'future__symbol', 'future__lookup', 'future__description',
    )

    list_filter = (ContractListFilter, )

    fieldsets = (
        ('Foreign Key', {
            'fields': ('account_summary', 'underlying', 'future', 'position_set')
        }),
        ('Profit Loss', {
            'fields': (
                'pl_open', 'pl_pct', 'pl_day', 'pl_ytd', 'margin_req', 'mark_value'
            )
        })
    )

    readonly_fields = ('account_summary', 'underlying', 'future', 'position_set')


# noinspection PyMethodMayBeStatic
class CashBalanceAdmin(AccountStatementForeignAdmin):
    list_display = (
        'account_summary_date',
        'time', 'contract', 'ref_no', 'description',
        'fees', 'commissions', 'amount', 'balance'
    )

    search_fields = (
        'account_summary__date', 'time', 'ref_no', 'description',
    )

    list_filter = (
        'contract',
    )

    fieldsets = (
        ('Foreign Key', {
            'fields': ('account_summary', )
        }),
        ('Cash Balance', {
            'fields': (
                'time', 'contract', 'ref_no', 'description',
                'fees', 'commissions', 'amount', 'balance'
            )
        })
    )

    readonly_fields = (
        'account_summary',
    )

    ordering = (
        '-account_summary__date', 'time'
    )


# noinspection PyMethodMayBeStatic,PyProtectedMember
class HoldingEquityAdmin(AccountStatementForeignAdmin):
    def symbol(self, obj):
        url = reverse(
            'admin:%s_%s_change' % (
                obj.underlying._meta.app_label, obj.underlying._meta.module_name
            ),
            args=(obj.underlying.id,)
        )
        return '<a href="%s">%s</a>' % (url, obj.underlying.symbol)

    symbol.allow_tags = True
    symbol.admin_order_field = 'underlying__symbol'

    def description(self, obj):
        return obj.underlying.company

    description.admin_order_field = 'underlying__company'

    list_display = (
        'account_summary_date', 'symbol', 'description',
        'quantity', 'trade_price', 'mark', 'mark_value'
    )

    search_fields = (
        'account_summary__date', 'underlying__symbol', 'quantity'
    )

    fieldsets = (
        ('Foreign Key', {
            'fields': ('account_summary', 'underlying')
        }),
        ('Holding Equity', {
            'fields': (
                'quantity', 'trade_price', 'mark', 'mark_value'
            )
        })
    )

    readonly_fields = (
        'account_summary', 'underlying'
    )

    ordering = (
        '-account_summary__date', 'underlying__symbol'
    )


# noinspection PyMethodMayBeStatic,PyProtectedMember
class HoldingOptionAdmin(AccountStatementForeignAdmin):
    def symbol(self, obj):
        url = reverse(
            'admin:%s_%s_change' % (
                obj.underlying._meta.app_label, obj.underlying._meta.module_name
            ),
            args=(obj.underlying.id,)
        )
        return '<a href="%s">%s</a>' % (url, obj.underlying.symbol)

    symbol.allow_tags = True
    symbol.admin_order_field = 'underlying__symbol'

    def description(self, obj):
        return obj.underlying.company

    list_display = (
        'account_summary_date', 'symbol', 'description',
        'option_code', 'expire_date', 'strike',
        'contract', 'quantity', 'trade_price', 'mark', 'mark_value'
    )

    search_fields = (
        'account_summary__date',
        'underlying__symbol', 'underlying__company',
        'option_code', 'expire_date', 'quantity'
    )

    list_filter = (
        'contract',
    )

    fieldsets = (
        ('Foreign Key', {
            'fields': ('account_summary', 'underlying')
        }),
        ('Holding Option', {
            'fields': (
                'option_code', 'expire_date', 'strike',
                'contract', 'quantity', 'trade_price', 'mark', 'mark_value'
            )
        })
    )


# noinspection PyMethodMayBeStatic,PyProtectedMember
class HoldingFutureAdmin(AccountStatementForeignAdmin):
    def lookup(self, obj):
        return obj.future.lookup

    lookup.short_description = 'Lookup'
    lookup.admin_order_field = 'future__lookup'

    def symbol(self, obj):
        url = reverse(
            'admin:%s_%s_change' % (
                obj.future._meta.app_label, obj.future._meta.module_name
            ),
            args=(obj.future.id,)
        )
        return '<a href="%s">%s</a>' % (url, obj.future.symbol)

    symbol.allow_tags = True

    symbol.short_description = 'Symbol'
    symbol.admin_order_field = 'future__symbol'

    def future_expire_date(self, obj):
        return obj.future.expire_date

    future_expire_date.short_description = 'Expire Date'
    future_expire_date.admin_order_field = 'future__expire_date'

    def future_description(self, obj):
        return obj.future.description

    future_description.short_description = 'Description'
    future_description.admin_order_field = 'future__description'

    list_display = (
        'account_summary_date',
        'symbol', 'lookup', 'future_description',
        'future_expire_date', 'quantity', 'trade_price', 'mark', 'pl_day'
    )

    search_fields = (
        'account_summary__date',
        'future__lookup', 'future__symbol', 'future__expire_date', 'future__description'
    )

    fieldsets = (
        ('Foreign Key', {
            'fields': ('account_summary', 'future')
        }),
        ('Future', {
            'fields': (
                'quantity', 'trade_price', 'mark', 'pl_day'
            )
        })
    )

    readonly_fields = (
        'account_summary', 'future'
    )

    ordering = (
        '-account_summary__date', 'future'
    )


# noinspection PyProtectedMember,PyMethodMayBeStatic
class HoldingForexAdmin(AccountStatementForeignAdmin):
    def symbol(self, obj):
        url = reverse(
            'admin:%s_%s_change' % (
                obj.forex._meta.app_label, obj.forex._meta.module_name
            ),
            args=(obj.forex.id,)
        )
        return '<a href="%s">%s</a>' % (url, obj.forex.symbol)

    symbol.allow_tags = True
    symbol.admin_order_field = 'forex__symbol'

    def description(self, obj):
        return obj.forex.description

    description.admin_order_field = 'forex__description'

    list_display = (
        'account_summary_date',
        'symbol', 'description',
        'quantity', 'mark', 'trade_price', 'fpl'
    )

    search_fields = (
        'account_summary__date', 'forex__symbol', 'forex__description',
    )

    fieldsets = (
        ('Foreign Key', {
            'fields': ('account_summary', 'forex')
        }),
        ('Holding Forex', {
            'fields': (
                'quantity', 'mark', 'trade_price', 'fpl'
            )
        })
    )

    readonly_fields = (
        'account_summary', 'forex'
    )

    ordering = (
        '-account_summary__date', 'forex'
    )


class ForexSummaryAdmin(AccountStatementForeignAdmin):
    list_display = (
        'account_summary_date',
        'cash', 'upl', 'floating', 'equity', 'margin',
        'available_equity', 'risk_level'
    )

    search_fields = ('account_summary__date', )

    fieldsets = (
        ('Foreign Key', {
            'fields': ('account_summary', )
        }),
        ('Forex Summary', {
            'fields': (
                'cash', 'upl', 'floating', 'equity', 'margin',
                'available_equity', 'risk_level'
            )
        })
    )

    readonly_fields = ('account_summary', )

    ordering = ('-account_summary__date', )


class ForexStatementAdmin(AccountStatementForeignAdmin):
    list_display = (
        'account_summary_date',
        'time', 'contract', 'ref_no', 'description',
        'commissions', 'amount', 'amount_usd', 'balance'
    )

    search_fields = ('account_summary__date', 'description')

    list_filter = ('contract', )

    fieldsets = (
        ('Foreign Key', {
            'fields': ('account_summary', )
        }),
        ('Forex Statement', {
            'fields': (
                'time', 'contract', 'ref_no', 'description',
                'commissions', 'amount', 'amount_usd', 'balance'
            )
        })
    )

    readonly_fields = ('account_summary', )

    ordering = ('-account_summary__date',)


class FutureStatementAdmin(AccountStatementForeignAdmin):
    list_display = (
        'account_summary_date',
        'execute_date', 'execute_time', 'contract',
        'ref_no', 'description', 'fee', 'commission', 'amount', 'balance'
    )

    search_fields = ('account_summary__date', 'description')

    list_filter = ('contract', )

    fieldsets = (
        ('Foreign Key', {
            'fields': ('account_summary', )
        }),
        ('Future Statement', {
            'fields': (
                'execute_date', 'execute_time', 'contract',
                'ref_no', 'description', 'fee', 'commission', 'amount', 'balance'
            )
        })
    )

    readonly_fields = ('account_summary', )

    ordering = ('-account_summary__date', '-execute_date', '-execute_time')


admin.site.register(models.AccountSummary, AccountSummaryAdmin)  # wait
admin.site.register(models.CashBalance, CashBalanceAdmin)  # done
admin.site.register(models.ProfitLoss, ProfitLossAdmin)  # done
admin.site.register(models.OrderHistory, OrderHistoryAdmin)  # done
admin.site.register(models.TradeHistory, TradeHistoryAdmin)  # done

admin.site.register(models.HoldingEquity, HoldingEquityAdmin)  # done
admin.site.register(models.HoldingOption, HoldingOptionAdmin)  # done
admin.site.register(models.HoldingFuture, HoldingFutureAdmin)  # done
admin.site.register(models.HoldingForex, HoldingForexAdmin)  # done

admin.site.register(models.FutureStatement, FutureStatementAdmin)  # done
admin.site.register(models.ForexStatement, ForexStatementAdmin)  # done
admin.site.register(models.ForexSummary, ForexSummaryAdmin)  # done
