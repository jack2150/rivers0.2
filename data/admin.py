from django.contrib import admin
from data.views import *
import locale


locale.setlocale(locale.LC_ALL, '')


# noinspection PyMethodMayBeStatic
class StockAdmin(admin.ModelAdmin):
    def volume_group(self, obj):
        return locale.format('%d', obj.volume, 1)

    volume_group.short_description = 'Volume'
    volume_group.admin_order_field = 'volume'

    list_display = (
        'symbol', 'date', 'volume_group',
        'open', 'high', 'low', 'close', 'source'
    )

    fieldsets = (
        ('Underlying', {
            'fields': (
                'symbol',
            )
        }),
        ('Primary Field', {
            'fields': (
                'date', 'volume',
                'open', 'high', 'low', 'close', 'source'
            )
        }),
    )

    search_fields = ('symbol', 'date', 'source')

    readonly_fields = ('symbol', )

    list_per_page = 20

    def has_add_permission(self, request):
        return False


# noinspection PyMethodMayBeStatic
class OptionContractAdmin(admin.ModelAdmin):
    list_display = (
        'symbol', 'option_code', 'ex_month', 'ex_year',
        'right', 'special', 'strike', 'contract', 'others'
    )

    fieldsets = (
        ('Underlying', {
            'fields': (
                'symbol',
            )
        }),
        ('Primary Field', {
            'fields': (
                'option_code', 'ex_month', 'ex_year', 'right', 'special',
                'strike', 'contract', 'others'
            )
        }),
    )

    list_filter = (
        'special', 'contract'
    )

    search_fields = ('symbol', 'ex_month', 'ex_year', 'special',
                     'contract', 'option_code', 'others')

    list_display_links = ('option_code', )

    readonly_fields = ('symbol', )

    list_per_page = 20

    def has_add_permission(self, request):
        return False


# noinspection PyMethodMayBeStatic
class OptionAdmin(admin.ModelAdmin):
    def symbol(self, obj):
        return obj.option_contract.symbol

    symbol.short_description = 'Symbol'
    symbol.admin_order_field = 'option_contract__symbol'

    def option_code(self, obj):
        return obj.option_contract.option_code

    option_code.short_description = 'Option Code'
    option_code.admin_order_field = 'option_contract__option_code'

    list_display = (
        'symbol', 'option_code', 'date', 'dte',
        'last', 'mark', 'bid', 'ask', 'delta', 'gamma', 'theta', 'vega',
        'theo_price', 'impl_vol', 'prob_itm', 'prob_otm', 'prob_touch', 'volume',
        'open_int', 'intrinsic', 'extrinsic'
    )

    list_per_page = 20

    list_filter = (
        'option_contract__special', 'option_contract__contract'
    )

    list_display_links = ('option_code', )

    search_fields = (
        'option_contract__symbol', 'option_contract__ex_month', 'option_contract__ex_year',
        'option_contract__special', 'option_contract__contract', 'option_contract__option_code'
    )

    def has_add_permission(self, request):
        return False

# admin model
admin.site.register(Stock, StockAdmin)
admin.site.register(OptionContract, OptionContractAdmin)
admin.site.register(Option, OptionAdmin)

# admin view, tos thinkback csv
admin.site.register_view(
    'data/import/$',
    urlname='data_select_symbol_view',
    view=data_select_symbol_view
)

admin.site.register_view(
    'data/symbol/stat/$',
    urlname='data_symbol_stat_view',
    view=data_symbol_stat_view
)

admin.site.register_view(
    'data/symbol/stat/(?P<symbol>\w+)/$',
    urlname='data_symbol_stat_view',
    view=data_symbol_stat_view
)

admin.site.register_view(
    'data/csv/import/$',
    urlname='data_tos_thinkback_import_view',
    view=data_tos_thinkback_import_view
)
admin.site.register_view(
    'data/csv/import/(?P<symbol>\w+)/$',
    urlname='data_tos_thinkback_import_view',
    view=data_tos_thinkback_import_view
)

# web get google and yahoo
admin.site.register_view(
    'data/web/import/$',
    urlname='data_web_import_view',
    view=data_web_import_view
)
admin.site.register_view(
    'data/web/import/(?P<symbol>\w+)/$',
    urlname='data_web_import_view',
    view=data_web_import_view
)

# daily import csv and web
admin.site.register_view(
    'data/daily/import/$',
    urlname='data_daily_import_view',
    view=data_daily_import_view
)