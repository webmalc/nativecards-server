from django.contrib import admin
from imagekit.admin import AdminThumbnail
from ordered_model.admin import OrderedModelAdmin
from reversion.admin import VersionAdmin

from .models import Deck


@admin.register(Deck)
class DeckAdmin(VersionAdmin, OrderedModelAdmin):
    """
    The deck's admin interface
    """
    list_display = ('id', 'title', 'description', 'is_default', 'is_enabled',
                    'created', 'created_by', 'admin_thumbnail',
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
