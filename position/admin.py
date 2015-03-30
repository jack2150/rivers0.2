from django.contrib import admin
from django.core.urlresolvers import reverse
from position.models import *
from position.views import spread_view
from tos_import.statement.statement_account.admin import ProfitLossInline
from tos_import.statement.statement_position.admin import \
    PositionInstrumentInline, PositionForexInline, PositionFutureInline
from tos_import.statement.statement_trade.admin import FilledOrderInline


# noinspection PyMethodMayBeStatic,PyProtectedMember
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


# noinspection PyMethodMayBeStatic
class PositionStageAdmin(SubContextAdmin):
    def position(self, obj):
        return str(obj.position_set).split(':')[1]

    position.admin_order_field = 'id'

    list_display = (
        'position',
        'stage_name', 'stage_expression',
        'price_a', 'amount_a',
        'price_b', 'amount_b',
        # 'left_status', 'left_expression',
        #'right_status', 'right_expression',
    )

    fieldsets = (
        ('Foreign Key', {
            'fields': ('position_set', )
        }),
        ('Primary Field', {
            'fields': (
                'stage_name', 'stage_expression',
                'price_a', 'amount_a',
                'price_b', 'amount_b',
                'left_status', 'left_expression',
                'right_status', 'right_expression',
            )
        }),
    )

    list_filter = SubContextAdmin.list_filter + (
        'stage_name',
    )

    search_fields = SubContextAdmin.search_fields + (
        'stage_name',
    )

    list_per_page = 30


class PositionSetInline(admin.TabularInline):
    def has_delete_permission(self, request, obj=None):
        return False

    extra = 0


class PositionStageInline(PositionSetInline):
    model = PositionStage
    fields = (
        'stage_name', 'stage_expression',
        'price_a', 'amount_a',
        'price_b', 'amount_b',
    )

    readonly_fields = (
        'stage_name', 'stage_expression',
        'price_a', 'amount_a',
        'price_b', 'amount_b',
    )


# noinspection PyMethodMayBeStatic,PyProtectedMember
class PositionSetAdmin(SubPositionAdmin):
    inlines = (
        PositionStageInline,
        ProfitLossInline, FilledOrderInline,
        PositionInstrumentInline, PositionFutureInline, PositionForexInline,
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


admin.site.register(PositionSet, PositionSetAdmin)
admin.site.register(PositionStage, PositionStageAdmin)
admin.site.register_view(
    'position/spread/$',
    urlname='position_set_spread_view',
    view=spread_view
)
admin.site.register_view(
    'position/spread/(?P<date>\d{4}-\d{2}-\d{2})/$',
    urlname='position_set_spread_view',
    view=spread_view
)
