from django.contrib import admin
from pms_app.acc_app import models


class AccountSummaryAdmin(admin.ModelAdmin):
    list_display = ('date', 'net_liquid_value', 'stock_buying_power', 'option_buying_power',
                    'commissions_ytd')

    fieldsets = [
        ('Date', {'fields': ['date']}),
        ('Net Liquid', {'fields': ['net_liquid_value', 'stock_buying_power', 'option_buying_power']}),
        ('Commissions', {'fields': ['commissions_ytd', 'futures_commissions_ytd']}),
    ]

    #list_filter = ['date']
    search_fields = ['date', 'net_liquid_value']

admin.site.register(models.CashBalance)
admin.site.register(models.ProfitsLosses)
admin.site.register(models.AccountStatement, AccountSummaryAdmin)
admin.site.register(models.OrderHistory)
admin.site.register(models.TradeHistory)
admin.site.register(models.Equities)
admin.site.register(models.Options)
admin.site.register(models.Futures)
admin.site.register(models.Forex)

