class UserViewSetMixin():
    """
    The mixin with created_by field filter
    """

    def filter_by_user(self, query):
        return query.filter(created_by=self.request.user).select_related(
            'created_by', 'modified_by')
