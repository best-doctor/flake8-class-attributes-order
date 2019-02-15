DEBUG = True


class User:
    def fetch_info_from_crm(self):
        pass

    LOGIN_FIELD = 'email'  # wtf? this should on top of class definition!


class UserNode:
    class Meta:
        model = User

    if DEBUG:  # not great idea at all
        def is_synced_with_crm(self):
            pass
