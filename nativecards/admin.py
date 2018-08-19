from django.contrib import admin
from django.contrib.postgres.fields import JSONField
from django.shortcuts import redirect
from django.urls import reverse
from prettyjson import PrettyJSONWidget


class TextFieldListFilter(admin.ChoicesFieldListFilter):
    template = "filters/text_field.html"

    def choices(self, changelist):
        yield {
            'selected':
            False,
            'query_string':
            changelist.get_query_string({
                self.lookup_kwarg: 0
            }, [self.lookup_kwarg_isnull]),
            'query_param':
            self.lookup_kwarg,
            'display':
            self.field
        }


class JsonAdmin(admin.ModelAdmin):
    formfield_overrides = {
        JSONField: {
            'widget': PrettyJSONWidget(attrs={'initial': 'parsed'})
        }
    }


class ShowAllInlineAdminMixin(admin.TabularInline):
    def get_formset(self, request, obj=None, **kwargs):
        self.parent_obj = obj
        return super().get_formset(request, obj, **kwargs)

    def all(self, request):
        template = """
        <a href="{}?client__login__exact={}" target="_blank">Show all</a>
        """
        return template.format(reverse(self.all_url), self.parent_obj.login)

    all.allow_tags = True  # type: ignore


class ManagerListMixin(admin.ModelAdmin):
    """
    Change list with list_manager perm
    """

    def has_view_permission(self, request, obj=None):
        opts = self.opts
        if request.user.has_perm('{}.list_manager'.format(opts.app_label)):
            return True
        return super().has_view_permission(request, obj)

    def get_queryset(self, request):
        query = super().get_queryset(request)
        if not super().has_view_permission(request):
            query = query.filter(client__manager=request.user)
        return query


class ManagerInlineListMixin(admin.TabularInline):
    """
    Change list with list_manager perm
    """

    def has_change_permission(self, request, obj=None):
        opts = self.opts
        if request.user.has_perm('{}.list_manager'.format(opts.app_label)):
            return True
        return super().has_change_permission(request, obj)

    def get_queryset(self, request):
        query = super().get_queryset(request)
        if not super().has_change_permission(request):
            query = query.filter(client__manager=request.user)
        return query


class ArchorAdminMixin(admin.ModelAdmin):
    """
    Admin with list archors
    """

    def num(self, obj):
        return '<a name="el_{0}"/>{0}'.format(obj.pk)

    num.allow_tags = True  # type: ignore

    def response_post_save_change(self, request, obj):
        parent = super().response_post_save_change(request, obj)
        return redirect('{}#el_{}'.format(parent.url, obj.pk))

    def response_post_save_add(self, request, obj):
        return self.response_post_save_change(request, obj)


class ChangeOwnMixin():
    """
    Change created by user object only
    """

    def has_change_permission(self, request, obj=None):
        parent = super().has_change_permission(request, obj)
        if not parent:
            return parent
        if obj is not None and obj.created_by != request.user:
            return False
        return True

    def has_delete_permission(self, request, obj=None):
        parent = super().has_delete_permission(request, obj)
        if not parent:
            return parent
        if obj is not None and obj.created_by != request.user:
            return False
        return True


class DictAdminMixin():
    """
    DictAdminMixin admin interface
    """

    list_display_links = ['id', 'title']
    list_select_related = [
        'modified_by',
    ]
    search_fields = ['=pk', 'title', 'description']
    readonly_fields = [
        'code', 'created', 'modified', 'created_by', 'modified_by'
    ]
    actions = None

    def get_fieldsets(self, request, obj=None):
        return [
            ['General', {
                'fields': ['title', 'description']
            }],
            [
                'Options', {
                    'fields': [
                        'is_enabled', 'code', 'created', 'modified',
                        'created_by', 'modified_by'
                    ]
                }
            ],
        ]

    def get_list_display(self, request):
        return ['id', 'title', 'code', 'is_enabled', 'modified', 'modified_by']

    def has_delete_permission(self, request, obj=None):
        parent = super().has_delete_permission(request, obj)
        if parent and obj and obj.code:
            return False
        return parent
