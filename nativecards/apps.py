"""
The nativecards apps module
"""
from django.apps import AppConfig


class NativecardsConfig(AppConfig):
    """
    The nativecards apps configuration
    """
    name = 'nativecards'

    def ready(self):
        """
        Imports signals
        """
        # pylint: disable=unused-import, import-outside-toplevel
        import nativecards.signals
