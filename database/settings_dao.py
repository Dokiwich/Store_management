class SettingsDAO:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def get_all_settings(self):
        conn = self.db_manager.get_connection()
        settings = {}
        if conn:
            cursor = None
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT setting_key, setting_value FROM system_settings")
                for k, v in cursor.fetchall():
                    settings[k] = v
            except Exception as e:
                print(f"Error fetching settings: {e}")
            finally:
                if cursor: cursor.close()
                conn.close()
        return settings

    def get_setting(self, key, default=None):
        conn = self.db_manager.get_connection()
        if conn:
            cursor = None
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT setting_value FROM system_settings WHERE setting_key = %s", (key,))
                row = cursor.fetchone()
                if row:
                    return row[0]
            except Exception as e:
                print(f"Error fetching setting {key}: {e}")
            finally:
                if cursor: cursor.close()
                conn.close()
        return default

    def update_setting(self, key, value):
        conn = self.db_manager.get_connection()
        if conn:
            cursor = None
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO system_settings (setting_key, setting_value)
                    VALUES (%s, %s)
                    ON DUPLICATE KEY UPDATE setting_value = VALUES(setting_value)
                """, (key, str(value)))
                conn.commit()
                return True
            except Exception as e:
                conn.rollback()
                print(f"Error updating setting {key}: {e}")
                return False
            finally:
                if cursor: cursor.close()
                conn.close()
        return False

    def update_multiple_settings(self, settings_dict):
        conn = self.db_manager.get_connection()
        if conn:
            cursor = None
            try:
                cursor = conn.cursor()
                for k, v in settings_dict.items():
                    cursor.execute("""
                        INSERT INTO system_settings (setting_key, setting_value)
                        VALUES (%s, %s)
                        ON DUPLICATE KEY UPDATE setting_value = VALUES(setting_value)
                    """, (k, str(v)))
                conn.commit()
                return True
            except Exception as e:
                conn.rollback()
                print(f"Error updating multiple settings: {e}")
                return False
            finally:
                if cursor: cursor.close()
                conn.close()
        return False
