"""
The users app module
"""
from django.apps import AppConfig


class UsersConfig(AppConfig):
    """
    The cards app configuration
    """
    name = 'users'

    def ready(self):
        """
        Imports the app signals
        """
        # pylint: disable=unused-import, import-outside-toplevel
        import users.signals
