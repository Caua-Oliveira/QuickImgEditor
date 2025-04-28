import os
import threading
from PIL import Image
import pystray


class TrayManager:
    """System tray icon management."""

    def __init__(self, app):
        self.app = app
        self.icon = None
        self.icon_thread = None

    def create_icon(self):
        menu = pystray.Menu(
            pystray.MenuItem('Open', self.toggle_visibility, default=True),
            pystray.MenuItem('Options', self.show_options),
            pystray.MenuItem('Exit', self.exit_app),
        )
        icon_path = os.path.join(os.path.dirname(__file__), '../resources/icon.ico')
        image = Image.open(icon_path)
        self.icon = pystray.Icon('image_editor', image, 'Image Editor', menu)

    def run(self):
        self.icon_thread = threading.Thread(target=self.icon.run, daemon=True)
        self.icon_thread.start()

    def toggle_visibility(self):
        self.app.after(0, self.app.toggle_visibility)

    def show_options(self):
        self.app.after(0, self.app.open_options_page)

    def exit_app(self):
        self.icon.stop()
        self.app.after(0, self.app.destroy)
