from django.contrib import admin
from position.models import *


class SubPositionAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False


# noinspection PyMethodMayBeStatic
class SubContextAdmin(SubPositionAdmin):
    def context(self, obj):
        return str(obj)


class BreakEvenAdmin(SubContextAdmin):
    list_display = ('context', 'price', 'condition', 'amount')

    fieldsets = (
        ('Primary Field', {
            'fields': ('price', 'condition', 'amount')
        }),
    )

    search_fields = ('price', 'condition', 'amount')

    list_per_page = 30


class StartProfitAdmin(SubContextAdmin):
    list_display = ('context', 'price', 'condition')

    fieldsets = (
        ('Primary Field', {
            'fields': ('price', 'condition')
        }),
    )

    search_fields = ('price', 'condition')

    list_per_page = 30


class StartLossAdmin(SubContextAdmin):
    list_display = ('context', 'price', 'condition')

    fieldsets = (
        ('Primary Field', {
            'fields': ('price', 'condition')
        }),
    )

    search_fields = ('price', 'condition')

    list_per_page = 30


class MaxProfitAdmin(SubContextAdmin):
    list_display = ('context', 'price', 'condition', 'limit', 'amount')

    fieldsets = (
        ('Primary Field', {
            'fields': ('price', 'condition', 'limit', 'amount')
        }),
    )

    list_per_page = 30


class MaxLossAdmin(SubContextAdmin):
    list_display = ('context', 'price', 'condition', 'limit', 'amount')

    fieldsets = (
        ('Primary Field', {
            'fields': ('price', 'condition', 'limit', 'amount')
        }),
    )

    list_per_page = 30


class PositionContextAdmin(SubContextAdmin):
    list_display = (
        'context',
        'break_even',
        'start_profit',
        'start_loss',
        'max_profit',
        'max_loss'
    )

    fieldsets = (
        ('Primary Field', {
            'fields': (
                'break_even',
                'start_profit',
                'start_loss',
                'max_profit',
                'max_loss'
            )
        }),
    )

    list_per_page = 30

admin.site.register(BreakEven, BreakEvenAdmin)
admin.site.register(StartProfit, StartProfitAdmin)
admin.site.register(StartLoss, StartLossAdmin)
admin.site.register(MaxProfit, MaxProfitAdmin)
admin.site.register(MaxLoss, MaxLossAdmin)
admin.site.register(PositionContext, PositionContextAdmin)
admin.site.register(PositionContexts)
admin.site.register(PositionSet)
