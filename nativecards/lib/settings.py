from django.conf import settings

from nativecards.models import Settings

SETTINGS = {}  # type: ignore
RELOAD = False  # type: ignore


def get(id: str, user=None):
    """
    Get settings
    """
    default = getattr(settings, 'NC_' + id.upper(), None)
    if user:
        if user.id not in SETTINGS or RELOAD:
            user_settings = Settings.objects.get_by_user(user)
            SETTINGS[user.id] = user_settings
        return getattr(SETTINGS[user.id], id, default)
    return default


def clear_mermory_cache(user):
    """
    Clear user settings in-memory cache
    """
    return SETTINGS.pop(user.id, None)
