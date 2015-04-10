from django.contrib import admin
from data.models import *
import locale

locale.setlocale(locale.LC_ALL, '')


# noinspection PyMethodMayBeStatic
class StockAdmin(admin.ModelAdmin):
    def volume_group(self, obj):
        return locale.format('%d', obj.volume, 1)

    volume_group.short_description = 'Volume'
    volume_group.admin_order_field = 'volume'

    def net_change_positive(self, obj):
        return '%+.2f' % obj.net_change

    net_change_positive.short_description = 'Net Chg'
    net_change_positive.admin_order_field = 'net_change'

    list_display = (
        'symbol', 'date', 'volume_group',
        'open', 'high', 'low', 'last',
        'net_change_positive'
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
                'open', 'high', 'low', 'last',
                'net_change'
            )
        }),
    )

    search_fields = ('symbol', 'date')

    readonly_fields = ('symbol', )

    list_per_page = 20

    def has_add_permission(self, request):
        return False


# noinspection PyMethodMayBeStatic
class OptionContractAdmin(admin.ModelAdmin):
    list_display = (
        'symbol', 'option_code', 'ex_month', 'ex_year',
        'right', 'special', 'strike', 'side', 'others'
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
                'strike', 'side', 'others'
            )
        }),
    )

    list_filter = (
        'special', 'side'
    )

    search_fields = ('symbol', 'ex_month', 'ex_year', 'special',
                     'side', 'option_code', 'others')

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
        'option_contract__special', 'option_contract__side'
    )

    list_display_links = ('option_code', )

    search_fields = (
        'option_contract__symbol', 'option_contract__ex_month', 'option_contract__ex_year',
        'option_contract__special', 'option_contract__side', 'option_contract__option_code'
    )

    def has_add_permission(self, request):
        return False


admin.site.register(Stock, StockAdmin)
admin.site.register(OptionContract, OptionContractAdmin)
admin.site.register(Option, OptionAdmin)