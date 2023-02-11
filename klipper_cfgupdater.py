# Plugin meta-data
__plugin_name__ = "Klipper Config Updater"
__plugin_version__ = "1.0.0"
__plugin_description__ = "Updates Klipper printer.cfg from Github repo"
__plugin_pythoncompat__ = ">=2.7,<4"

# octoprint_klipper_cfgupdater/__init__.py

import octoprint.plugin
import os
import threading
import urllib2
import shutil


class KlipperCfgUpdaterPlugin(octoprint.plugin.StartupPlugin,
                              octoprint.plugin.SettingsPlugin,
                              octoprint.plugin.AssetPlugin,
                              octoprint.plugin.TemplatePlugin):
    def __init__(self):
        self.update_timer = None

    def get_settings_defaults(self):
        return dict(
            repo_url='https://github.com/FracktalWorks/Klipper_CFG/raw/main/printer.cfg',
            update_interval=15
        )

    def get_update_check_interval(self):
        return int(self._settings.get(["update_interval"])) * 24 * 60 * 60

    def update_configuration(self):
        url = self._settings.get(["repo_url"])
        response = urllib2.urlopen(url)
        data = response.read()
        path = os.path.join(os.path.expanduser("~"), ".octoprint/printer.cfg")
        with open(path, 'wb') as f:
            f.write(data)

    def on_after_startup(self):
        self.update_timer = threading.Timer(self.get_update_check_interval(), self.update_configuration)
        self.update_timer.start()

    def on_shutdown(self):
        if self.update_timer is not None:
            self.update_timer.cancel()

    def get_assets(self):
        return dict(
            js=["js/klipper_cfgupdater.js"]
        )

    def get_template_configs(self):
        return [
            dict(type="settings", custom_bindings=True)
        ]

    def get_settings_version(self):
        return 1

    def on_settings_save(self, data):
        octoprint.plugin.SettingsPlugin.on_settings_save(self, data)
        if self.update_timer is not None:
            self.update_timer.cancel()
        self.update_timer = threading.Timer(self.get_update_check_interval(), self.update_configuration)
        self.update_timer.start()

    def on_settings_initialized(self):
        if self.update_timer is not None:
            self.update_timer.cancel()
        self.update_timer = threading.Timer(self.get_update_check_interval(), self.update_configuration)
        self.update_timer.start()

    def get_update_information(self):
        return dict(
            klipper_cfgupdater=dict(
                displayName="Klipper Configuration Updater",
                displayVersion=self._plugin_version,

                type="github_release",
                user="FracktalWorks",
                repo="Klipper_CFG",
                current=self._plugin_version,

                pip="https://github.com/FracktalWorks/Klipper_CFG/releases/latest/download/master.zip"
            )
        )


__plugin_name__ = "Klipper Config Updater"
__plugin_version__ = "1.0.0"
__plugin_description__ = "Updates Klipper printer.cfg from Github repo"
__plugin_pythoncompat__ = ">=2.7,<4"

def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = KlipperConfigUpdaterPlugin()
    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
    }
