from django.forms import ModelForm
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.db.models import Count

from tos_import.statement.statement_trade import models


# noinspection PyMethodMayBeStatic,PyProtectedMember
class TradeActivityInline(admin.TabularInline):
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

    def link(self, obj):
        url = reverse(
            'admin:%s_%s_change' % (
                obj._meta.app_label, obj._meta.module_name
            ),
            args=(obj.id,)
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
class FilledOrderInline(TradeActivityInline):
    model = models.FilledOrder

    def order_time(self, obj):
        return obj.exec_time.strftime('%H:%M')

    order_time.short_description = 'Time'
    order_time.admin_order_field = 'exec_time'

    readonly_fields = (
        'symbol', 'order_time', 'spread', 'side',
        'quantity', 'pos_effect', 'expire_date', 'strike', 'contract',
        'price', 'net_price', 'order', 'link'
    )
    exclude = ('exec_time', 'underlying', 'future', 'forex')

    ordering = ('exec_time', 'future', 'forex', 'underlying')


# noinspection PyMethodMayBeStatic
class WorkingOrderInline(TradeActivityInline):
    model = models.WorkingOrder

    def order_time(self, obj):
        return obj.time_placed.strftime('%H:%M')

    order_time.short_description = 'Time'
    order_time.admin_order_field = 'time_placed'

    readonly_fields = (
        'symbol', 'order_time', 'spread', 'side',
        'quantity', 'pos_effect', 'expire_date', 'strike', 'contract',
        'price', 'order', 'tif', 'mark', 'status', 'link'
    )
    exclude = ('time_placed', 'underlying', 'future', 'forex')

    ordering = ('time_placed', 'future', 'forex', 'underlying')


# noinspection PyMethodMayBeStatic
class CancelledOrderInline(TradeActivityInline):
    model = models.CancelledOrder

    def order_time(self, obj):
        return obj.time_cancelled.strftime('%H:%M')

    order_time.short_description = 'Time'
    order_time.admin_order_field = 'time_cancelled'

    readonly_fields = (
        'symbol', 'order_time', 'spread', 'side', 'quantity', 'pos_effect',
        'expire_date', 'strike', 'contract', 'price', 'order', 'tif', 'status', 'link'
    )
    exclude = ('time_cancelled', 'underlying', 'future', 'forex')

    ordering = ('time_cancelled', 'future', 'forex', 'underlying')


class RollingStrategyInline(TradeActivityInline):
    model = models.RollingStrategy

    readonly_fields = (
        'underlying', 'new_expire_date', 'call_by', 'days_begin',
        'order_price', 'active_time_start', 'active_time_end',
        'move_to_market_time_start', 'move_to_market_time_end', 'status', 'link'
    )

    exclude = ('strategy', 'side', 'right', 'ex_month', 'ex_year', 'strike', 'contract')

    ordering = ('active_time_start', 'underlying')


# noinspection PyMethodMayBeStatic,PyUnusedLocal
class TradeActivityAdmin(admin.ModelAdmin):
    inlines = (
        WorkingOrderInline, FilledOrderInline,
        CancelledOrderInline, RollingStrategyInline
    )

    def queryset(self, request):
        return models.TradeSummary.objects\
            .annotate(working_order=Count('workingorder', distinct=True)) \
            .annotate(filled_order=Count('filledorder', distinct=True)) \
            .annotate(cancelled_order=Count('cancelledorder', distinct=True)) \
            .annotate(rolling_strategy=Count('rollingstrategy', distinct=True))

    def working_orders(self, obj):
        return obj.working_order

    working_orders.admin_order_field = 'working_order'

    def filled_orders(self, obj):
        return obj.filled_order

    filled_orders.admin_order_field = 'filled_order'

    def cancelled_orders(self, obj):
        return obj.cancelled_order

    cancelled_orders.admin_order_field = 'cancelled_order'

    def rolling_strategies(self, obj):
        return obj.rolling_strategy

    rolling_strategies.admin_order_field = 'rolling_strategy'

    def get_inline_instances(self, request, obj=None):
        return obj and super(TradeActivityAdmin, self).get_inline_instances(request, obj) or []

    def date_formatted(self, obj):
        return obj.date.strftime('%Y-%m-%d')

    date_formatted.short_description = 'Date'
    date_formatted.admin_order_field = 'date'

    list_display = (
        'date_formatted', 'working_orders', 'filled_orders',
        'cancelled_orders', 'rolling_strategies'
    )

    fieldsets = (
        ('Trade Activity', {
            'fields': (
                'statement', 'date'
            )
        }),
    )

    readonly_fields = ('statement', 'date')

    date_hierarchy = 'date'

    ordering = ('-date', )

    def has_add_permission(self, request):
        return False

    list_per_page = 20

    suit_form_tabs = (
        ('general', 'General'),
        ('working_order', 'Working Order'),
        ('filled_order', 'Filled Order'),
        ('cancelled_order', 'Cancelled Order'),
        ('rolling_strategy', 'Rolling Strategy'),
    )

    # Read about form includes in next section
    suit_form_includes = (
        ('admin/tos_import/statement_trade/working_order.html', 'middle', 'cities'),
    )


# noinspection PyMethodMayBeStatic,PyProtectedMember
class TaAdmin(admin.ModelAdmin):
    def date(self, obj):
        return obj.trade_summary.date.strftime('%Y-%m-%d')

    date.admin_order_field = 'trade_summary__date'

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

    readonly_fields = (
        'trade_summary', 'underlying', 'future', 'forex'
    )

    search_fields = (
        'trade_summary__date',
        'underlying__symbol', 'underlying__company',
        'forex__symbol', 'forex__description',
        'future__symbol', 'future__lookup', 'future__description',
        'future__expire_date', 'future__session', 'future__spc',
        'quantity'
    )

    list_per_page = 30

    def has_add_permission(self, request):
        return False


class TaForm(ModelForm):
    class Meta:
        pass


# noinspection PyMethodMayBeStatic
class WorkingOrderAdmin(TaAdmin):
    form = TaForm

    def order_time(self, obj):
        return obj.time_placed.strftime('%H:%M')

    order_time.short_description = 'Time'
    order_time.admin_order_field = 'time_placed'

    list_display = (
        'date', 'symbol', 'spread', 'order_time', 'side', 'quantity', 'pos_effect',
        'expire_date', 'strike', 'contract', 'price', 'order', 'tif', 'mark', 'status'
    )

    list_filter = (
        'trade_summary__date', 'spread', 'side', 'contract',
        'pos_effect', 'order', 'tif', 'status'
    )

    fieldsets = (
        ('Foreign Key', {
            'fields': ('trade_summary', 'underlying', 'future', 'forex')
        }),
        ('Working Order', {
            'fields': (
                'time_placed',
                'spread', 'side', 'quantity',
                'expire_date', 'contract', 'strike',
                'pos_effect', 'status', 'price',
                'order', 'tif', 'mark'
            )
        }),
    )

    ordering = (
        '-trade_summary__date', '-time_placed',
        'future__symbol', 'forex__symbol', 'underlying__symbol'
    )


# noinspection PyMethodMayBeStatic
class FilledOrderAdmin(TaAdmin):
    form = TaForm

    def order_time(self, obj):
        return obj.exec_time.strftime('%H:%M')

    order_time.short_description = 'Time'
    order_time.admin_order_field = 'exec_time'

    list_display = (
        'date', 'symbol', 'spread', 'order_time', 'side', 'quantity', 'pos_effect',
        'expire_date', 'strike', 'contract', 'price', 'net_price', 'order'
    )

    list_filter = (
        'trade_summary__date', 'spread', 'side', 'contract', 'pos_effect', 'order'
    )

    fieldsets = (
        ('Foreign Key', {
            'fields': ('trade_summary', 'underlying', 'future', 'forex')
        }),
        ('Filled Order', {
            'fields': (
                'exec_time',
                'spread', 'side', 'quantity',
                'expire_date', 'contract', 'strike',
                'pos_effect', 'price',
                'order', 'net_price'
            )
        })
    )

    ordering = ('-trade_summary__date', '-exec_time')


class CustomStatusFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = 'Status'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return (
            ('cancel', 'CANCELED'),
            ('expire', 'EXPIRED'),
            ('reject', 'REJECTED')
        )

    def queryset(self, request, queryset):
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.
        if self.value() == 'cancel':
            return queryset.filter(status='CANCELED')
        elif self.value() == 'expire':
            return queryset.filter(status='EXPIRED')
        elif self.value() == 'reject':
            return queryset.filter(status__contains='REJECTED')


# noinspection PyMethodMayBeStatic
class CancelledOrderAdmin(TaAdmin):
    form = TaForm

    def order_time(self, obj):
        return obj.time_cancelled.strftime('%H:%M')

    def custom_status(self, obj):
        return 'REJECTED' if 'REJECTED' in obj.status else obj.status

    order_time.short_description = 'Time'
    order_time.admin_order_field = 'time_cancelled'

    list_display = (
        'date', 'symbol', 'spread', 'order_time', 'side', 'quantity', 'pos_effect',
        'expire_date', 'strike', 'contract', 'price', 'order', 'tif', 'custom_status'
    )

    list_filter = (
        'trade_summary__date', 'spread', 'side', 'contract',
        'pos_effect', 'order', 'tif', CustomStatusFilter
    )

    fieldsets = (
        ('Foreign Key', {
            'fields': ('trade_summary', 'underlying', 'future', 'forex')
        }),
        ('Cancelled Order', {
            'fields': (
                'time_cancelled',
                'spread', 'side', 'quantity',
                'expire_date', 'contract', 'strike',
                'pos_effect', 'status', 'price',
                'order', 'tif'
            )
        }),
    )

    ordering = ('-trade_summary__date', '-time_cancelled')


# noinspection PyMethodMayBeStatic,PyProtectedMember
class RollingStrategyAdmin(admin.ModelAdmin):
    def date(self, obj):
        return obj.trade_summary.date.strftime('%Y-%m-%d')

    date.admin_order_field = 'trade_summary__date'

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

    def option(self, obj):
        return obj.__unicode__().split('>')[-1]

    list_display = (
        'date', 'symbol', 'strategy', 'option', 'side',
        'new_expire_date', 'call_by', 'days_begin',
        'order_price', 'status'
    )

    search_fields = (
        'trade_summary__date', 'underlying__symbol', 'underlying__company',
        'strategy', 'right', 'ex_month', 'ex_year', 'strike',
        'new_expire_date', 'call_by', 'days_begin', 'order_price'
    )

    list_filter = (
        'trade_summary__date', 'right', 'contract', 'status',
    )

    fieldsets = (
        ('Foreign Key', {
            'fields': ('trade_summary', 'underlying')
        }),
        ('Rolling Strategy', {
            'fields': (
                'strategy',
                'new_expire_date', 'call_by', 'order_price', 'days_begin',
                'active_time_start', 'active_time_end',
                'move_to_market_time_start', 'move_to_market_time_end',
                'status'
            )
        }),
        ('Option', {
            'fields': (
                'side', 'right', 'ex_month',
                'ex_year', 'strike', 'contract'
            )
        })
    )

    readonly_fields = (
        'trade_summary', 'underlying', 'strategy'
    )

    list_per_page = 30

    ordering = ('-trade_summary__date', 'underlying__symbol')

    def has_add_permission(self, request):
        return False

admin.site.register(models.TradeSummary, TradeActivityAdmin)
admin.site.register(models.WorkingOrder, WorkingOrderAdmin)
admin.site.register(models.FilledOrder, FilledOrderAdmin)
admin.site.register(models.CancelledOrder, CancelledOrderAdmin)
admin.site.register(models.RollingStrategy, RollingStrategyAdmin)
