"""
The users admin module
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import Profile


class ProfileInline(admin.StackedInline):
    """
    The profile inline admin
    """
    model = Profile
    can_delete = False


class UserAdmin(BaseUserAdmin):
    """
    The profile inline admin
    """
    inlines = (ProfileInline, )
    list_select_related = ('profile', )

    def get_list_display(self, requset):
        """
        Admin list display
        """
        list_display = list(super().get_list_display(requset))
        list_display.append('is_verified')
        return list_display

    @staticmethod
    def is_verified(obj):
        """
        Check if an user is verified
        """
        return obj.profile.is_verified

    is_verified.boolean = True  # type: ignore


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
