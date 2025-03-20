# QuickImgEditor

QuickImgEditor is a lightweight image editing application built with Python and CustomTkinter. It provides a quick and easy interface to load, edit, and export images with features like scaling, resizing, grayscale conversion, and a low-quality effect. The app also integrates with the Windows clipboard and system tray for a streamlined workflow.

## Features

- **Clipboard Integration:**  
  - Load images directly from the clipboard.
  - Copy edited images back to the clipboard.
  
- **Basic Image Processing:**  
  - Scale images with a slider control.
  - Resize images by specifying custom dimensions.
  - Convert images to grayscale.
  - Apply a "low quality" effect.
  
- **User-Friendly Interface:**  
  - Built with CustomTkinter for a modern UI.
  - Real-time preview of image changes.
  - Status bar displays operation logs and timestamps.
  
- **System Tray Support:**  
  - Minimize the app to the system tray.
  - Toggle visibility using a custom hotkey (default: `ctrl+shift+b`).
  - Access options and exit the app via the tray icon menu.
  
- **Startup Configuration:**  
  - Option to run the application at Windows startup.
  - Save and load custom settings including hotkey and scale limits.

## Prerequisites

Ensure you have Python 3.7 or higher installed. The following Python packages are required:

- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
- [Pillow](https://pillow.readthedocs.io/)
- [pystray](https://github.com/moses-palmer/pystray)
- [pywin32](https://github.com/mhammond/pywin32)
- [keyboard](https://github.com/boppreh/keyboard)


