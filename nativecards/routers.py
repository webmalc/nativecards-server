from rest_framework.routers import DefaultRouter


class DefaultRouter(DefaultRouter):
    def extend(self, *args):
        for router in args:
            self.registry.extend(router.registry)
