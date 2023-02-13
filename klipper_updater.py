# octoprint_klipper_cfgupdater.py

import octoprint.plugin
import requests
import os
import hashlib

class KlipperCfgUpdaterPlugin(octoprint.plugin.SettingsPlugin,
                              octoprint.plugin.StartupPlugin,
                              octoprint.plugin.EventHandlerPlugin):

    def on_after_startup(self):
        self._logger.info("KlipperCfgUpdaterPlugin started!")
        self.update_printer_cfg()

    def update_printer_cfg(self):
        klipper_config_path = self._settings.get(['/home/pi/printer.cfg'])
        github_config_url = self._settings.get(['https://github.com/FracktalWorks/Klipper_CFG/raw/main/Twin%20Dragon_IDEX.cfg'])
        if klipper_config_path is None or github_config_url is None:
            self._logger.warn("KlipperCfgUpdaterPlugin: Configuration incomplete, skipping update")
            return

        if not os.path.exists(klipper_config_path):
            self._logger.warn("KlipperCfgUpdaterPlugin: Klipper config file not found, skipping update")
            return

        response = requests.get(github_config_url)
        if response.status_code == 200:
            new_config_hash = hashlib.sha256(response.content).hexdigest()
            with open(klipper_config_path, 'rb') as klipper_config_file:
                current_config_hash = hashlib.sha256(klipper_config_file.read()).hexdigest()

            if new_config_hash != current_config_hash:
                with open(klipper_config_path, 'wb') as klipper_config_file:
                    klipper_config_file.write(response.content)
                    self._logger.info("KlipperCfgUpdaterPlugin: Updated Klipper config file at %s", klipper_config_path)
                    self._plugin_manager.send_plugin_message(self._identifier, dict(type="success", message="Klipper config file updated"))
            else:
                self._logger.info("KlipperCfgUpdaterPlugin: Klipper config file already up-to-date")
        else:
            self._logger.warn("KlipperCfgUpdaterPlugin: Failed to retrieve Klipper config file, status code: %s", response.status_code)

    def get_settings_defaults(self):
        return dict(
            klipper_config_path="/home/pi/printer.cfg",
            github_config_url="https://raw.githubusercontent.com/FracktalWorks/Klipper_CFG/main/Twin%20Dragon_IDEX.cfg"
        )

    def get_settings_restricted_paths(self):
        return dict(admin=[['/home/pi/printer.cfg']])

    def on_settings_save(self, data):
        octoprint.plugin.SettingsPlugin.on_settings_save(self, data)
        self.update_printer_cfg()

    def on_settings_initialized(self):
        self.update_printer_cfg()

    def get_template_configs(self):
        return [
            dict(type="settings", custom_bindings=False)
        ]

    def get_update_information(self):
        return dict(
            klipper_cfgupdater=dict(
                displayName="Klipper Config Updater",
                displayVersion=self._plugin_version,

                type="github_release",
                user="FracktalWorks",
                repo="Klipper_CFG",
                current=self._plugin_version,

                pip="https://github.com/FracktalWorks/Klipper_CFG/archive/{target_version}.zip"
            )
        )


__plugin_name__ = "Klipper Config Updater"
__plugin_pythoncompat__ = ">=2.7,<4"
__plugin_implementation__ = KlipperCfgUpdaterPlugin()
