from io import BytesIO
import logging
import win32clipboard
from PIL import ImageGrab, Image
from typing import Optional

THUMBNAIL_SIZE = (700, 700)


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
