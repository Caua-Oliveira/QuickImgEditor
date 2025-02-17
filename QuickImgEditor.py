import shutil
import tkinter as tk
from win32com.client import Dispatch
from tkinter import filedialog
import customtkinter as ctk
import sys
import os
import keyboard
import pystray
import threading
import logging
from io import BytesIO
import win32clipboard
from PIL import Image, ImageGrab, ImageOps
from datetime import datetime
import json
import winreg
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
THUMBNAIL_SIZE = (700, 700)
DEFAULT_SCALE = 100
SETTINGS_FILE = os.path.join(os.getenv('APPDATA'), 'ImageEditor', 'settings.json')


# -----------------------------
# Clipboard Manager
# -----------------------------
class ClipboardManager:
    """Handles clipboard operations with error handling and format support."""

    @staticmethod
    def get_image_from_clipboard() -> Optional[Image.Image]:
        try:
            image = ImageGrab.grabclipboard()
            if isinstance(image, Image.Image):
                logging.info("Image retrieved from clipboard")
                return image.convert("RGB")
            logging.warning("Clipboard content is not an image")
            return None
        except Exception as e:
            logging.error(f"Clipboard retrieval error: {str(e)}")
            return None

    @staticmethod
    def copy_image_to_clipboard(image: Image.Image) -> bool:
        try:
            output = BytesIO()
            image.save(output, format="BMP")
            data = output.getvalue()[14:]
            output.close()

            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
            win32clipboard.CloseClipboard()
            logging.info("Image copied to clipboard")
            return True
        except Exception as e:
            logging.error(f"Clipboard copy failed: {str(e)}")
            try:
                win32clipboard.CloseClipboard()
            except Exception:
                pass
            return False


# -----------------------------
# Image Processor
# -----------------------------
class ImageProcessor:
    """Image processing operations."""

    @classmethod
    def scale(cls, image: Image.Image, scale_factor: float) -> Image.Image:
        new_width = int(image.width * scale_factor)
        new_height = int(image.height * scale_factor)
        return image.resize((new_width, new_height), Image.Resampling.LANCZOS)

    @classmethod
    def resize(cls, image: Image.Image, width: int, height: int) -> Image.Image:
        if width <= 0 or height <= 0:
            raise ValueError("Dimensions must be positive integers")
        return image.resize((width, height), Image.Resampling.LANCZOS)

    @classmethod
    def to_grayscale(cls, image: Image.Image) -> Image.Image:
        return ImageOps.grayscale(image)

    @classmethod
    def low_quality(cls, image: Image.Image) -> Image.Image:
        w, h = image.size
        temp = image.resize((max(1, w // 3), max(1, h // 3)), Image.Resampling.LANCZOS)
        return temp.resize((w, h), Image.Resampling.LANCZOS)


# -----------------------------
# Tray Manager
# -----------------------------
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
        image = Image.open("icon.ico")
        self.icon = pystray.Icon("image_editor", image, "Image Editor", menu)

    def run(self):
        self.icon_thread = threading.Thread(target=self.icon.run, daemon=True)
        self.icon_thread.start()

    def toggle_visibility(self, icon, item):
        self.app.after(0, self.app.toggle_visibility)

    def show_options(self, icon, item):
        self.app.after(0, self.app.open_options_page)

    def exit_app(self, icon, item):
        self.icon.stop()
        self.app.after(0, self.app.destroy)


# -----------------------------
# Main Application
# -----------------------------
class ImageEditorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("QuickImgEditor")
        self.geometry("1000x700")

        # Image states
        self.original_image = None
        self.base_image = None
        self.processed_image = None
        self.current_scale = DEFAULT_SCALE
        self.is_scaling = False

        # Settings
        self.min_scale = 10
        self.max_scale = 200
        self.hotkey = 'ctrl+shift+b'
        self.run_at_startup = False
        self.load_settings()

        # UI components
        self.options_window = None
        self.setup_ui()
        self.setup_bindings()
        self.setup_tray()
        self.load_initial_image()

    def setup_ui(self):
        ctk.set_appearance_mode("dark")
        self.load_theme()
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.create_control_panel()
        self.create_image_preview()
        self.create_status_bar()

    def load_theme(self):
        try:
            theme_path = 'theme.json' if os.path.exists('theme.json') else None
            if theme_path:
                ctk.set_default_color_theme(theme_path)
        except Exception as e:
            logging.error(f"Error loading theme: {str(e)}")

    def setup_bindings(self):
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        keyboard.add_hotkey(self.hotkey, self.toggle_visibility)
        self.bind("<Control-v>", lambda e: self.load_from_clipboard())
        self.bind("<Control-c>", lambda e: self.copy_to_clipboard())

    def setup_tray(self):
        self.tray = TrayManager(self)
        self.tray.create_icon()
        self.tray.run()

    def create_control_panel(self):
        self.control_frame = ctk.CTkFrame(self)
        self.control_frame.grid(row=0, column=0, sticky="ns", padx=5, pady=5)

        self.create_action_buttons()
        self.create_processing_buttons()
        self.create_resize_controls()
        self.create_scale_controls()
        self.create_export_buttons()

    def create_action_buttons(self):
        actions = [
            ("Load from Clipboard", self.load_from_clipboard),
            ("Choose Image", self.choose_image),
            ("Revert to Original", self.revert_to_original)
        ]
        for text, cmd in actions:
            btn = ctk.CTkButton(self.control_frame, text=text, command=cmd)
            btn.pack(pady=3, fill='x')

    def create_processing_buttons(self):
        processing_frame = ctk.CTkFrame(self.control_frame)
        processing_frame.pack(pady=10, fill='x')

        effects = [
            ("Convert to Grayscale", self.convert_to_grayscale),
            ("Low Quality", self.low_quality)
        ]
        for text, cmd in effects:
            btn = ctk.CTkButton(processing_frame, text=text, command=cmd)
            btn.pack(pady=2, fill='x')

    def create_resize_controls(self):
        resize_frame = ctk.CTkFrame(self.control_frame)
        resize_frame.pack(pady=10, fill='x')

        # Width
        self.width_var = tk.StringVar()
        ctk.CTkEntry(resize_frame, textvariable=self.width_var).pack(pady=2, fill='x')

        # Height
        self.height_var = tk.StringVar()
        ctk.CTkEntry(resize_frame, textvariable=self.height_var).pack(pady=2, fill='x')

        ctk.CTkButton(resize_frame, text="Resize", command=self.resize_image).pack(pady=5, fill='x')

    def create_scale_controls(self):
        scale_frame = ctk.CTkFrame(self.control_frame)
        scale_frame.pack(pady=10, fill='x')

        self.scale_slider = ctk.CTkSlider(
            scale_frame,
            from_=self.min_scale,
            to=self.max_scale,
            command=self.on_scale_slide
        )
        self.scale_slider.set(DEFAULT_SCALE)
        self.scale_slider.pack(side='left', expand=True, fill='x', padx=5)

        self.scale_label = ctk.CTkLabel(scale_frame, text=f"{DEFAULT_SCALE}%")
        self.scale_label.pack(side='left')

    def create_export_buttons(self):
        export_frame = ctk.CTkFrame(self.control_frame)
        export_frame.pack(pady=10, fill='x')

        actions = [
            ("Copy Image", self.copy_to_clipboard),
            ("Save Image", self.save_image)
        ]
        for text, cmd in actions:
            btn = ctk.CTkButton(export_frame, text=text, command=cmd)
            btn.pack(pady=3, fill='x')

    def create_image_preview(self):
        self.preview_label = ctk.CTkLabel(self, text="")
        self.preview_label.grid(row=0, column=1, padx=10, pady=5, sticky="n")

    def create_status_bar(self):
        self.status_var = tk.StringVar()
        status_bar = ctk.CTkLabel(self, textvariable=self.status_var, height=20, anchor='w')
        status_bar.grid(row=1, column=0, columnspan=2, sticky="we")

    # -----------------------------
    # Core Functionality
    # -----------------------------
    def update_status(self, message: str):
        self.status_var.set(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")

    def load_initial_image(self):
        if img := ClipboardManager.get_image_from_clipboard():
            self.update_image_state(img)
            self.update_status("Loaded initial image from clipboard")

    def update_image_state(self, image: Image.Image):
        self.original_image = image.copy()
        self.base_image = image.copy()
        self.processed_image = image.copy()
        self.current_scale = DEFAULT_SCALE
        self.update_ui()

    def update_ui(self):
        self.update_preview()
        self.update_dimension_entries()
        self.scale_slider.configure(from_=self.min_scale, to=self.max_scale)
        self.scale_slider.set(DEFAULT_SCALE)
        self.scale_label.configure(text=f"{DEFAULT_SCALE}%")

    def update_preview(self):
        if self.processed_image:
            preview = self.processed_image.copy()
            preview.thumbnail(THUMBNAIL_SIZE, Image.Resampling.LANCZOS)
            tk_image = ctk.CTkImage(light_image=preview, size=preview.size)
            self.preview_label.configure(image=tk_image)
            self.preview_label.image = tk_image

    def update_dimension_entries(self):
        if self.processed_image:
            self.width_var.set(str(self.processed_image.width))
            self.height_var.set(str(self.processed_image.height))

    # -----------------------------
    # Image Operations
    # -----------------------------
    def load_from_clipboard(self, event=None):
        if img := ClipboardManager.get_image_from_clipboard():
            self.update_image_state(img)
            self.update_status("Image loaded from clipboard")
        else:
            self.update_status("No image in clipboard")

    def choose_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            try:
                image = Image.open(file_path)
                self.update_image_state(image)
                self.update_status(f"Loaded: {file_path}")
                logging.info("Image loaded from computer")
            except Exception as e:
                self.update_status(f"Error: {str(e)}")
                logging.warning("Selected file is not an image")

    def convert_to_grayscale(self):
        if self.base_image:
            try:
                self.base_image = ImageProcessor.to_grayscale(self.base_image)
                self.processed_image = self.base_image.copy()
                self.update_ui()
                self.update_status("Converted to grayscale")
                logging.info("Image converted to grayscale")
            except Exception as e:
                self.update_status(f"Error: {str(e)}")
                logging.warning("Failed to convert to grayscale")

    def low_quality(self):
        if self.base_image:
            try:
                self.base_image = ImageProcessor.low_quality(self.base_image)
                self.processed_image = self.base_image.copy()
                self.update_ui()
                self.update_status("Applied low quality")
                logging.info("Applied low quality")
            except Exception as e:
                self.update_status(f"Error: {str(e)}")
                logging.warning("Failed to apply low quality")

    def revert_to_original(self):
        if self.original_image:
            self.base_image = self.original_image.copy()
            self.processed_image = self.original_image.copy()
            self.update_ui()
            self.update_status("Reverted to original image")
            logging.info("Reverted to original image")

    def on_scale_slide(self, value):
        if not self.base_image or self.is_scaling:
            return
        self.is_scaling = True
        try:
            scale = float(value)
            self.current_scale = scale
            self.processed_image = ImageProcessor.scale(
                self.base_image,
                scale / DEFAULT_SCALE
            )
            self.scale_label.configure(text=f"{int(scale)}%")
            self.update_preview()
            self.update_dimension_entries()
        except Exception as e:
            self.update_status(f"Error: {str(e)}")
            logging.warning(f"Error: {str(e)}")
        finally:
            self.is_scaling = False

    def resize_image(self):
        if not self.base_image:
            return
        try:
            width = int(self.width_var.get())
            height = int(self.height_var.get())
            self.base_image = ImageProcessor.resize(self.base_image, width, height)
            self.processed_image = self.base_image.copy()
            self.current_scale = DEFAULT_SCALE
            self.update_ui()
            self.update_status(f"Resized to {width}x{height}")
            logging.info(f"Resized to {width}x{height}")
        except Exception as e:
            self.update_status(f"Resize error: {str(e)}")
            logging.warning(f"Resize error: {str(e)}")

    def copy_to_clipboard(self, event=None):
        if self.processed_image:
            if ClipboardManager.copy_image_to_clipboard(self.processed_image):
                self.update_status("Image copied to clipboard")
            else:
                self.update_status("Failed to copy image")

    def save_image(self):
        if not self.processed_image:
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        if file_path:
            try:
                self.processed_image.save(file_path)
                self.update_status(f"Saved to: {file_path}")
            except Exception as e:
                self.update_status(f"Save error: {str(e)}")

    # -----------------------------
    # Settings Management
    # -----------------------------
    def get_app_path(self) -> str:
        if getattr(sys, 'frozen', False):
            return sys.executable
        return os.path.realpath(sys.argv[0])

    def set_startup(self, enable: bool):
        try:
            exe_path = os.path.abspath(sys.executable)
            startup_folder = os.path.join(
                os.getenv('APPDATA'),
                r'Microsoft\Windows\Start Menu\Programs\Startup'
            )
            shortcut_path = os.path.join(startup_folder, 'QuickImgEditor.lnk')

            if enable:
                try:
                    shell = Dispatch('WScript.Shell')
                    shortcut = shell.CreateShortCut(shortcut_path)
                    shortcut.Targetpath = exe_path
                    shortcut.WorkingDirectory = os.path.dirname(exe_path)
                    shortcut.IconLocation = exe_path + ",0"  # Define o ícone
                    shortcut.save()

                    logging.info("Startup shortcut added")
                except ImportError:
                    logging.warning("Used exe copy instead of proper shortcut")
            else:
                try:
                    if os.path.exists(shortcut_path):
                        os.remove(shortcut_path)
                        logging.info("Startup shortcut removed")
                    else:
                        logging.warning("Startup shortcut not found")
                except Exception as remove_error:
                    logging.error(f"Failed to remove shortcut: {str(remove_error)}")

        except Exception as e:
            logging.error(f"Startup setting failed: {str(e)}")

    def save_settings(self):
        settings = {
            'hotkey': self.hotkey,
            'min_scale': self.min_scale,
            'max_scale': self.max_scale,
            'run_at_startup': self.run_at_startup
        }

        os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f)

    def load_settings(self):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                settings = json.load(f)
                self.hotkey = settings.get('hotkey', 'ctrl+shift+b')
                self.min_scale = settings.get('min_scale', 10)
                self.max_scale = settings.get('max_scale', 200)
                self.run_at_startup = settings.get('run_at_startup', False)

                # Update startup setting
                self.set_startup(self.run_at_startup)

        except FileNotFoundError:
            pass
        except Exception as e:
            logging.error(f"Error loading settings: {str(e)}")

    # -----------------------------
    # Options Page
    # -----------------------------
    def open_options_page(self):
        if self.options_window is not None:
            self.options_window.focus_force()
            return

        self.options_window = ctk.CTkToplevel(self)
        self.options_window.title("Options")
        self.options_window.geometry("400x300")
        self.options_window.protocol("WM_DELETE_WINDOW", self.close_options_window)

        # Create main container
        container = ctk.CTkFrame(self.options_window)
        container.pack(fill='both', expand=True, padx=10, pady=10)

        # Hotkey Setting
        hotkey_frame = ctk.CTkFrame(container)
        hotkey_frame.pack(fill='x', pady=5)

        ctk.CTkLabel(hotkey_frame, text="Toggle Visibility Hotkey:").pack(side='left')
        self.hotkey_entry = ctk.CTkEntry(hotkey_frame)
        self.hotkey_entry.insert(0, self.hotkey)
        self.hotkey_entry.pack(side='right', fill='x', expand=True)

        # Scale Settings
        scale_frame = ctk.CTkFrame(container)
        scale_frame.pack(fill='x', pady=5)

        ctk.CTkLabel(scale_frame, text="Min Scale:").grid(row=0, column=0, padx=2)
        self.min_scale_entry = ctk.CTkEntry(scale_frame, width=60)
        self.min_scale_entry.insert(0, str(self.min_scale))
        self.min_scale_entry.grid(row=0, column=1, padx=2)

        ctk.CTkLabel(scale_frame, text="Max Scale:").grid(row=0, column=2, padx=2)
        self.max_scale_entry = ctk.CTkEntry(scale_frame, width=60)
        self.max_scale_entry.insert(0, str(self.max_scale))
        self.max_scale_entry.grid(row=0, column=3, padx=2)

        # Startup Setting
        self.startup_var = ctk.BooleanVar(value=self.run_at_startup)
        startup_check = ctk.CTkCheckBox(
            container,
            text="Run at Windows Startup",
            variable=self.startup_var
        )
        startup_check.pack(pady=5, anchor='w')

        # Save Button
        save_btn = ctk.CTkButton(
            container,
            text="Save Settings",
            command=self.save_options
        )
        save_btn.pack(pady=10)

    def save_options(self):
        try:
            # Validate and save hotkey
            new_hotkey = self.hotkey_entry.get().lower()
            keyboard.remove_hotkey(self.hotkey)
            keyboard.add_hotkey(new_hotkey, self.toggle_visibility)
            self.hotkey = new_hotkey

            # Validate and save scale settings
            new_min = max(1, int(self.min_scale_entry.get()))
            new_max = max(new_min + 1, int(self.max_scale_entry.get()))

            self.min_scale = new_min
            self.max_scale = new_max

            # Update scale slider in main UI
            self.scale_slider.configure(from_=self.min_scale, to=self.max_scale)

            # Save startup setting
            new_startup = self.startup_var.get()
            if new_startup != self.run_at_startup:
                self.run_at_startup = new_startup
                self.set_startup(new_startup)

            # Save all settings
            self.save_settings()
            self.close_options_window()
            self.update_status("Settings saved successfully")

        except ValueError as e:
            self.update_status(f"Invalid value: {str(e)}")
        except Exception as e:
            self.update_status(f"Error saving settings: {str(e)}")

    def close_options_window(self):
        if self.options_window is not None:
            self.options_window.destroy()
            self.options_window = None

    # -----------------------------
    # Window Management
    # -----------------------------
    def toggle_visibility(self):
        if self.state() == 'normal':
            self.withdraw()
        else:
            self.deiconify()
            self.lift()
            self.focus_force()
            self.load_from_clipboard()

    def on_close(self):
        self.withdraw()
        if self.tray.icon:
            self.tray.icon.visible = True


if __name__ == "__main__":
    app = ImageEditorApp()
    app.mainloop()