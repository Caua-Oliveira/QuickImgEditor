import os
import customtkinter as ctk
from src.ui import ImageEditorUI

if __name__ == "__main__":
    theme_path = os.path.join(os.path.dirname(__file__), "..", "resources", "theme.json")
    if os.path.exists(theme_path):
        ctk.set_default_color_theme(theme_path)
    else:
        print("Warning: theme.json not found at", theme_path)
    app = ImageEditorUI()
    app.mainloop()
