# OctoPrint Plugin to automatically update printer.cfg from GitHub

import octoprint.plugin
import requests

class PrinterConfigUpdaterPlugin(octoprint.plugin.StartupPlugin):
	def on_after_startup(self):
		owner = "FracktalWorks"
		repo = "Klipper_CFG"
		filename = "Twin Dragon IDEX.cfg"
		local_path = "/home/pi/printer.cfg"
		update_interval = 1 # in days
		
		# Check for an update
		try:
			response = requests.get(f"https://github.com/FracktalWorks/Klipper_CFG/raw/main/Twin%20Dragon_IDEX.cfg")
			response.raise_for_status()
			commit = response.json()
			latest_sha = commit['sha']
		except requests.exceptions.RequestException:
			self._logger.exception("Failed to retrieve latest commit from GitHub")
			return

		with open(local_path, "r") as f:
			current_cfg = f.read()
			f.close()

		try:
			response = requests.get(f"https://raw.githubusercontent.com/FracktalWorks/Klipper_CFG/main/Twin%20Dragon_IDEX.cfg")
			response.raise_for_status()
			new_cfg = response.text
		except requests.exceptions.RequestException:
			self._logger.exception("Failed to retrieve new printer.cfg from GitHub")
			return

		if new_cfg != current_cfg:
			with open(local_path, "w") as f:
				f.write(new_cfg)
				f.close()
			self._logger.info("Updated printer.cfg from GitHub")
		else:
			self._logger.info("No updates found in GitHub")

		self.t = threading.Timer(update_interval * 3600, self.on_after_startup)
		self.t.start()
		
__plugin_name__ = "Printer Config Updater"
__plugin_version__ = "1.0.0"
__plugin_description__ = "Automatically updates printer.cfg from a specified GitHub repository"
__plugin_implementation__ = PrinterConfigUpdaterPlugin()
