"""
The words admin module
"""
from django.contrib import admin
from django.utils.safestring import mark_safe
from markdownx.admin import MarkdownxModelAdmin
from reversion.admin import VersionAdmin

from .models import Word


class WordAudioMixin(admin.ModelAdmin):
    """
    The admin mixin to dispaly an audio tag
    """
    @staticmethod
    def audio(obj):
        """
        Get the HTML code for the word pronunciation audio file
        """
        if not obj.pronunciation:
            return None
        html = """
            <audio id="audio_{id}">
                <source src="{file}">
            </audio>
            <a href="#" data-audio="audio_{id}">►</a>
        """

        return mark_safe(  # nosec
            html.format(
                id=obj.pk,
                file=obj.pronunciation,
            ))


@admin.register(Word)
class WordAdmin(VersionAdmin, MarkdownxModelAdmin, WordAudioMixin):
    """
    The words admin interface
    """
    list_display = ('id', 'word', 'category', 'audio', 'is_enabled', 'created',
                    'created_by')
    list_display_links = ('id', 'word')
    list_filter = ('category', 'created_by', 'created', 'is_enabled')
    search_fields = ('=pk', 'word', 'definition', 'examples',
                     'created_by__username', 'created_by__email',
                     'created_by__last_name')
    readonly_fields = ('created', 'modified', 'created_by', 'modified_by')
    fieldsets = (
        ('General', {
            'fields':
            ('word', 'category', 'definition', 'examples', 'synonyms',
             'antonyms', 'translations', 'transcription', 'pronunciation')
        }),
        ('Options', {
            'fields':
            ('is_enabled', 'created', 'modified', 'created_by', 'modified_by')
        }),
    )
    list_select_related = ('created_by', )

    class Media:
        css = {'all': ('css/admin/cards.css', )}
        js = ('js/admin/cards.js', )
