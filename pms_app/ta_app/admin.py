from django.contrib import admin
from django.core.urlresolvers import reverse
from pms_app.ta_app import models


# noinspection PyMethodMayBeStatic,PyProtectedMember
class TradeActivityInline(admin.TabularInline):
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


class FilledOrderInline(TradeActivityInline):
    model = models.FilledOrder

    readonly_fields = (
        'underlying', 'exec_time', 'spread', 'side', 'quantity', 'pos_effect',
        'expire_date', 'strike', 'contract', 'price', 'net_price', 'order', 'link'
    )

    ordering = ('underlying', )


class WorkingOrderInline(TradeActivityInline):
    model = models.WorkingOrder

    readonly_fields = (
        'underlying', 'time_placed', 'spread', 'side', 'quantity', 'pos_effect',
        'expire_date', 'strike', 'contract', 'price', 'order', 'tif', 'mark',
        'status', 'link'
    )

    ordering = ('underlying', )


class CancelledOrderInline(TradeActivityInline):
    model = models.CancelledOrder

    readonly_fields = (
        'underlying', 'time_cancelled', 'spread', 'side', 'quantity', 'pos_effect',
        'expire_date', 'strike', 'contract', 'price', 'order', 'tif', 'status', 'link'
    )

    ordering = ('underlying', )


class RollingStrategyInline(TradeActivityInline):
    model = models.RollingStrategy

    readonly_fields = (
        'underlying', 'new_expire_date', 'call_by', 'days_begin',
        'order_price', 'active_time_start', 'active_time_end',
        'move_to_market_time_start', 'move_to_market_time_end', 'status', 'link'
    )

    exclude = ('strategy', 'side', 'right', 'ex_month', 'ex_year', 'strike_price', 'contract')

    ordering = ('underlying', )


# noinspection PyMethodMayBeStatic
class TradeActivityAdmin(admin.ModelAdmin):
    inlines = (
        WorkingOrderInline, FilledOrderInline,
        CancelledOrderInline, RollingStrategyInline
    )

    def filled_order_count(self, obj):
        return models.FilledOrder.objects.filter(trade_activity=obj).count()

    def working_order_count(self, obj):
        return models.WorkingOrder.objects.filter(trade_activity=obj).count()

    def cancelled_order_count(self, obj):
        return models.CancelledOrder.objects.filter(trade_activity=obj).count()

    def rolling_strategy_count(self, obj):
        return models.RollingStrategy.objects.filter(trade_activity=obj).count()

    filled_order_count.short_description = 'Filled Orders'
    working_order_count.short_description = 'Working Orders'
    cancelled_order_count.short_description = 'Cancelled Orders'
    rolling_strategy_count.short_description = 'Rolling Strategy'

    def get_inline_instances(self, request, obj=None):
        return obj and super(TradeActivityAdmin, self).get_inline_instances(request, obj) or []

    def date_formatted(self, obj):
        return obj.date.strftime('%Y-%m-%d')

    list_display = (
        'date_formatted', 'filled_order_count', 'working_order_count',
        'cancelled_order_count', 'rolling_strategy_count'
    )

    fieldsets = (
        ('Trade Activity', {
            'fields': (
                'statement', 'date'
            )
        }),
    )

    date_hierarchy = 'date'

    ordering = ('-date', )

    def has_add_permission(self, request):
        return False

    list_per_page = 20


# noinspection PyMethodMayBeStatic
class WorkingOrderAdmin(admin.ModelAdmin):
    def date(self, obj):
        return obj.trade_activity.date.strftime('%Y-%m-%d')

    list_display = (
        'date', 'underlying', 'time_placed', 'spread', 'side', 'quantity', 'pos_effect',
        'expire_date', 'strike', 'contract', 'price', 'order', 'tif', 'mark', 'status'
    )

    search_fields = (
        'trade_activity__date', 'underlying__symbol', 'quantity'
    )

    list_filter = (
        'trade_activity__date', 'spread', 'side', 'contract',
        'pos_effect', 'order', 'tif', 'status'
    )

    fieldsets = (
        ('Foreign Key', {
            'classes': ('collapse', 'open'),
            'fields': ('trade_activity', 'underlying')
        }),
        ('Working Order', {
            'fields': (
                'time_placed',
                ('spread', 'side', 'quantity'),
                ('expire_date', 'contract', 'strike'),
                ('pos_effect', 'status', 'price'),
                ('order', 'tif', 'mark')
            )
        }),
    )

    readonly_fields = (
        'trade_activity', 'underlying'
    )

    list_per_page = 30

    ordering = ('-trade_activity__date', 'underlying__symbol')

    def has_add_permission(self, request):
        return False


# noinspection PyMethodMayBeStatic
class FilledOrderAdmin(admin.ModelAdmin):
    def date(self, obj):
        return obj.trade_activity.date.strftime('%Y-%m-%d')

    list_display = (
        'date', 'underlying', 'exec_time', 'spread', 'side', 'quantity', 'pos_effect',
        'expire_date', 'strike', 'contract', 'price', 'net_price', 'order'
    )

    list_filter = (
        'trade_activity__date', 'spread', 'side', 'contract', 'pos_effect', 'order'
    )

    search_fields = (
        'trade_activity__date', 'underlying__symbol', 'quantity'
    )

    fieldsets = (
        ('Foreign Key', {
            'classes': ('collapse', 'open'),
            'fields': ('trade_activity', 'underlying')
        }),
        ('Filled Order', {
            'fields': (
                'exec_time',
                ('spread', 'side', 'quantity'),
                ('expire_date', 'contract', 'strike'),
                ('pos_effect', 'price'),
                ('order', 'net_price')
            )
        })
    )

    readonly_fields = (
        'trade_activity', 'underlying'
    )

    list_per_page = 30

    ordering = ('-trade_activity__date', 'underlying__symbol')

    def has_add_permission(self, request):
        return False


# noinspection PyMethodMayBeStatic
class CancelledOrderAdmin(admin.ModelAdmin):
    def date(self, obj):
        return obj.trade_activity.date.strftime('%Y-%m-%d')

    list_display = (
        'date', 'underlying', 'time_cancelled', 'spread', 'side', 'quantity', 'pos_effect',
        'expire_date', 'strike', 'contract', 'price', 'order', 'tif', 'status'
    )

    search_fields = (
        'trade_activity__date', 'underlying__symbol', 'quantity'
    )

    list_filter = (
        'trade_activity__date', 'spread', 'side', 'contract',
        'pos_effect', 'order', 'tif', 'status'
    )

    fieldsets = (
        ('Foreign Key', {
            'classes': ('collapse', 'open'),
            'fields': ('trade_activity', 'underlying')
        }),
        ('Cancelled Order', {
            'fields': (
                'time_cancelled',
                ('spread', 'side', 'quantity'),
                ('expire_date', 'contract', 'strike'),
                ('pos_effect', 'status', 'price'),
                ('order', 'tif')
            )
        }),
    )

    readonly_fields = (
        'trade_activity', 'underlying'
    )

    list_per_page = 30

    ordering = ('-trade_activity__date', 'underlying__symbol')

    def has_add_permission(self, request):
        return False


# noinspection PyMethodMayBeStatic
class RollingStrategyAdmin(admin.ModelAdmin):
    def date(self, obj):
        return obj.trade_activity.date.strftime('%Y-%m-%d')

    def option(self, obj):
        return obj.__unicode__().split('>')[-1]

    list_display = (
        'date', 'underlying', 'strategy', 'option', 'side',
        'new_expire_date', 'call_by', 'days_begin',
        'order_price', 'status'
    )

    search_fields = (
        'trade_activity__date', 'underlying__symbol', 'ex_month', 'ex_year',
        'new_expire_date', 'call_by', 'days_begin', 'order_price'
    )

    list_filter = (
        'trade_activity__date', 'status'
    )

    fieldsets = (
        ('Foreign Key', {
            'classes': ('collapse', 'open'),
            'fields': ('trade_activity', 'underlying')
        }),
        ('Rolling Strategy', {
            'fields': (
                'strategy',
                ('new_expire_date', 'call_by'), ('order_price', 'days_begin'),
                ('active_time_start', 'active_time_end'),
                ('move_to_market_time_start', 'move_to_market_time_end'),
                'status'
            )
        }),
        ('Option', {
            'fields': (
                'side', 'right', 'ex_month',
                'ex_year', 'strike_price', 'contract'
            )
        })
    )

    readonly_fields = (
        'trade_activity', 'underlying', 'strategy'
    )

    list_per_page = 30

    ordering = ('-trade_activity__date', 'underlying__symbol')

    def has_add_permission(self, request):
        return False

# todo: ta... futures working, filled, cancelled


admin.site.register(models.TradeActivity, TradeActivityAdmin)
admin.site.register(models.WorkingOrder, WorkingOrderAdmin)
admin.site.register(models.FilledOrder, FilledOrderAdmin)
admin.site.register(models.CancelledOrder, CancelledOrderAdmin)
admin.site.register(models.RollingStrategy, RollingStrategyAdmin)

# todo: all models... waiting, add search and filter
# todo: test all save change
# todo: pos option missing option fields