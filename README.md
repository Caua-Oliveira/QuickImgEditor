# QuickImgEditor

**QuickImgEditor** is a lightweight, fast, and user-friendly image editing tool built with Python and CustomTkinter.  
Effortlessly load, edit, and export images with essential editing features—all from a modern, minimal interface.

---

## 🚀 Features

- **Clipboard Integration**
  - Load images directly from your clipboard
  - Copy edited images back to the clipboard with a click

- **Essential Image Editing**
  - Scale images using a simple slider
  - Resize images to custom dimensions
  - Convert images to grayscale
  - Apply a "low quality" effect for quick compression

- **Modern, Intuitive UI**
  - Built with CustomTkinter for a clean, modern look
  - Real-time image preview
  - Status bar with logs and timestamps

- **System Tray Support**
  - Minimize the app to the system tray
  - Toggle visibility with a global hotkey (`Ctrl+Shift+B` by default)
  - Access options or exit using the tray icon menu

- **Customizable Startup & Settings**
  - Option to launch at Windows startup
  - Save/load preferences (hotkey, scale limits, etc.)

---

## 🖼️ Preview

![QuickImgEditor Screenshot](https://github.com/user-attachments/assets/33f7fa77-3f00-415b-a543-e9aa01df4f97)

---

## 🛠 Requirements

- **Python 3.7+**

### Python Packages

- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
- [Pillow](https://pillow.readthedocs.io/)
- [pystray](https://github.com/moses-palmer/pystray)
- [pywin32](https://github.com/mhammond/pywin32)
- [keyboard](https://github.com/boppreh/keyboard)

Install all dependencies with:
```bash
pip install customtkinter pillow pystray pywin32 keyboard
```

---

## ⚡ Quick Start

1. **Clone this repository**
   ```bash
   git clone https://github.com/Caua-Oliveira/QuickImgEditor.git
   cd QuickImgEditor
   ```
2. **Install dependencies**  
   See the requirements section above.

3. **Run the application**
   ```bash
   python main.py
   ```

---

*Questions or suggestions? Open an issue or start a discussion!*
