import os
import sys
import json
import logging
from win32com.client import Dispatch

SETTINGS_FILE = os.path.join(os.getenv('APPDATA'), 'ImageEditor', 'settings.json')


class SettingsManager:
    @staticmethod
    def load() -> dict:
        try:
            with open(SETTINGS_FILE, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except Exception as e:
            logging.error(f"Error loading settings: {str(e)}")
            return {}

    @staticmethod
    def save(settings: dict):
        os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f)

    @staticmethod
    def set_startup(enable: bool):
        try:
            exe_path = os.path.abspath(sys.executable)
            startup_folder = os.path.join(
                os.getenv('APPDATA'),
                r'Microsoft\Windows\Start Menu\Programs\Startup'
            )
            shortcut = os.path.join(startup_folder, 'QuickImgEditor.lnk')
            if enable:
                shell = Dispatch('WScript.Shell')
                link = shell.CreateShortCut(shortcut)
                link.Targetpath = exe_path
                link.WorkingDirectory = os.path.dirname(exe_path)
                link.IconLocation = exe_path + ",0"
                link.save()
            else:
                if os.path.exists(shortcut):
                    os.remove(shortcut)
        except Exception as e:
            logging.error(f"Startup setting failed: {str(e)}")
