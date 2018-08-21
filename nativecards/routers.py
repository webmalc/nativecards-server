from rest_framework.routers import DefaultRouter as BaseRouter


class DefaultRouter(BaseRouter):
    def extend(self, *args):
        for router in args:
            self.registry.extend(router.registry)
