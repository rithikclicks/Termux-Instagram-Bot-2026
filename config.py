import json
import os

class Config:
    SETTINGS_FILE = 'settings.json'
    SESSION_FILE = 'session.json'

    DEFAULT_SETTINGS = {
        "services": {
            "timeline_liker": {
                "enabled": False, 
                "delay_min": 30, 
                "delay_max": 60,
                "source_type": "hashtag", # hashtag, location, followers, following
                "source_value": "instagram"
            },
            "timeline_commenter": {
                "enabled": False, 
                "delay_min": 60, 
                "delay_max": 120, 
                "comments": ["Nice!", "Great shot!", "Love this!"],
                "source_type": "hashtag",
                "source_value": "photography"
            },
            "story_watcher": {
                "enabled": False, 
                "delay_min": 20, 
                "delay_max": 40,
                "like_stories": True,
                "source_type": "feed", # feed, hashtag, location, followers, following
                "source_value": "none"
            }
        },
        "username": "",
        "password": ""
    }

    def __init__(self):
        self.settings = self.load_settings()

    def load_settings(self):
        if not os.path.exists(self.SETTINGS_FILE):
            self.save_settings(self.DEFAULT_SETTINGS)
            return self.DEFAULT_SETTINGS
        
        try:
            with open(self.SETTINGS_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return self.DEFAULT_SETTINGS

    def save_settings(self, settings=None):
        if settings is None:
            settings = self.settings
        
        with open(self.SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=4)
        self.settings = settings

    def get_service_config(self, service_name):
        return self.settings.get("services", {}).get(service_name, {})

    def update_service_config(self, service_name, key, value):
        if "services" not in self.settings:
            self.settings["services"] = {}
        if service_name not in self.settings["services"]:
            self.settings["services"][service_name] = {}
        
        self.settings["services"][service_name][key] = value
        self.save_settings()

    def set_credentials(self, username, password):
        self.settings["username"] = username
        self.settings["password"] = password
        self.save_settings()

    def get_credentials(self):
        return self.settings.get("username"), self.settings.get("password")
