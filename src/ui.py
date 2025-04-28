import logging
import tkinter as tk
from tkinter import filedialog
import customtkinter as ctk
import keyboard
from datetime import datetime
from PIL import Image
from clipboard_manager import ClipboardManager
from image_processor import ImageProcessor
from settings import SettingsManager
from tray_manager import TrayManager

THUMBNAIL_SIZE = (700, 700)
DEFAULT_SCALE = 100


class ImageEditorUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("QuickImgEditor")
        self.geometry("1000x700")

        # Image state
        self.original_image = None
        self.base_image = None
        self.processed_image = None
        self.current_scale = DEFAULT_SCALE
        self.is_scaling = False

        # Load settings
        settings = SettingsManager.load()
        self.hotkey = settings.get('hotkey', 'ctrl+shift+b')
        self.min_scale = settings.get('min_scale', 10)
        self.max_scale = settings.get('max_scale', 200)
        self.run_at_startup = settings.get('run_at_startup', False)
        SettingsManager.set_startup(self.run_at_startup)

        # UI components
        self.setup_ui()
        self.setup_bindings()
        self.setup_tray()
        self.load_initial_image()

    def setup_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.create_control_panel()
        self.create_image_preview()
        self.create_status_bar()

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
            ("Lower Quality", self.lower_quality)
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
        bar = ctk.CTkLabel(self, textvariable=self.status_var, height=20, anchor='w')
        bar.grid(row=1, column=0, columnspan=2, sticky="we")

    def update_status(self, msg: str):
        self.status_var.set(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

    def load_initial_image(self):
        if img := ClipboardManager.get_image_from_clipboard():
            self._set_image(img)
            self.update_status("Loaded initial image from clipboard")
        else:
            self.update_status("No image in clipboard")

    def _set_image(self, img: Image.Image):
        self.original_image = img.copy()
        self.base_image = img.copy()
        self.processed_image = img.copy()
        self.current_scale = DEFAULT_SCALE
        self._update_ui()

    def _update_ui(self):
        self._update_preview()
        self.width_var.set(str(self.processed_image.width))
        self.height_var.set(str(self.processed_image.height))
        self.scale_slider.configure(from_=self.min_scale, to=self.max_scale)
        self.scale_slider.set(DEFAULT_SCALE)
        self.scale_label.configure(text=f"{DEFAULT_SCALE}%")

    def _update_preview(self):
        if not self.processed_image:
            return
        preview = self.processed_image.copy()
        preview.thumbnail(THUMBNAIL_SIZE, Image.Resampling.LANCZOS)
        tkimg = ctk.CTkImage(light_image=preview, size=preview.size)
        self.preview_label.configure(image=tkimg)
        self.preview_label.image = tkimg

    def load_from_clipboard(self):
        if img := ClipboardManager.get_image_from_clipboard():
            self._set_image(img)
            self.update_status("Image loaded from clipboard")
        else:
            self.update_status("No image in clipboard")


    def choose_image(self):
        path = filedialog.askopenfilename()
        if not path:
            return
        try:
            img = Image.open(path)
            self._set_image(img)
            self.update_status(f"Loaded: {path}")
        except Exception as e:
            logging.warning(f"Failed loading image: {e}")
            self.update_status("Error loading image")

    def convert_to_grayscale(self):
        if not self.base_image:
            return
        self.base_image = ImageProcessor.to_grayscale(self.base_image)
        self.processed_image = self.base_image.copy()
        self._update_ui()
        self.update_status("Converted to grayscale")

    def lower_quality(self):
        if not self.base_image:
            return
        self.base_image = ImageProcessor.lower_quality(self.base_image)
        self.processed_image = self.base_image.copy()
        self._update_ui()
        self.update_status("Applied low quality")

    def revert_to_original(self):
        if not self.original_image:
            return
        self.base_image = self.original_image.copy()
        self.processed_image = self.original_image.copy()
        self._update_ui()
        self.update_status("Reverted to original image")

    def on_scale_slide(self, val: float):
        if not self.base_image or self.is_scaling:
            return
        self.is_scaling = True
        try:
            scale = float(val)
            self.current_scale = scale
            self.processed_image = ImageProcessor.scale(self.base_image, scale / DEFAULT_SCALE)
            self.scale_label.configure(text=f"{int(scale)}%")
            self._update_preview()
            self.width_var.set(str(self.processed_image.width))
            self.height_var.set(str(self.processed_image.height))
        finally:
            self.is_scaling = False

    def resize_image(self):
        if not self.base_image:
            return
        try:
            w, h = int(self.width_var.get()), int(self.height_var.get())
            self.base_image = ImageProcessor.resize(self.base_image, w, h)
            self.processed_image = self.base_image.copy()
            self._update_ui()
            self.update_status(f"Resized to {w}x{h}")
        except Exception as e:
            logging.warning(f"Resize failed: {e}")
            self.update_status("Resize error")

    def copy_to_clipboard(self):
        if not self.processed_image:
            return
        success = ClipboardManager.copy_image_to_clipboard(self.processed_image)
        self.update_status("Image copied to clipboard" if success else "Copy failed")

    def save_image(self):
        if not self.processed_image:
            return
        path = filedialog.asksaveasfilename(defaultextension='.png', filetypes=[('PNG', '*.png'), ('All', '*.*')])
        if not path:
            return
        try:
            self.processed_image.save(path)
            self.update_status(f"Saved to: {path}")
        except Exception as e:
            logging.warning(f"Save failed: {e}")
            self.update_status("Save error")

    def open_options_page(self):
        if getattr(self, 'options_window', None) is not None:
            self.options_window.focus_force()
            return

        # Create options window
        self.options_window = ctk.CTkToplevel(self)
        self.options_window.title("Options")
        self.options_window.geometry("400x300")
        self.options_window.protocol("WM_DELETE_WINDOW", self.close_options_window)

        container = ctk.CTkFrame(self.options_window)
        container.pack(fill='both', expand=True, padx=10, pady=10)

        # Hotkey setting
        hotkey_frame = ctk.CTkFrame(container)
        hotkey_frame.pack(fill='x', pady=5)
        ctk.CTkLabel(hotkey_frame, text="Toggle Visibility Hotkey:").pack(side='left')
        self.hotkey_entry = ctk.CTkEntry(hotkey_frame)
        self.hotkey_entry.insert(0, self.hotkey)
        self.hotkey_entry.pack(side='right', fill='x', expand=True)

        # Scale settings
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

        # Startup setting
        self.startup_var = ctk.BooleanVar(value=self.run_at_startup)
        ctk.CTkCheckBox(container, text="Run at Windows Startup", variable=self.startup_var).pack(pady=5, anchor='w')

        # Save button
        ctk.CTkButton(container, text="Save Settings", command=self.save_options).pack(pady=10)

    def save_options(self):
        try:
            # Hotkey
            new_hotkey = self.hotkey_entry.get().lower()
            keyboard.remove_hotkey(self.hotkey)
            keyboard.add_hotkey(new_hotkey, self.toggle_visibility)
            self.hotkey = new_hotkey

            # Scale range
            new_min = max(1, int(self.min_scale_entry.get()))
            new_max = max(new_min + 1, int(self.max_scale_entry.get()))
            self.min_scale, self.max_scale = new_min, new_max
            self.scale_slider.configure(from_=new_min, to=new_max)

            # Startup
            if self.startup_var.get() != self.run_at_startup:
                self.run_at_startup = self.startup_var.get()
                SettingsManager.set_startup(self.run_at_startup)

            # Persist
            SettingsManager.save({
                'hotkey': self.hotkey,
                'min_scale': self.min_scale,
                'max_scale': self.max_scale,
                'run_at_startup': self.run_at_startup
            })

            self.close_options_window()
            self.update_status("Settings saved successfully")
        except Exception as e:
            logging.warning(f"Error saving settings: {e}")
            self.update_status(f"Error saving settings: {e}")

    def close_options_window(self):
        if getattr(self, 'options_window', None):
            self.options_window.destroy()
            self.options_window = None

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
