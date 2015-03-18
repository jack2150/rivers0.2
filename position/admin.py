from django.contrib import admin
from django.core.urlresolvers import reverse
from position.models import *


# noinspection PyMethodMayBeStatic,PyProtectedMember
from tos_import.statement.statement_account.admin import AccountSummaryInline, ProfitLossInline
from tos_import.statement.statement_account.models import ProfitLoss
from tos_import.statement.statement_position.admin import PositionInstrumentInline, PositionForexInline, \
    PositionFutureInline
from tos_import.statement.statement_trade.admin import TradeActivityInline, FilledOrderInline
from tos_import.statement.statement_trade.models import FilledOrder


class SubPositionAdmin(admin.ModelAdmin):
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
    symbol.admin_order_field = 'underlying__symbol'

    def has_add_permission(self, request):
        return False


# noinspection PyMethodMayBeStatic
class SubContextAdmin(SubPositionAdmin):
    def context(self, obj):
        return str(obj)

    search_fields = (
        'position_set__name',
        'position_set__spread',
        'position_set__status',
        'position_set__underlying__symbol',
        'position_set__future__symbol',
        'position_set__forex__symbol',
    )

    list_filter = (
        'position_set__name',
        'position_set__spread',
        'position_set__status'
    )

    readonly_fields = ('position_set', )


class BreakEvenAdmin(SubContextAdmin):
    list_display = ('position_set', 'context', 'price', 'condition', 'amount')

    fieldsets = (
        ('Foreign Key', {
            'fields': ('position_set', )
        }),
        ('Primary Field', {
            'fields': ('price', 'condition', 'amount')
        }),
    )

    search_fields = SubContextAdmin.search_fields + ('price', 'condition', 'amount')

    list_per_page = 30


class StartProfitAdmin(SubContextAdmin):
    list_display = ('position_set', 'context', 'price', 'condition')

    fieldsets = (
        ('Foreign Key', {
            'fields': ('position_set', )
        }),
        ('Primary Field', {
            'fields': ('price', 'condition')
        }),
    )

    search_fields = SubContextAdmin.search_fields + ('price', 'condition')

    list_per_page = 30


class StartLossAdmin(SubContextAdmin):
    list_display = ('position_set', 'context', 'price', 'condition')

    fieldsets = (
        ('Foreign Key', {
            'fields': ('position_set', )
        }),
        ('Primary Field', {
            'fields': ('price', 'condition')
        }),
    )

    search_fields = SubContextAdmin.search_fields + ('price', 'condition')

    list_per_page = 30


class MaxProfitAdmin(SubContextAdmin):
    list_display = ('position_set', 'context', 'price', 'condition', 'limit', 'amount')

    fieldsets = (
        ('Foreign Key', {
            'fields': ('position_set', )
        }),
        ('Primary Field', {
            'fields': ('price', 'condition', 'limit', 'amount')
        }),
    )

    list_per_page = 30


class MaxLossAdmin(SubContextAdmin):
    list_display = ('position_set', 'context', 'price', 'condition', 'limit', 'amount')

    fieldsets = (
        ('Foreign Key', {
            'fields': ('position_set', )
        }),
        ('Primary Field', {
            'fields': ('price', 'condition', 'limit', 'amount')
        }),
    )

    list_per_page = 30


class PositionSetInline(admin.TabularInline):
    def has_delete_permission(self, request, obj=None):
        return False

    extra = 0


class BreakEvenInline(PositionSetInline):
    model = BreakEven
    readonly_fields = (
        'price', 'condition', 'amount'
    )


class StartProfitInline(PositionSetInline):
    model = StartProfit
    readonly_fields = (
        'price', 'condition'
    )


class StartLossInline(PositionSetInline):
    model = StartLoss
    readonly_fields = (
        'price', 'condition'
    )


class MaxProfitInline(PositionSetInline):
    model = MaxProfit
    readonly_fields = (
        'price', 'condition', 'limit', 'amount'
    )


class MaxLossInline(PositionSetInline):
    model = MaxLoss
    readonly_fields = (
        'price', 'condition', 'limit', 'amount'
    )


# noinspection PyMethodMayBeStatic,PyProtectedMember
class PositionSetAdmin(SubPositionAdmin):
    inlines = (
        FilledOrderInline,
        PositionInstrumentInline, PositionFutureInline, PositionForexInline,
        ProfitLossInline,
        BreakEvenInline, StartProfitInline, StartLossInline,
        MaxProfitInline, MaxLossInline,

    )

    def position(self, obj):
        return str(obj).split(':')[1]

    position.admin_order_field = 'id'

    list_display = ('id', 'position', 'symbol', 'name', 'spread', 'status')
    list_display_links = ('position', )

    search_fields = (
        'name',
        'spread',
        'status',
        'underlying__symbol',
        'future__symbol',
        'forex__symbol',
    )

    list_filter = (
        'name',
        'spread',
        'status'
    )

    fieldsets = (
        ('Foreign Key', {
            'fields': ('symbol', )
        }),
        ('Primary Field', {
            'fields': ('name', 'spread', 'status')
        }),
    )

    readonly_fields = ('symbol', 'underlying', 'future', 'forex')

    list_per_page = 30


# todo: inline read only position_set on statements
# todo: profit invalid foreign key on position set

admin.site.register(BreakEven, BreakEvenAdmin)
admin.site.register(StartProfit, StartProfitAdmin)
admin.site.register(StartLoss, StartLossAdmin)
admin.site.register(MaxProfit, MaxProfitAdmin)
admin.site.register(MaxLoss, MaxLossAdmin)
admin.site.register(PositionSet, PositionSetAdmin)
