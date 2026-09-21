class SettingsService:
    def __init__(self, settings_dao):
        self.dao = settings_dao

    def get_all(self):
        return self.dao.get_all_settings()

    def get(self, key, default=None):
        return self.dao.get_setting(key, default)

    def set(self, key, value):
        return self.dao.update_setting(key, value)

    def update_settings(self, settings_dict):
        return self.dao.update_multiple_settings(settings_dict)
