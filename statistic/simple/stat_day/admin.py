from django.contrib import admin
from statistic.simple.stat_day.models import StatDay, StatDayHolding, StatDayOptionGreek
from statistic.simple.stat_day.views import simple_stat_day_view


# noinspection PyMethodMayBeStatic
class DayStatAdmin(admin.ModelAdmin):
    def statement_date(self, obj):
        return obj.statement.date

    statement_date.short_description = 'Date'
    statement_date.admin_order_field = 'statement__date'

    list_display = (
        'statement_date',
        'total_holding_count',
        'total_order_count',
        'working_order_count',
        'filled_order_count',
        'cancelled_order_count',
        'account_pl_ytd',
        'account_pl_day',
        'holding_pl_day',
        'holding_pl_open',
        'commission_day',
        'commission_ytd',
        'option_bp_day',
        'stock_bp_day'
    )

    fieldsets = (
        ('Foreign Key', {
            'fields': (
                'statement',
            )
        }),
        ('Primary Fields', {
            'fields': (
                'total_holding_count',
                'total_order_count',
                'working_order_count',
                'filled_order_count',
                'cancelled_order_count',
                'account_pl_ytd',
                'account_pl_day',
                'holding_pl_day',
                'holding_pl_open',
                'commission_day',
                'commission_ytd',
                'option_bp_day',
                'stock_bp_day'
            )
        })
    )

    ordering = ('-statement__date', )
    readonly_fields = ('statement', )
    search_fields = ('statement__date', )
    list_per_page = 30

    def has_add_permission(self, request):
        return False


# noinspection PyMethodMayBeStatic
class DayStatHoldingAdmin(admin.ModelAdmin):

    list_display = (
        'stat_day', 'name',
        'total_order_count',
        'working_order_count',
        'filled_order_count',
        'cancelled_order_count',
        'total_holding_count',
        'profit_holding_count',
        'loss_holding_count',
        'pl_open_sum',
        'profit_open_sum',
        'loss_open_sum',
        'pl_day_sum',
        'profit_day_sum',
        'loss_day_sum',
        'bp_effect_sum'
    )

    list_filter = (
        'name',
    )

    fieldsets = (
        ('Foreign Key', {
            'fields': (
                'stat_day',
            )
        }),
        ('Primary Fields', {
            'fields': (
                'name',
                'total_order_count',
                'working_order_count',
                'filled_order_count',
                'cancelled_order_count',
                'total_holding_count',
                'profit_holding_count',
                'loss_holding_count',
                'pl_open_sum',
                'profit_open_sum',
                'loss_open_sum',
                'pl_day_sum',
                'profit_day_sum',
                'loss_day_sum',
                'bp_effect_sum'
            )
        })
    )

    ordering = ('-stat_day__statement__date', )
    readonly_fields = ('stat_day', )
    list_per_page = 30

    search_fields = ('stat_day__statement__date', 'name')

    def has_add_permission(self, request):
        return False


admin.site.register(StatDay, DayStatAdmin)
admin.site.register(StatDayHolding, DayStatHoldingAdmin)
admin.site.register(StatDayOptionGreek)
admin.site.register_view(
    'stat_simple/daily/$',
    urlname='simple_stat_day_view',
    view=simple_stat_day_view
)
admin.site.register_view(
    'stat_simple/daily/(?P<date>\d{4}-\d{2}-\d{2})/$',
    urlname='simple_stat_day_view',
    view=simple_stat_day_view
)
