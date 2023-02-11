# Plugin information
__plugin_name__ = "Klipper Config Updater"
__plugin_version__ = "1.0.0"
__plugin_description__ = "Automatically update Klipper configuration files from GitHub."
__plugin_pythoncompat__ = "2.7,<4"  # This plugin is compatible with Python 2.7

# Import required modules
import octoprint.plugin
import octoprint.util
import requests
import threading
import time
import shutil
import os

class KlipperConfigUpdaterPlugin(octoprint.plugin.SettingsPlugin,
                                  octoprint.plugin.StartupPlugin):

    def __init__(self):
        self._update_thread = None
        self._update_interval = None

    def get_settings_defaults(self):
        return dict(
            repo_url = "https://github.com/FracktalWorks/Klipper_CFG/raw/main/Twin%20Dragon_IDEX.cfg",
            update_interval = 15
        )

    def on_settings_save(self, data):
        octoprint.plugin.SettingsPlugin.on_settings_save(self, data)
        self._update_interval = int(self._settings.get(["update_interval"]))

    def on_after_startup(self):
        self._update_interval = int(self._settings.get(["update_interval"]))
        self.start_update_thread()

    def start_update_thread(self):
        if self._update_thread is None or not self._update_thread.is_alive():
            self._update_thread = threading.Thread(target=self.update_config_file)
            self._update_thread.daemon = True
            self._update_thread.start()

    def update_config_file(self):
        while True:
            try:
                url = self._settings.get(["repo_url"])
                response = requests.get(url, stream=True)
                if response.status_code == 200:
                    with open("/home/pi/printer.cfg", 'wb') as f:
                        response.raw.decode_content = True
                        shutil.copyfileobj(response.raw, f)
                        octoprint.util.comm.printer.synchronize()
                        self._plugin_manager.send_plugin_message(self._identifier, dict(type="success"))
            except Exception as e:
                self._logger.exception("Exception during config update: {}".format(e))

            time.sleep(self._update_interval * 86400)

    def get_update_information(self):
        return dict(
            klipper_config_updater=dict(
                displayName="Klipper Config Updater",
                displayVersion=self._plugin_version,
                type="github_release",
                user="octoprint",
                repo="octoprint-klipper-config-updater",
                current=self._plugin_version,
                pip="https://github.com/octoprint/octoprint-klipper-config-updater/archive/{target_version}.zip"
            )
        )

__plugin_name__ = "Klipper Config Updater"
__plugin_version__ = "1.0.0"
__plugin_description__ = "Automatically update Klipper configuration files from GitHub."
__plugin_implementation__ = KlipperConfigUpdaterPlugin()
