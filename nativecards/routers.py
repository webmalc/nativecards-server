"""
The router model
"""
from rest_framework.routers import DefaultRouter as BaseRouter


class DefaultRouter(BaseRouter):
    """
    The default router class
    """
    def extend(self, *args):
        """
        Extends the default router with other routers
        """
        for router in args:
            self.registry.extend(router.registry)
