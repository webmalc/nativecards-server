import arrow
from django.contrib import admin
from django.utils.safestring import mark_safe
from imagekit.admin import AdminThumbnail
from nativecards.admin import ShowAllInlineAdminMixin
from ordered_model.admin import OrderedModelAdmin
from reversion.admin import VersionAdmin

from .models import Attempt, Card, Deck


@admin.register(Attempt)
class AttemptAdmin(VersionAdmin):
    """
    The attempt's admin interface
    """
    list_display = ('id', 'form', 'card', 'is_correct', 'is_hint', 'answer',
                    'score', 'created', 'created_by')
    list_display_links = ('id', 'form')
    list_filter = ('is_correct', 'is_hint', 'created_by', 'created')
    search_fields = ('=id', 'card__word', 'answer', 'created_by__username',
                     'created_by__email', 'created_by__last_name')
    readonly_fields = ('created', 'modified', 'created_by', 'modified_by',
                       'score')
    raw_id_fields = ('card', )
    fieldsets = (
        ('General', {
            'fields': ('form', 'card', 'is_correct', 'is_hint', 'answer')
        }),
        ('Options', {
            'fields': ('score', 'created', 'modified', 'created_by',
                       'modified_by')
        }),
    )
    list_select_related = ('created_by', 'card')


class AttemptInlineAdmin(ShowAllInlineAdminMixin):
    """
    The attempt's inline admin interface
    """
    model = Attempt
    fields = ('form', 'is_correct', 'is_hint', 'answer', 'score', 'created',
              'all')
    verbose_name_plural = "Last attempts (1 month)"
    readonly_fields = ('created', 'score', 'all')
    show_change_link = True
    all_url = 'admin:cards_attempt_changelist'

    def get_queryset(self, request):
        query = super().get_queryset(request)
        date_limit = arrow.utcnow().shift(months=-1).datetime
        return query.filter(created__gte=date_limit)


@admin.register(Card)
class CardAdmin(VersionAdmin):
    """
    The cards's admin interface
    """
    list_display = ('id', 'admin_thumbnail', 'word', 'translation', 'audio',
                    'deck', 'priority', 'complete', 'last_showed_at',
                    'is_enabled', 'created', 'created_by')
    admin_thumbnail = AdminThumbnail(image_field='image')
    list_display_links = ('id', 'word')
    list_filter = ('deck', 'priority', 'category', 'created_by', 'created',
                   'last_showed_at', 'is_enabled')
    search_fields = ('=pk', 'word', 'definition', 'translation', 'examples',
                     'created_by__username', 'created_by__email',
                     'created_by__last_name')
    readonly_fields = ('created', 'modified', 'last_showed_at', 'created_by',
                       'modified_by')
    inlines = (AttemptInlineAdmin, )
    fieldsets = (
        ('General', {
            'fields': ('word', 'deck', 'category', 'definition', 'examples',
                       'synonyms', 'antonyms', 'translation', 'transcription',
                       'pronunciation', 'note', 'image', 'remote_image')
        }),
        ('Options', {
            'fields': ('priority', 'complete', 'is_enabled', 'last_showed_at',
                       'created', 'modified', 'created_by', 'modified_by')
        }),
    )
    list_select_related = ('created_by', 'deck')

    def audio(self, obj):
        if not obj.pronunciation:
            return None
        html = """
            <audio id="audio_{id}">
                <source src="{file}">
            </audio>
            <a href="#" data-audio="audio_{id}">►</a>
        """

        return mark_safe(html.format(id=obj.pk, file=obj.pronunciation))

    class Media:
        css = {'all': ('css/admin/cards.css', )}
        js = ('js/admin/cards.js', )


@admin.register(Deck)
class DeckAdmin(VersionAdmin, OrderedModelAdmin):
    """
    The deck's admin interface
    """
    list_display = ('id', 'admin_thumbnail', 'title', 'description',
                    'is_default', 'is_enabled', 'created', 'created_by',
                    'move_up_down_links')
    admin_thumbnail = AdminThumbnail(image_field='image')
    list_display_links = ('id', 'title')
    list_filter = ('is_default', 'is_enabled', 'created_by', 'created')
    search_fields = ('=pk', 'title', 'description', 'created_by__username',
                     'created_by__email', 'created_by__last_name')
    readonly_fields = ('created', 'modified', 'created_by', 'modified_by')
    fieldsets = (
        ('General', {
            'fields': ('title', 'description', 'image', 'remote_image')
        }),
        ('Options', {
            'fields': ('is_default', 'is_enabled', 'created', 'modified',
                       'created_by', 'modified_by')
        }),
    )
    list_select_related = ('created_by', )
