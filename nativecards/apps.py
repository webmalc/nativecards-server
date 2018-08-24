from django.apps import AppConfig


class NativecardsConfig(AppConfig):
    name = 'nativecards'

    def ready(self):
        import nativecards.signals
