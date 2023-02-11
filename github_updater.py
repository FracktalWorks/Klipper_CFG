import octoprint.plugin
import requests
import os

class GitHubUpdaterPlugin(octoprint.plugin.StartupPlugin):
    def __init__(self):
        self._repo_url = "https://github.com/FracktalWorks/Klipper_CFG/raw/main/Twin%20Dragon_IDEX.cfg"  # replace with your own repo URL
        self._config_file_path = "/home/pi/printer.cfg"  # replace with the path to your Klipper config file

    def on_after_startup(self):
        self._current_commit_sha = self._get_current_commit_sha()
        self._schedule_update_check()

    def _get_current_commit_sha(self):
        with open(self._config_file_path, "r") as f:
            lines = f.readlines()
            for line in lines:
                if line.startswith("# commit "):
                    return line[len("# commit "):].strip()

    def _download_new_config_file(self):
        r = requests.get(self._repo_url + "/raw/main/printer.cfg")
        if r.status_code == requests.codes.ok:
            with open(self._config_file_path, "w") as f:
                f.write(r.text)
            return True
        else:
            return False

    def _schedule_update_check(self):
        threading.Timer(3600, self._check_for_updates).start()  # check every hour

    def _check_for_updates(self):
        try:
            r = requests.get(self._repo_url + "/commits/main")
            if r.status_code == requests.codes.ok:
                commit_sha = r.json()["sha"]
                if commit_sha != self._current_commit_sha:
                    if self._download_new_config_file():
                        self._current_commit_sha = commit_sha
                        self._show_success_message()
            else:
                self._show_error_message("Unable to check for updates")
        except Exception as e:
            self._show_error_message("Error checking for updates: {}".format(str(e)))
        self._schedule_update_check()

    def _show_success_message(self):
        self._plugin_manager.send_plugin_message(self._identifier, {"type": "success", "message": "Configuration file updated"})

    def _show_error_message(self, message):
        self._plugin_manager.send_plugin_message(self._identifier, {"type": "error", "message": message})
