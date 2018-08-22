from django.contrib import admin
from django.utils.safestring import mark_safe
from imagekit.admin import AdminThumbnail
from ordered_model.admin import OrderedModelAdmin
from reversion.admin import VersionAdmin

from .models import Card, Deck


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
    list_filter = ('deck', 'priority', 'created_by', 'created',
                   'last_showed_at', 'is_enabled')
    search_fields = ('=pk', 'word', 'definition', 'translation', 'examples',
                     'created_by__username', 'created_by__email',
                     'created_by__last_name')
    readonly_fields = ('created', 'modified', 'last_showed_at', 'created_by',
                       'modified_by')
    fieldsets = (
        ('General', {
            'fields': ('word', 'deck', 'definition', 'examples', 'translation',
                       'pronunciation', 'image', 'remote_image')
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
