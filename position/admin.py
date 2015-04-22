from django import forms
from django.contrib import admin
from django.core.urlresolvers import reverse
from position.models import *
from position.views import *
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
class PositionStageAdmin(SubPositionAdmin):
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

    search_fields = (
        'position_set__name',
        'position_set__id',
        'position_set__spread',
        'position_set__status',
        'position_set__underlying__symbol',
        'position_set__future__symbol',
        'position_set__forex__symbol',
        'stage_name',
    )

    list_filter = (
        'position_set__name',
        'position_set__spread',
        'position_set__status',
        'stage_name',
    )

    readonly_fields = ('position_set', )

    list_per_page = 30


class PositionStageInline(admin.TabularInline):
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

    def has_delete_permission(self, request, obj=None):
        return False

    extra = 0


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


class PositionOpinionAdminForm(forms.ModelForm):
    DIRECTIONS = (
        ('CUSTOM', 'CUSTOM'),
        ('BULL', 'BULLISH'),
        ('BEAR', 'BEARISH'),
    )

    direction = forms.ChoiceField(choices=DIRECTIONS)

    DECISIONS = (
        ('CUSTOM', 'CUSTOM'),
        ('HOLD', 'HOLD'),
        ('CLOSE', 'CLOSE'),
    )

    decision = forms.ChoiceField(choices=DECISIONS)

    ANALYSIS = (
        ('QUICK', 'QUICK'),
        ('SIMPLE', 'SIMPLE'),
        ('DEEP', 'DEEP'),
    )

    analysis = forms.ChoiceField(choices=ANALYSIS)


class PositionOpinionAdmin(admin.ModelAdmin):
    form = PositionOpinionAdminForm

    change_list_template = 'position/admin/change_list.html'

    list_display = (
        'position_set', 'date', 'direction', 'decision',
        'analysis', 'description',
        'direction_result', 'decision_result'
    )

    fieldsets = (
        ('Foreign Key', {
            'fields': ('position_set', )
        }),
        ('Primary Field', {
            'fields': (
                'date', 'direction', 'decision',
                'analysis', 'description',
                'direction_result', 'decision_result'
            )
        }),
    )

    search_fields = (
        'position_set__id',
        'position_set__name',
        'position_set__spread',
        'position_set__underlying__symbol',
        'position_set__underlying__company',
        'position_set__future__symbol',
        'position_set__forex__symbol',
    )

    list_filter = (
        'position_set__name',
        'position_set__spread',
        'position_set__status',
    )

    list_per_page = 20


admin.site.register(PositionSet, PositionSetAdmin)
admin.site.register(PositionStage, PositionStageAdmin)
admin.site.register(PositionOpinion, PositionOpinionAdmin)


# spread view
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

# profiler view
admin.site.register_view(
    'position/profiler/$',
    urlname='position_set_profiler_view',
    view=profiler_view
)
admin.site.register_view(
    'position/profiler/(?P<id>[0-9]+)/$',
    urlname='position_set_profiler_view',
    view=profiler_view
)
admin.site.register_view(
    'position/profiler/(?P<id>[0-9]+)/(?P<date>\d{4}-\d{2}-\d{2})/$',
    urlname='position_set_profiler_view',
    view=profiler_view
)

# opinion ajax
admin.site.register_view(
    'position/opinion/add/',
    urlname='position_add_opinion_view',
    view=position_add_opinion_view
)
admin.site.register_view(
    'position/opinion/add/'
    '(?P<id>[0-9]+)/(?P<date>\d{4}-\d{2}-\d{2})/'
    '(?P<direction>[a-z]+)/(?P<decision>[a-z]+)/$',
    urlname='position_add_opinion_view',
    view=position_add_opinion_view
)

# update opinion results
admin.site.register_view(
    'position/opinion/set_results/',
    urlname='update_opinion_results',
    view=update_opinion_results
)
