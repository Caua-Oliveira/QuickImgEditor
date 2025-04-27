import customtkinter as ctk
from src.ui import ImageEditorUI

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    app = ImageEditorUI()
    app.mainloop()