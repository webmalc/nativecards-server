"""
The nativecards admin module
"""
from django import forms
from django.contrib import admin
from django.core.validators import ValidationError
from django.urls import reverse
from django.utils.safestring import mark_safe
from reversion.admin import VersionAdmin

from .models import Settings


class ShowAllInlineAdminMixin(admin.TabularInline):
    """
    The mixin to show a link to all entries in inline admin classes
    """

    def get_formset(self, request, obj=None, **kwargs):
        self.parent_obj = obj
        return super().get_formset(request, obj, **kwargs)

    def all(self, request):
        """
        Returns a link HTML code
        """
        template = """
        <a href="{}?created_by__id__exact={}" target="_blank">Show all</a>
        """
        return mark_safe(
            template.format(reverse(self.all_url),
                            self.parent_obj.created_by.id))


class SettingsAdminForm(forms.ModelForm):
    """
    The settings admin form class
    """

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        """
        Validation
        """
        query = Settings.objects.filter(created_by=self.request.user)
        if self.instance.pk:
            query = query.exclude(pk=self.instance.pk)
        if query.count():
            raise ValidationError(
                'The settings object already exists for this user.')
        return super().clean()


@admin.register(Settings)
class SettingsAdmin(VersionAdmin):
    """
    The settings admin interface
    """
    form = SettingsAdminForm
    list_display = ('id', 'attempts_to_remember', 'cards_per_lesson',
                    'cards_to_repeat', 'lesson_latest_days', 'lessons_per_day',
                    'play_audio_on_open', 'created', 'created_by')
    list_display_links = ('id', 'attempts_to_remember', 'cards_per_lesson',
                          'cards_to_repeat', 'lesson_latest_days')
    list_filter = ('created_by', 'created')
    search_fields = ('=pk', 'created_by__username', 'created_by__email',
                     'created_by__last_name')
    readonly_fields = ('created', 'modified', 'created_by', 'modified_by',
                       'attempts_per_day')
    fieldsets = (
        ('General', {
            'fields':
            ('attempts_to_remember', 'cards_per_lesson', 'cards_to_repeat',
             'lesson_latest_days', 'lessons_per_day', 'attempts_per_day',
             'play_audio_on_open')
        }),
        ('Options', {
            'fields': ('created', 'modified', 'created_by', 'modified_by')
        }),
    )
    list_select_related = ('created_by', )

    def get_form(self, request, obj=None, change=False, **kwargs):
        """
        Returns the settings admin form
        """
        admin_form = super().get_form(request, obj, **kwargs)

        class ModelFormMetaClass(admin_form):
            """
            Admin form metaclass
            """

            def __new__(cls, *args, **kwargs):
                kwargs['request'] = request
                return admin_form(*args, **kwargs)

        return ModelFormMetaClass
