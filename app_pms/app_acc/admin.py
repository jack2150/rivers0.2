import locale
from django.contrib import admin
from app_pms.app_acc import models


# noinspection PyMethodMayBeStatic
class AccountSummaryAdmin(admin.ModelAdmin):
    def formatted_date(self, obj):
        return obj.date.strftime('%Y-%m-%d')
    formatted_date.short_description = 'Date'

    def currency_net_liquid_value(self, obj):
        return locale.currency(obj.net_liquid_value, grouping=True)
    currency_net_liquid_value.short_description = 'Net Liquid Value'

    def currency_stock_buying_power(self, obj):
        return locale.currency(obj.stock_buying_power, grouping=True)
    currency_stock_buying_power.short_description = 'Stock Buying Power'

    def currency_option_buying_power(self, obj):
        return locale.currency(obj.option_buying_power, grouping=True)
    currency_option_buying_power.short_description = 'Option Buying Power'

    def currency_commissions_ytd(self, obj):
        return locale.currency(obj.commissions_ytd, grouping=True)
    currency_commissions_ytd.short_description = 'Commissions YTD'

    def currency_futures_commissions_ytd(self, obj):
        return locale.currency(obj.futures_commissions_ytd, grouping=True)
    currency_futures_commissions_ytd.short_description = 'Futures Commissions YTD'

    list_display = (
        'formatted_date', 'currency_net_liquid_value',
        'currency_stock_buying_power', 'currency_option_buying_power',
        'currency_commissions_ytd', 'currency_futures_commissions_ytd'
    )

    fieldsets = (
        ('Foreign Key', {
            'classes': ('wide', 'collapse', 'open'),
            'fields': ('statement', 'date')
        }),
        ('Account Statement', {
            'classes': ('wide', ),
            'fields': (
                'net_liquid_value', 'stock_buying_power', 'option_buying_power',
                'commissions_ytd', 'futures_commissions_ytd'
            )
        })
    )

    readonly_fields = ('statement', 'date')

    date_hierarchy = 'date'
    search_fields = ['date', 'net_liquid_value']

    def has_add_permission(self, request):
        return False


# noinspection PyMethodMayBeStatic
class AccountStatementForeignAdmin(admin.ModelAdmin):
    def account_statement_date(self, obj):
        return obj.account_statement.date.strftime('%Y-%m-%d')

    account_statement_date.short_description = 'Date'

    def underlying_symbol(self, obj):
        return obj.underlying.symbol

    underlying_symbol.short_description = 'Symbol'

    list_per_page = 30

    readonly_fields = (
        'account_statement', 'underlying'
    )

    ordering = (
        '-account_statement__date', 'underlying__symbol'
    )

    def has_add_permission(self, request):
        return False


# noinspection PyMethodMayBeStatic
class OrderHistoryAdmin(AccountStatementForeignAdmin):
    list_display = (
        'account_statement_date', 'underlying_symbol',
        'status', 'time_placed', 'pos_effect', 'contract', 'side',
        'spread', 'expire_date', 'strike', 'tif', 'price', 'order', 'quantity'
    )

    search_fields = (
        'account_statement__date', 'underlying__symbol', 'expire_date', 'quantity'
    )

    list_filter = (
        'status', 'pos_effect', 'contract', 'side', 'spread', 'tif', 'order'
    )

    fieldsets = (
        ('Foreign Key', {
            'classes': ('wide', 'collapse', 'open'),
            'fields': ('account_statement', 'underlying')
        }),
        ('Order History', {
            #'classes': ('wide', ),
            'fields': (
                'time_placed',
                ('status', 'pos_effect', 'quantity'),
                ('contract', 'side', 'price'),
                ('expire_date', 'tif', 'strike'),
                ('order', 'spread')
            )
        })
    )


# noinspection PyMethodMayBeStatic
class TradeHistoryAdmin(AccountStatementForeignAdmin):
    list_display = (
        'account_statement_date', 'underlying_symbol',
        'execute_time', 'spread', 'side', 'quantity', 'pos_effect',
        'expire_date', 'strike', 'contract', 'price', 'net_price', 'order_type'
    )

    search_fields = (
        'account_statement__date', 'underlying__symbol', 'expire_date', 'quantity'
    )

    list_filter = (
        'spread', 'side', 'pos_effect', 'contract', 'order_type'
    )

    fieldsets = (
        ('Foreign Key', {
            'classes': ('wide', 'collapse', 'open'),
            'fields': ('account_statement', 'underlying')
        }),
        ('Trade History', {
            'fields': (
                'execute_time',
                ('spread', 'side', 'contract'),
                ('pos_effect', 'expire_date', 'order_type'),
                ('quantity', 'strike', 'net_price', 'price')
            )
        })
    )


# noinspection PyMethodMayBeStatic
class HoldingEquityAdmin(AccountStatementForeignAdmin):
    list_display = (
        'account_statement_date', 'underlying_symbol',
        'quantity', 'trade_price', 'mark', 'mark_value'
    )

    search_fields = (
        'account_statement__date', 'underlying__symbol', 'quantity'
    )

    fieldsets = (
        ('Foreign Key', {
            'classes': ('wide', 'collapse', 'open'),
            'fields': ('account_statement', 'underlying')
        }),
        ('Holding Equity', {
            'fields': (
                'quantity', 'trade_price', 'mark', 'mark_value'
            )
        })
    )

    readonly_fields = (
        'account_statement', 'underlying'
    )

    ordering = (
        '-account_statement__date', 'underlying__symbol'
    )


# noinspection PyMethodMayBeStatic
class HoldingOptionAdmin(AccountStatementForeignAdmin):
    list_display = (
        'account_statement_date', 'underlying_symbol',
        'option_code', 'expire_date', 'strike',
        'contract', 'quantity', 'trade_price', 'mark', 'mark_value'
    )

    search_fields = (
        'account_statement__date', 'underlying__symbol', 'option_code', 'expire_date', 'quantity'
    )

    list_filter = (
        'contract',
    )

    fieldsets = (
        ('Foreign Key', {
            'classes': ('wide', 'collapse', 'open'),
            'fields': ('account_statement', 'underlying')
        }),
        ('Holding Option', {
            'fields': (
                'option_code', 'expire_date', 'strike',
                'contract', 'quantity', 'trade_price', 'mark', 'mark_value'
            )
        })
    )


# noinspection PyMethodMayBeStatic
class ProfitLossAdmin(AccountStatementForeignAdmin):
    list_display = (
        'account_statement_date', 'underlying_symbol',
        'pl_open', 'pl_pct', 'pl_day', 'pl_ytd', 'margin_req', 'mark_value'
    )

    search_fields = (
        'account_statement__date', 'underlying__symbol',
    )

    fieldsets = (
        ('Foreign Key', {
            'classes': ('wide', 'collapse', 'open'),
            'fields': ('account_statement', 'underlying')
        }),
        ('Profit Loss', {
            'fields': (
                'pl_open', 'pl_pct', 'pl_day', 'pl_ytd', 'margin_req', 'mark_value'
            )
        })
    )


# noinspection PyMethodMayBeStatic
class CashBalanceAdmin(AccountStatementForeignAdmin):
    list_display = (
        'account_statement_date',
        'time', 'contract', 'ref_no', 'description',
        'fees', 'commissions', 'amount', 'balance'
    )

    search_fields = (
        'account_statement__date', 'time', 'ref_no', 'description',
    )

    list_filter = (
        'contract',
    )

    fieldsets = (
        ('Foreign Key', {
            'classes': ('wide', 'collapse', 'open'),
            'fields': ('account_statement', )
        }),
        ('Cash Balance', {
            'fields': (
                'time', 'contract', 'ref_no', 'description',
                'fees', 'commissions', 'amount', 'balance'
            )
        })
    )

    readonly_fields = (
        'account_statement',
    )

    ordering = (
        '-account_statement__date', 'time'
    )


# noinspection PyMethodMayBeStatic
class FutureAdmin(AccountStatementForeignAdmin):
    def future_lookup(self, obj):
        return obj.future.lookup

    future_lookup.short_description = 'Lookup'

    def future_symbol(self, obj):
        return obj.future.symbol

    future_symbol.short_description = 'Symbol'

    def future_expire_date(self, obj):
        return obj.future.expire_date

    future_expire_date.short_description = 'Expire Date'

    def future_description(self, obj):
        return obj.future.description

    future_description.short_description = 'Description'

    list_display = (
        'account_statement_date',
        'future_lookup', 'future_symbol', 'future_expire_date', 'future_description',
        'quantity', 'trade_price', 'mark', 'pl_day'
    )

    search_fields = (
        'account_statement__date',
        'future__lookup', 'future__symbol', 'future__expire_date', 'future__description'
    )

    fieldsets = (
        ('Foreign Key', {
            'classes': ('wide', 'collapse', 'open'),
            'fields': ('account_statement', 'future')
        }),
        ('Future', {
            'fields': (
                'quantity', 'trade_price', 'mark', 'pl_day'
            )
        })
    )

    readonly_fields = (
        'account_statement', 'future'
    )

    ordering = (
        '-account_statement__date', 'future'
    )


# todo: acc... future statements, futures profit losses, order history, trade history



admin.site.register(models.AccountStatement, AccountSummaryAdmin)
admin.site.register(models.CashBalance, CashBalanceAdmin)
admin.site.register(models.ProfitLoss, ProfitLossAdmin)
admin.site.register(models.OrderHistory, OrderHistoryAdmin)
admin.site.register(models.TradeHistory, TradeHistoryAdmin)
admin.site.register(models.HoldingEquity, HoldingEquityAdmin)
admin.site.register(models.HoldingOption, HoldingOptionAdmin)
admin.site.register(models.HoldingFuture, FutureAdmin)
admin.site.register(models.Forex)

