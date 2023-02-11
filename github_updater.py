# Plugin meta-data
__plugin_name__ = "Klipper Config Updater"
__plugin_version__ = "1.0.0"
__plugin_description__ = "Updates Klipper printer.cfg from Github repo"
__plugin_pythoncompat__ = ">=3.7,<4"

# Plugin imports
import octoprint.plugin
import requests
import shutil
import os
import threading

class KlipperConfigUpdaterPlugin(octoprint.plugin.StartupPlugin,
                                  octoprint.plugin.TemplatePlugin,
                                  octoprint.plugin.AssetPlugin):
    def on_after_startup(self):
        self._logger.info("Klipper Config Updater started")
        self.start_update_thread()

    def get_assets(self):
        return {
            "js": ["js/klipper_config_updater.js"]
        }

    def get_template_configs(self):
        return [
            dict(type="settings", custom_bindings=False)
        ]

    def start_update_thread(self):
        self.update_thread = threading.Timer(15 * 24 * 60 * 60, self.update_config)
        self.update_thread.start()

    def update_config(self):
        self._logger.info("Checking for updates...")
        url = "https://github.com/FracktalWorks/Klipper_CFG/raw/main/Twin%20Dragon_IDEX.cfg"
        r = requests.get(url, allow_redirects=True)
        if r.status_code == 200:
            filename = os.path.join(os.path.expanduser("~"), "printer.cfg")
            with open(filename, "wb") as f:
                f.write(r.content)
            self._logger.info("Printer config updated from Github repo")
        else:
            self._logger.info("Printer config update failed. HTTP status code: %d" % r.status_code)

        self.start_update_thread()

__plugin_name__ = "Klipper Config Updater"
__plugin_version__ = "1.0.0"
__plugin_description__ = "Updates Klipper printer.cfg from Github repo"
__plugin_pythoncompat__ = ">=3.7,<4"

def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = KlipperConfigUpdaterPlugin()
    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
    }
